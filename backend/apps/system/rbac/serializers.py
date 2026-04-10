from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from .models import GroupMenu, GroupDataScope
from apps.system.organization.models import Organization

User = get_user_model()
UserRoleModel = User.groups.through
RolePermissionModel = Group.permissions.through

class UserRoleSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(source="group", queryset=Group.objects.all())
    username = serializers.CharField(source="user.username", read_only=True)
    role_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = UserRoleModel
        fields = ["id", "user", "role", "username", "role_name"]

class RolePermissionSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(source="group", queryset=Group.objects.all())
    role_name = serializers.CharField(source="group.name", read_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)
    permission_code = serializers.SerializerMethodField()

    class Meta:
        model = RolePermissionModel
        fields = ["id", "role", "permission", "role_name", "permission_name", "permission_code"]

    def get_permission_code(self, obj):
        return f"{obj.permission.content_type.app_label}.{obj.permission.codename}"

class RoleMenuSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(source="group", queryset=Group.objects.all())
    role_name = serializers.CharField(source="group.name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    menu_path = serializers.CharField(source="menu.path", read_only=True)

    class Meta:
        model = GroupMenu
        fields = ["id", "role", "menu", "role_name", "menu_name", "menu_path"]

class RoleDataScopeSerializer(serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(source="group", queryset=Group.objects.all())
    role_name = serializers.CharField(source="group.name", read_only=True)
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    organizations = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all(), many=True, required=False)
    organization_names = serializers.SerializerMethodField()

    class Meta:
        model = GroupDataScope
        fields = ["id", "role", "scope_type", "organization", "organizations", "role_name", "organization_name", "organization_names"]

    def get_organization_names(self, obj):
        return list(obj.organizations.values_list("name", flat=True))
