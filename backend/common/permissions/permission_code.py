from rest_framework.permissions import BasePermission
from apps.system.rbac.models import UserRole, RolePermission

class PermissionCodePermission(BasePermission):
    required_permission = ""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        required = getattr(view, "required_permission", "") or self.required_permission
        if not required:
            return True
        role_ids = UserRole.objects.filter(user=request.user, is_active=True).values_list("role_id", flat=True)
        perm_codes = RolePermission.objects.filter(
            role_id__in=role_ids,
            is_active=True,
            permission__is_active=True
        ).values_list("permission__code", flat=True)
        return required in set(perm_codes)
