from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = "__all__"
