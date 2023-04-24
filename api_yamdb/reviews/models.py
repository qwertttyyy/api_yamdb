from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.settings import DEFAULT_SHOWING_SYMBOLS, MAX_LENGTH_NAME, \
    MAX_LENGTH_SLUG


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
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='имя',
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='фамилия',
        blank=True,
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=254,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        max_length=250,
    )
    role = models.CharField(
        verbose_name='Роль',
        default='user',
        choices=ROLES,
        max_length=16,
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        blank=True,
        max_length=50,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('role',)
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user',
            ),
        ]

    def __str__(self) -> str:
        return self.username[:15]

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

    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            verbose_name='Название')
    slug = models.SlugField(unique=True, max_length=MAX_LENGTH_SLUG,
                            verbose_name='Слаг')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name[:DEFAULT_SHOWING_SYMBOLS]


class Genre(models.Model):
    """Описывает модель для хранения групп жанров."""

    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            verbose_name='Название')
    slug = models.SlugField(unique=True, max_length=MAX_LENGTH_SLUG,
                            verbose_name='Слаг')

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name[:DEFAULT_SHOWING_SYMBOLS]


class Title(models.Model):
    """Описывает модель для хранения групп произведений."""

    name = models.CharField(max_length=MAX_LENGTH_NAME,
                            verbose_name='Название')
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска', db_index=True,
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        through='TitleGenre',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:DEFAULT_SHOWING_SYMBOLS]


class TitleGenre(models.Model):
    """Описывает связующую модель для привязки жанров к произведениям."""

    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'title_genres'


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=False,
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        unique_together = ('title', 'author')

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:15]
