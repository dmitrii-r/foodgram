from rest_framework import permissions


class IsAdminOwnerOrReadOnly(permissions.BasePermission):
    """
    Доступ разрешён всем при безопасном методе,
    аутентифицированные пользователи могут использовать метод POST,
    остальные методы могут использовать автор или администратор.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or obj.author == request.user)
