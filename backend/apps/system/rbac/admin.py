from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import GroupMenu, GroupDataScope

User = get_user_model()
UserRoleModel = User.groups.through
RolePermissionModel = Group.permissions.through

@admin.register(UserRoleModel)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "group")
    search_fields = ("user__username", "group__name")

@admin.register(RolePermissionModel)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "permission")
    search_fields = ("group__name", "permission__name")

@admin.register(GroupMenu)
class RoleMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "menu", "is_active", "created_at")
    search_fields = ("group__name", "menu__name", "menu__path")
    list_filter = ("is_active",)

@admin.register(GroupDataScope)
class RoleDataScopeAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "scope_type", "organization", "is_active", "created_at")
    search_fields = ("group__name", "organization__name")
    list_filter = ("scope_type", "is_active")
