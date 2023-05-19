from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import ADMINS_EMAIL
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import AdminViewMixin, ModeratorViewMixin
from .permissions import IsAdminOrSuperUser
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer,
                          GenreSerializer, TitleGetSerializer,
                          ReviewSerializer, SignupSerializer,
                          TitlePostSerializer, TokenSerializer,
                          UserPatchMeSerializer, UserSerializer)
from .utils import get_response_message, send_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperUser,)
    filter_backends = (
        DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter
    )
    lookup_field = 'username'
    search_fields = ('username',)
    ordering = ('username',)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserPatchMeSerializer,
    )
    def my_profile(self, request):
        user = self.request.user
        if self.request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ViewSet):
    """
    Extends ViewSet class by defining functions for
    user registration, refreshing confirmation code and generating auth token.
    Confirmation code is sent to email.
    """

    permission_classes = (AllowAny,)

    @property
    def validated_user_data(self):
        if self.action == 'refresh_confirmation_code':
            serializer = ConfirmationCodeSerializer(data=self.request.data)
        else:
            serializer = SignupSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_user_data = serializer.validated_data
        return validated_user_data

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        username = self.validated_user_data['username']
        email = self.validated_user_data['email']
        user = User.objects.create(email=email, username=username)
        send_confirmation_code(user, ADMINS_EMAIL, email)
        return Response(
            get_response_message().get('successful_registration'),
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=False, url_path='confirmation_code')
    def refresh_confirmation_code(self, request):
        username = self.validated_user_data['username']
        email = self.validated_user_data['email']
        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return Response(
                get_response_message().get('user_not_found'),
                status=status.HTTP_404_NOT_FOUND
            )
        send_confirmation_code(user, ADMINS_EMAIL, email)
        return Response(
            get_response_message().get('confirmation_code_sent'),
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=False, url_path='token')
    def get_auth_token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                get_response_message(username).get('invalid_username'),
                status=status.HTTP_404_NOT_FOUND
            )
        if not default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            return Response(
                get_response_message().get('invalid_confirmation_code'),
                status=status.HTTP_400_BAD_REQUEST
            )
        token = str(RefreshToken.for_user(user).access_token)
        return Response({"token": token}, status=status.HTTP_200_OK)


class CategoryViewSet(
        mixins.CreateModelMixin, mixins.DestroyModelMixin,
        mixins.ListModelMixin, AdminViewMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    search_fields = ('name', 'slug')
    ordering = ('name',)


class GenreViewSet(CategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet, AdminViewMixin):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).select_related()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_class = TitleFilter
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleGetSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet, ModeratorViewMixin):
    serializer_class = ReviewSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-pub_date')

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all().select_related('author')

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ReviewViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(title.reviews, id=review_id)
        return review.comments.all().select_related('author')

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)
