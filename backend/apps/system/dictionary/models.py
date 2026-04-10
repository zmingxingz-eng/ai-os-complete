from django.db import models
from common.models.base import AuditModel

class DictionaryType(AuditModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)

class DictionaryItem(AuditModel):
    dict_type = models.ForeignKey(DictionaryType, on_delete=models.CASCADE, related_name="items")
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    sort = models.PositiveIntegerField(default=0)
