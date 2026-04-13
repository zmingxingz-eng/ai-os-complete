from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, PositionViewSet, UserOrganizationRelationViewSet

router = DefaultRouter()
router.register("positions", PositionViewSet, basename="organization-position")
router.register("user-relations", UserOrganizationRelationViewSet, basename="organization-user-relation")
router.register("", OrganizationViewSet, basename="organization")
urlpatterns = router.urls
