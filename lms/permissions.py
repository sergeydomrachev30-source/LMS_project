from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором (состоит ли в группе 'moderators')."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.groups.filter(name="moderators").exists()
        return False


class IsNotModerator(permissions.BasePermission):
    """Блокирует доступ, если пользователь является модератором."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return not request.user.groups.filter(name="moderators").exists()
        return False


class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
