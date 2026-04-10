from rest_framework import viewsets
from .models import ConfigItem
from .serializers import ConfigItemSerializer

class ConfigItemViewSet(viewsets.ModelViewSet):
    queryset = ConfigItem.objects.all().order_by("id")
    serializer_class = ConfigItemSerializer
