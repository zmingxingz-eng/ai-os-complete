from rest_framework.routers import DefaultRouter
from .views import ConfigItemViewSet

router = DefaultRouter()
router.register("", ConfigItemViewSet, basename="config-center")
urlpatterns = router.urls
