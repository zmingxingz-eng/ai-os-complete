from django.db import models
from common.models.base import AuditModel

class Notice(AuditModel):
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title
