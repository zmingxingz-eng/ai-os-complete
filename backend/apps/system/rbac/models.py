from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from common.models.base import AuditModel
from apps.system.menu.models import Menu
from apps.system.organization.models import Organization

User = get_user_model()

class GroupMenu(AuditModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_menus", verbose_name="角色")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_roles", verbose_name="菜单")

    class Meta:
        unique_together = ("group", "menu")
        default_permissions = ()

class GroupDataScope(AuditModel):
    SCOPE_CHOICES = (
        ("self", "仅本人"),
        ("org", "本组织"),
        ("org_and_children", "本组织及下级"),
        ("custom", "自定义"),
        ("all", "全部数据"),
    )
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="data_scope", verbose_name="角色")
    scope_type = models.CharField("数据范围", max_length=30, choices=SCOPE_CHOICES, default="self")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="指定组织")
    organizations = models.ManyToManyField(Organization, blank=True, related_name="custom_data_scopes", verbose_name="自定义组织")

    class Meta:
        default_permissions = ()
