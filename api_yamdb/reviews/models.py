from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django.conf import settings


class User(AbstractUser):
    """Класс пользователя переопределенный."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Админ'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_superuser:
            self.role = self.ADMIN

    username = models.SlugField(
        db_index=True,
        max_length=settings.MAX_LENGTH_USERNAME,
        verbose_name='Имя пользователя',
        unique=True,
    )
    first_name = models.CharField(
        blank=True,
        max_length=settings.MAX_LENGTH_USERNAME,
        verbose_name='имя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=settings.MAX_LENGTH_USERNAME,
        verbose_name='фамилия',
    )
    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта',
        unique=True,
    )
    bio = models.TextField(
        blank=True,
        max_length=settings.MAX_LENGTH,
        verbose_name='Биография',
    )
    role = models.CharField(
        default='user',
        choices=ROLES,
        max_length=settings.MAX_LENGTH_CORE,
        verbose_name='Роль',
    )
    confirmation_code = models.CharField(
        blank=True,
        max_length=settings.MAX_LENGTH_CORE,
        verbose_name='Код подтверждения',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user',
            ),
        ]
        ordering = ('role',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username[:settings.DEFAULT_SHOWING_SYMBOLS]

    @property
    def is_admin(self) -> bool:
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self) -> bool:
        return self.role == self.MODERATOR

    @property
    def is_user(self) -> bool:
        return self.role == self.USER


class Category(models.Model):
    """Описывает модель для хранения групп категорий."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.MAX_LENGTH_SLUG,
        verbose_name='Слаг',
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name[:settings.DEFAULT_SHOWING_SYMBOLS]


class Genre(models.Model):
    """Описывает модель для хранения групп жанров."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.MAX_LENGTH_SLUG,
        verbose_name='Слаг',
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name[:settings.DEFAULT_SHOWING_SYMBOLS]


class Title(models.Model):
    """Описывает модель для хранения групп произведений."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH,
        verbose_name='Название',
    )
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        db_index=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        through='TitleGenre',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.DEFAULT_SHOWING_SYMBOLS]


class TitleGenre(models.Model):
    """Описывает связующую модель для привязки жанров к произведениям."""

    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'title_genres'


class Review(models.Model):
    text = models.TextField(verbose_name='текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение',
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(settings.MIN_SCORE),
            MaxValueValidator(settings.MAX_SCORE),
        ],
        null=False,
        verbose_name='оценка',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        unique_together = ('title', 'author')

    def __str__(self):
        return self.text[:settings.DEFAULT_SHOWING_SYMBOLS]


class Comment(models.Model):
    text = models.TextField(verbose_name='текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:settings.DEFAULT_SHOWING_SYMBOLS]
