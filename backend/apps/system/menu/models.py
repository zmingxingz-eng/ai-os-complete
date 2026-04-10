from django.contrib.contenttypes.models import ContentType
from django.db import models
from common.models.base import AuditModel

class Menu(AuditModel):
    TYPE_CHOICES = (
        ("directory", "目录"),
        ("menu", "菜单"),
    )
    name = models.CharField("菜单名称", max_length=100)
    code = models.CharField("菜单编码", max_length=100, unique=True, null=True, blank=True)
    path = models.CharField("路由地址", max_length=255, blank=True, default="")
    component = models.CharField("组件路径", max_length=255, blank=True, default="")
    menu_type = models.CharField("菜单类型", max_length=20, choices=TYPE_CHOICES, default="menu")
    icon = models.CharField("图标", max_length=100, blank=True, default="")
    visible = models.BooleanField("是否显示", default=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children", verbose_name="上级菜单")
    sort = models.PositiveIntegerField("排序", default=0)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL, related_name="system_menus", verbose_name="业务模型")

    class Meta:
        ordering = ["sort", "id"]
