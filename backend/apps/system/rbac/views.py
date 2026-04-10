from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import viewsets
from .models import GroupMenu, GroupDataScope
from .serializers import UserRoleSerializer, RolePermissionSerializer, RoleMenuSerializer, RoleDataScopeSerializer

User = get_user_model()
UserRoleModel = User.groups.through
RolePermissionModel = Group.permissions.through

class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRoleModel.objects.select_related("user", "group").all().order_by("id")
    serializer_class = UserRoleSerializer

class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset = RolePermissionModel.objects.select_related("group", "permission", "permission__content_type").all().order_by("id")
    serializer_class = RolePermissionSerializer

class RoleMenuViewSet(viewsets.ModelViewSet):
    queryset = GroupMenu.objects.select_related("group", "menu").all().order_by("id")
    serializer_class = RoleMenuSerializer

class RoleDataScopeViewSet(viewsets.ModelViewSet):
    queryset = GroupDataScope.objects.select_related("group", "organization").prefetch_related("organizations").all().order_by("id")
    serializer_class = RoleDataScopeSerializer
