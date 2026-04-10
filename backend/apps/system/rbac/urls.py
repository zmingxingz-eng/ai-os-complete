from rest_framework.routers import DefaultRouter
from .views import UserRoleViewSet, RolePermissionViewSet, RoleMenuViewSet, RoleDataScopeViewSet

router = DefaultRouter()
router.register("user-role", UserRoleViewSet, basename="user-role")
router.register("role-permission", RolePermissionViewSet, basename="role-permission")
router.register("role-menu", RoleMenuViewSet, basename="role-menu")
router.register("role-data-scope", RoleDataScopeViewSet, basename="role-data-scope")
urlpatterns = router.urls
