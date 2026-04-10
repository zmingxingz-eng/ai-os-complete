from rest_framework import viewsets
from common.permissions.permission_code import PermissionCodePermission
from common.permissions.data_scope import DataScopeFilter
from common.utils.audit import audit_action
from .models import Notice
from .serializers import NoticeSerializer

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [PermissionCodePermission]
    required_permission = "notice.manage"

    def get_queryset(self):
        queryset = super().get_queryset()
        return DataScopeFilter.filter_queryset(queryset, self.request.user, user_field="creator")

    @audit_action("create", "notice")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @audit_action("update", "notice")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @audit_action("delete", "notice")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
