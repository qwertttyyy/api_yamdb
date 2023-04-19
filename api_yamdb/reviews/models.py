from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models


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

    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Имя пользователя содержит недопустимый символ',
            ),
        ],
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


class Genres(models.Model):
    """Описывает модель для хранения групп жанров."""

    # потом перенести все числа в константы
    name = models.CharField(max_length=265)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name[:15]


class Categories(models.Model):
    """Описывает модель для хранения групп категорий."""

    name = models.CharField(max_length=265)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    """Описывает модель для хранения групп произведений."""

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ForeignKey(
        Genres,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
    )
    category = models.ForeignKey(
        Categories,
        related_name='titles',
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return self.name[:15]


class Review(models.Model):
    text = models.TextField(null=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,  # моделька для titles еще не написана, доработать как увижу
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=False,
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(null=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    reviews = models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.text[:15]
