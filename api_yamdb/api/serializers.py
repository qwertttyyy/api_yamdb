from datetime import datetime

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)

    class Meta:
        model = Genre
        lookup_field = 'slug'
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)

    class Meta:
        model = Category
        lookup_field = 'slug'
        fields = ('name', 'slug')


class ReadTitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    name = serializers.CharField(max_length=256)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            '__all__'  # ('name', 'year', 'description', 'genre', 'category',)
        )
        read_only_fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'rating',
            'category',
        )


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    name = serializers.CharField(max_length=256)
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects,
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects,
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate(self, data):
        if not self.partial:
            genres = data.get('genre')
            for genre in genres:
                if genre not in Genre.objects.all():
                    raise serializers.ValidationError(
                        'Такого жанра нет в списке',
                    )

            if data.get('category') not in Category.objects.all():
                raise serializers.ValidationError(
                    'Такой категории нет в списке',
                )

            if data.get('year') > datetime.today().year:
                raise serializers.ValidationError(
                    'Это произведение ещё не вышло',
                )
            return data
        return data


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Придумай другое имя. Кто себя называет me?',
            )
        elif User.objects.filter(username=value):
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.',
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.',
            )
        return value


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена JWT."""

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
        extra_kwargs = {
            'username': {
                'validators': [],
            },
        }

    def validate(self, data):
        username = data['username']
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError('Неверный код подтверждения.')
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    title = serializers.SlugRelatedField(slug_field='name', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    def validate_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value
    
    def validate_title(self, value):
        try:
            Title.objects.get(name=value)
        except Title.DoesNotExist:
            raise serializers.ValidationError('Произведение не найдено.')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = title_id = self.context.get('view').kwargs.get('title_id')
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title_id, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field='text', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = '__all__'
        model = Comment
