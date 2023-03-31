from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """Разрешает просмотр профилей авторов
    только авторизованным пользователям"""
    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return request.user.is_authenticated

        return True


class RecipePermission(permissions.BasePermission):
    """Разрешает создание рецептов только авторизованным пользователям,
    просмотр рецептов доступен для всех,
    обновление и удаление доступно автору рецепта или администратору"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author
                or request.user.is_staff
                or request.user.is_superuser)
