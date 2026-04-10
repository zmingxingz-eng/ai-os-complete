from django.contrib.auth.models import Group
from rest_framework import viewsets
from .serializers import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.select_related("profile").all().order_by("id")
    serializer_class = RoleSerializer
