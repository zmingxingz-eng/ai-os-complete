from django.contrib.auth.models import Permission
from django.db import models
from common.models.base import AuditModel
from apps.system.menu.models import Menu

class MenuPermission(AuditModel):
    TYPE_CHOICES = (
        ("api", "API"),
        ("button", "按钮"),
    )
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_permissions", verbose_name="菜单")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="menu_bindings", verbose_name="权限")
    perm_type = models.CharField("权限类型", max_length=20, choices=TYPE_CHOICES, default="button")
    description = models.CharField("描述", max_length=200, blank=True, default="")
    sort = models.PositiveIntegerField("排序", default=0)

    class Meta:
        unique_together = ("menu", "permission")
        default_permissions = ()
