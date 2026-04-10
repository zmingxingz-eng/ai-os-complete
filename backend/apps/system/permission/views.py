from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from .models import MenuPermission
from .serializers import PermissionSerializer, MenuPermissionSerializer

INTERNAL_PERMISSION_APP_LABELS = {"admin", "contenttypes", "sessions"}


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.select_related("content_type").exclude(
        content_type__app_label__in=INTERNAL_PERMISSION_APP_LABELS
    ).order_by("content_type__app_label", "codename")
    serializer_class = PermissionSerializer

    @action(detail=False, methods=["get"], url_path="content-types")
    def content_types(self, request):
        data = [
            {
                "id": item.id,
                "app_label": item.app_label,
                "model": item.model,
                "label": f"{item.app_label}.{item.model}",
            }
            for item in ContentType.objects.exclude(
                app_label__in=INTERNAL_PERMISSION_APP_LABELS
            ).order_by("app_label", "model")
        ]
        return Response(data)


class MenuPermissionViewSet(viewsets.ModelViewSet):
    queryset = MenuPermission.objects.select_related("menu", "permission", "permission__content_type").exclude(
        permission__content_type__app_label__in=INTERNAL_PERMISSION_APP_LABELS
    ).order_by("menu__sort", "sort", "id")
    serializer_class = MenuPermissionSerializer
