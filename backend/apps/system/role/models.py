from django.contrib.auth.models import Group
from django.db import models
from common.models.base import AuditModel

class GroupProfile(AuditModel):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="profile", verbose_name="角色")
    code = models.CharField("角色编码", max_length=50, unique=True)
    description = models.TextField("角色描述", blank=True, default="")

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        default_permissions = ()
