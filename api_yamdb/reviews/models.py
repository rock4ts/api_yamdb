from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USERS_ROLES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(
        unique=True, max_length=150, verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        unique=True, verbose_name='Электронная почта'
    )
    first_name = models.CharField(
        max_length=150, null=True, blank=True,
        default='', verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150, null=True, blank=True,
        default='', verbose_name='Фамилия'
    )
    bio = models.TextField(
        max_length=500, null=True, blank=True,
        default='', verbose_name='О себе'
    )
    role = models.CharField(
        max_length=50, choices=USERS_ROLES, default=USER, verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser


class Category(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='Слаг категории'
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=256, verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name='Слаг жанра'
    )

    class Meta:
        verbose_name = 'Genre',
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=100, verbose_name='Название произведения'
    )
    year = models.IntegerField(
        verbose_name='Год публикации'
    )
    description = models.TextField(
        null=True, verbose_name='Описание произведения'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitle',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Title',
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='genres', verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE,
        related_name='titles', verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Title genres'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique title-genre constraint',
            ),
        ]


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique author-review constaint')
        ]

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Сomments'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
