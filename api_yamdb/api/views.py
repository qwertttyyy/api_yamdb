from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, request, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import TitleFilter
from api.permissions import (
    IsAdminModeratorAuthorOrReadOnly,
    IsRoleAdmin,
    ReadOnly,
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReadTitleSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)
from reviews.models import Category, Genre, Review, Title, User


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки произведений."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).order_by(
        'id',
    )
    serializer_class = TitleSerializer
    permission_classes = [IsRoleAdmin | ReadOnly]
    filterset_class = TitleFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadTitleSerializer
        return TitleSerializer


class GetCreateDestroyViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Создание базового вьюсета, который обрабатывает запросы на
    получение списка всех объектов, создание и удаление."""

    pass


class GenreViewSet(GetCreateDestroyViewSet):
    """Вьюсет для обработки жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsRoleAdmin | ReadOnly]
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(GetCreateDestroyViewSet):
    """Вьюсет для обработки категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsRoleAdmin | ReadOnly]
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'slug'
    search_fields = ('name',)


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
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)


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
                'message': 'Ты забыл свой токен? '
                'Код подтверждения отправлен повторно.',
            },
            status=status.HTTP_200_OK,
        )
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
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    access = AccessToken.for_user(user)
    return Response(f'token: {access}', status=status.HTTP_200_OK)


def send_confirmation_code(user):
    """Генерирует и отправляет код авторизации."""
    generated_code = default_token_generator.make_token(user)
    user.confirmation_code = (
        generated_code  # присваиваем новое значение confirmation_code
    )
    user.save()

    subject = 'YaMDb. Код авторизации.'
    message = f'Привет, {user}! Твой код для авторизации «{generated_code}»'
    from_email = settings.FROM_EMAIL
    to_email = [user.email]
    return send_mail(subject, message, from_email, to_email)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id'),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(author=self.request.user, review=review)
