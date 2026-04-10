from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import GroupMenu, GroupDataScope

User = get_user_model()
UserRoleModel = User.groups.through
RolePermissionModel = Group.permissions.through

class RbacService:
    @staticmethod
    def list_user_roles():
        return UserRoleModel.objects.select_related("user", "group").all()

    @staticmethod
    def list_role_permissions():
        return RolePermissionModel.objects.select_related("group", "permission").all()

    @staticmethod
    def list_role_menus():
        return GroupMenu.objects.select_related("group", "menu").all()

    @staticmethod
    def list_role_data_scopes():
        return GroupDataScope.objects.select_related("group", "organization").all()
