from django.db import models
from common.models.base import AuditModel

class ConfigItem(AuditModel):
    key = models.CharField("配置键", max_length=100, unique=True)
    value = models.TextField("配置值", blank=True, default="")
    category = models.CharField("配置分类", max_length=100, blank=True, default="")
    is_secret = models.BooleanField("是否敏感", default=False)
    remark = models.CharField("备注", max_length=255, blank=True, default="")
