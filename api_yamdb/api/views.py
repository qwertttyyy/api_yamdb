from api.permissions import IsRoleAdmin
from api.serializers import TokenSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets,request
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import User


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

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me_page(self, request):
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
