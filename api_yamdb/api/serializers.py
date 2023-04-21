from datetime import datetime
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import User, Review, Comment, Title, Genre, Category


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

    class Meta:
        model = Title
        fields = '__all__'  # ('name', 'year', 'description', 'genre', 'category',)
        read_only_fields = (
            'id', 'name', 'year', 'description', 'genre', 'rating', 'category',
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
        fields = '__all__'  # ('name', 'year', 'description', 'genre', 'category',)

    def validate(self, data):

        genres = data.get('genre')
        for genre in genres:
            if genre not in Genre.objects.all():
                raise serializers.ValidationError('Такого жанра нет в списке')

        if data.get('category') not in Category.objects.all():
            raise serializers.ValidationError('Такой категории нет в списке')

        if data.get('year') > datetime.today().year:
            raise serializers.ValidationError('Это произведение ещё не вышло')

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
            print(user.confirmation_code, '!=', data['confirmation_code'])
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

    def validate_username(self, username):
        if username in 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено',
            )
        return username


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    title = serializers.SlugRelatedField(slug_field='name', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    def validate_score(self, value):
        if 0 > value > 10:
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field='text', read_only=True)
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
