from django.conf import settings
from django.db import models

class TimestampedModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True

class AuditModel(TimestampedModel):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_creator",
        verbose_name="创建人",
    )
    updater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_updater",
        verbose_name="更新人",
    )
    is_active = models.BooleanField("启用状态", default=True)

    class Meta:
        abstract = True
