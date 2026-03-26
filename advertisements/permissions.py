from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его владельцу или админу.
    """
    
    def has_object_permission(self, request, view, obj):
        # Администратор может все
        if request.user.is_staff:
            return True
        
        # Для остальных - проверяем, что пользователь - создатель объявления
        return obj.creator == request.user


class IsOwnerOrAdminForDraft(permissions.BasePermission):
    """
    Разрешение для черновиков: видят только владелец и админ.
    """
    
    def has_object_permission(self, request, view, obj):
        # Если объявление в черновике
        if obj.status == 'DRAFT':
            # Только автор или админ могут видеть
            return request.user.is_staff or obj.creator == request.user
        
        # Для остальных статусов - доступно всем
        return True
