from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Права доступа, если пользователь автор контента."""

    def has_permission(self, request, view) -> bool:
        del view
        user = request.user
        return (
            user.is_authenticated
            and user.is_user
            or request.method in SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj) -> bool:
        del view
        user = request.user
        return obj.author == user or request.method in SAFE_METHODS


class IsRoleAdmin(BasePermission):
    """Права доступа, если пользователь администратор."""

    def has_permission(self, request, view) -> bool:
        del view
        user = request.user
        return user.is_authenticated and (user.is_admin or user.is_superuser)

    def has_object_permission(self, request, view, obj) -> bool:
        del view
        del obj
        user = request.user
        return user.is_authenticated and (user.is_admin or user.is_superuser)


class IsRoleModerator(BasePermission):
    """Права доступа, если пользователь модератор."""

    def has_permission(self, request, view) -> bool:
        del view
        user = request.user
        return user.is_authenticated and user.is_moderator

    def has_object_permission(self, request, view, obj) -> bool:
        del view
        del obj
        user = request.user
        return user.is_authenticated and user.is_moderator


class ReadOnly(BasePermission):
    """Права доступа только чтение."""

    def has_permission(self, request, view) -> bool:
        del view
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj) -> bool:
        del view
        del obj
        return request.method in SAFE_METHODS


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    """
    права доступа если пользователь автор, модератор или админ
    для остальных только чтение
    """

    def has_permission(self, request, view) -> bool:
        del view
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj) -> bool:
        del view
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
