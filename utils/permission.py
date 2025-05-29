from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class IsSuperAdminUser(BasePermission):
    """
    自定义权限类，检查用户是否是超级管理员
    """
    def has_permission(self, request, view):
        # 确保用户已认证且是超级管理员
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)