from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.system.organization.models import Organization


class User(AbstractUser):
    full_name = models.CharField("姓名", max_length=100, blank=True, default="")
    mobile = models.CharField("手机号", max_length=20, blank=True, default="")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name="users", verbose_name="所属组织")
    position_name = models.CharField("岗位名称", max_length=100, blank=True, default="")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.full_name or self.username
