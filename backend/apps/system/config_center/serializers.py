from rest_framework import serializers
from .models import ConfigItem

class ConfigItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigItem
        fields = "__all__"
