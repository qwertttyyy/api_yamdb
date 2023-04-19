from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import User


class SingUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    pass


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения токена JWT."""

    class Meta:
        model = User
        fields = ('username', ) # 'confirmation_code'
        extra_kwargs = {'username': {'validators': []}}

    def validate(self, data):
        username = data['username']
        user = get_object_or_404(User, username=username)
        # будет в ближайшей фиче проверка с конфирм кодом, пока так токен можно получить
        # if user.confirmation_code != data['confirmation_code']:
            # raise serializers.ValidationError('Неверный код подтверждения.')

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

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
