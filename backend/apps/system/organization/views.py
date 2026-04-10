from rest_framework import viewsets
from .models import Organization
from .serializers import OrganizationSerializer

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("parent").all().order_by("sort", "id")
    serializer_class = OrganizationSerializer
