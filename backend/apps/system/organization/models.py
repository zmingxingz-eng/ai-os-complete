from django.db import models
from common.models.base import AuditModel

class Organization(AuditModel):
    name = models.CharField("组织名称", max_length=100)
    code = models.CharField("组织编码", max_length=50, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="children", verbose_name="上级组织")
    sort = models.PositiveIntegerField("排序", default=0)

    class Meta:
        verbose_name = "组织机构"
        verbose_name_plural = verbose_name
        ordering = ["sort", "id"]

    def __str__(self):
        return self.name
