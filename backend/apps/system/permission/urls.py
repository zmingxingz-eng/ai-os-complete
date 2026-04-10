from rest_framework.routers import DefaultRouter
from .views import PermissionViewSet, MenuPermissionViewSet

router = DefaultRouter()
router.register("", PermissionViewSet, basename="permission")
router.register("menu-bindings", MenuPermissionViewSet, basename="menu-permission")
urlpatterns = router.urls
