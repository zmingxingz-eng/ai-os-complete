from django.contrib.auth import get_user_model
from django.db import models
from common.models.base import TimestampedModel

User = get_user_model()

class AuditLog(TimestampedModel):
    action = models.CharField("操作类型", max_length=50)
    target = models.CharField("目标对象", max_length=100)
    content = models.TextField("操作内容", blank=True, default="")
    operator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="操作人")
