from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Q
from rest_framework import viewsets

from apps.system.organization.models import Organization
from apps.system.organization.models import UserOrganizationRelation
from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("organization").prefetch_related(
        Prefetch(
            "organization_relations",
            queryset=UserOrganizationRelation.objects.select_related("organization", "position").order_by("relation_type", "id"),
        )
    ).all().order_by("id")
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = getattr(self.request, "query_params", self.request.GET)
        keyword = params.get("keyword", "").strip()
        if keyword:
            queryset = queryset.filter(
                Q(username__icontains=keyword)
                | Q(full_name__icontains=keyword)
                | Q(mobile__icontains=keyword)
                | Q(email__icontains=keyword)
            )
        is_active = params.get("is_active", "").strip()
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() in {"1", "true", "yes", "active"})
        organization_id = params.get("organization", "").strip()
        if organization_id:
            organization = Organization.objects.filter(pk=organization_id).first()
            if organization and organization.path:
                queryset = queryset.filter(
                    organization_relations__status="active",
                    organization_relations__organization__path__startswith=organization.path,
                ).distinct()
        return queryset
