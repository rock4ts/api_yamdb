from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User
from .validators import (allowed_username_validator,
                         score_validator, year_validator)


class SignupSerializer(serializers.ModelSerializer):
    """
    User registration serializer.
    """
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Введённый email используется другим пользователем."
            )
        ]
    )
    username = serializers.CharField(
        validators=[
            allowed_username_validator,
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    'Имя пользователя должно состоять из букв, '
                     'цифр и символов @/./+/-/_'
                    )
                ),
            UniqueValidator(
                queryset=User.objects.all(),
                message="Введённый username используется другим пользователем."
            )
        ]
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class ConfirmationCodeSerializer(serializers.Serializer):
    """
    Confirmation code request serializer.
    """
    username = serializers.CharField()
    email = serializers.EmailField()


class TokenSerializer(serializers.Serializer):
    """
    Token request serializer.
    """
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(SignupSerializer):
    """
    User data serializer.
    """
    class Meta(SignupSerializer.Meta):
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )


class UserPatchMeSerializer(UserSerializer):
    """
    User self data serializer.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )


class TitlePostSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=False
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=False
    )
    year = serializers.IntegerField(validators=[year_validator])

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)
        validators = [
            UniqueTogetherValidator(
                queryset=Title.objects.all(),
                fields=['name', 'category'],
                message='В указанной категории уже существует '
                        'произведение с аналогичным названием.'
            )
        ]


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    score = serializers.IntegerField(validators=[score_validator])

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return super().validate(data)
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        is_second_review = (
            Review.objects.filter(author=author, title=title_id).exists()
        )
        if is_second_review:
            raise serializers.ValidationError(
                'Вы уже написали отзыв к этому произведению.'
            )
        return super().validate(data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
