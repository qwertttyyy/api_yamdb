from django.db import models


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


class Titles(models.Model):
    """Описывает модель для хранения групп произведений."""

    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField()
    genre = models.ForeignKey(
        Genres, related_name='titles', on_delete=models.SET_NULL, null=True
    )
    category = models.ForeignKey(
        Categories, related_name='titles', on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.name[:15]
