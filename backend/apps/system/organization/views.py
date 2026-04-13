from django.db.models import Q
from rest_framework import viewsets

from .models import Organization, Position, UserOrganizationRelation
from .serializers import OrganizationSerializer, PositionSerializer, UserOrganizationRelationSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.select_related("parent", "leader").all().order_by("sort", "id")
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.query_params.get("keyword", "").strip()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(code__icontains=keyword))
        return queryset


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all().order_by("sort", "id")
    serializer_class = PositionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.query_params.get("keyword", "").strip()
        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(code__icontains=keyword))
        status = self.request.query_params.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class UserOrganizationRelationViewSet(viewsets.ModelViewSet):
    queryset = UserOrganizationRelation.objects.select_related("user", "organization", "position").all().order_by("relation_type", "id")
    serializer_class = UserOrganizationRelationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user")
        organization_id = self.request.query_params.get("organization")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)
        return queryset

    def perform_destroy(self, instance):
        user = instance.user
        super().perform_destroy(instance)
        primary_relation = (
            UserOrganizationRelation.objects.select_related("organization", "position")
            .filter(user=user, relation_type="primary", status="active")
            .first()
        )
        user.organization = primary_relation.organization if primary_relation else None
        user.position_name = primary_relation.position.name if primary_relation and primary_relation.position else ""
        user.save(update_fields=["organization", "position_name"])
