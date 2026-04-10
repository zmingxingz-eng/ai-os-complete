from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.tokens import RefreshToken
from apps.system.rbac.models import GroupMenu, GroupDataScope
from apps.system.menu.models import Menu
RolePermissionModel = Group.permissions.through

class AuthService:
    @staticmethod
    def login_user(username: str, password: str):
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            return user
        return None

    @staticmethod
    def build_token_payload(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def _group_ids(user):
        group_qs = user.groups.all()
        if hasattr(Group, "profile"):
            group_qs = group_qs.filter(profile__is_active=True)
        return group_qs.values_list("id", flat=True)

    @staticmethod
    def get_user_menus(user):
        group_ids = AuthService._group_ids(user)
        menu_ids = GroupMenu.objects.filter(group_id__in=group_ids, is_active=True).values_list("menu_id", flat=True)
        return Menu.objects.filter(id__in=menu_ids, is_active=True).select_related("parent").order_by("sort", "id").distinct()

    @staticmethod
    def get_user_permissions(user):
        group_ids = AuthService._group_ids(user)
        perm_ids = RolePermissionModel.objects.filter(group_id__in=group_ids).values_list("permission_id", flat=True)
        return Permission.objects.filter(id__in=perm_ids).select_related("content_type").order_by("content_type__app_label", "codename").distinct()

    @staticmethod
    def get_user_data_scopes(user):
        group_ids = AuthService._group_ids(user)
        return GroupDataScope.objects.filter(group_id__in=group_ids, is_active=True).select_related("group", "organization").prefetch_related("organizations").distinct()

    @staticmethod
    def build_session_info(user):
        return {
            "username": user.username,
            "full_name": getattr(user, "full_name", "") or user.username,
            "user_id": user.id,
            "organization_name": getattr(getattr(user, "organization", None), "name", ""),
            "position_name": getattr(user, "position_name", ""),
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
        }
