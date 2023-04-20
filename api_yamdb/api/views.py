from rest_framework import viewsets

from api.filters import TitlesFilter
from api.permissions import IsAdminOrReadOnly
from api.serializers import TitleSerializer
from reviews.models import Titles

from random import randint

from api.permissions import IsRoleAdmin, IsAdminModeratorAuthorOrReadOnly
from api.serializers import (SignUpSerializer, TokenSerializer, UserSerializer,
                             TokenSerializer, UserSerializer, ReviewSerializer,
                             CommentSerializer,
                             )
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, request

from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import User, Title, Review


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_class = TitlesFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет работает с эндпойнтом users/.
    Предоставляет администратору доступ ко всем видам запросов.
    """

    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsRoleAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me_page(self, request: request.Request) -> Response:
        """
        Доступ к эндпойнту users/me/.
        Информация о пользователе и возмодность редактирования
            своей информации.
        """
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
            )
            if serializer.is_valid():
                serializer.save(role=request.user.role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


@api_view(['POST'])
@permission_classes(
    [
        AllowAny,
    ],
)
def signup(request):
    """
    Регистрация пользователя и запрос на отправку кода авторизации на почту.
    """
    serializer = SignUpSerializer(data=request.data)
    email = request.data.get('email')
    username = request.data.get('username')
    user = User.objects.filter(email=email, username=username)

    if user.exists():
        user = user.get(email=email)
        send_confirmation_code(user)
        return Response(
            {
                'message': 'Почта занята! '
                           'Код подтверждения отправлен повторно.',
            },
            status=status.HTTP_200_OK,
        )

    else:
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        user, _ = User.objects.get_or_create(
            username=username,
            email=email,
        )
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes(
    [
        AllowAny,
    ],
)
def get_token(request: request.Request) -> Response:
    """
    Возвращает пользователю токен для авторизации.
    """
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        access = AccessToken.for_user(user)
        return Response(f'token: {access}', status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_confirmation_code(user):
    """Генерирует и отправляет код авторизации."""
    generated_code = randint(1000000, 9999999)  # создаем код 7-значный
    user.confirmation_code = (
        generated_code,  # присваиваем новое значение confirmation_code
    )
    user.save()

    subject = 'YaMDb. Код авторизации.'
    message = f'Привет, {user}! Твой код для авторизации «{generated_code}»'
    from_email = 'YaMDb@yamdb.com'
    to_email = [user.email]
    return send_mail(subject, message, from_email, to_email)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
