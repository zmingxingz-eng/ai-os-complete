from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/system/organization/", include("apps.system.organization.urls")),
    path("api/system/users/", include("apps.system.users.urls")),
    path("api/system/role/", include("apps.system.role.urls")),
    path("api/system/dictionary/", include("apps.system.dictionary.urls")),
    path("api/system/permission/", include("apps.system.permission.urls")),
    path("api/system/menu/", include("apps.system.menu.urls")),
    path("api/system/config-center/", include("apps.system.config_center.urls")),
    path("api/system/audit-log/", include("apps.system.audit_log.urls")),
    path("api/system/rbac/", include("apps.system.rbac.urls")),
    path("api/system/auth/", include("apps.system.auth.urls")),
]
