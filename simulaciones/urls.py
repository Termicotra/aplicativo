from rest_framework.routers import DefaultRouter

from .views import SimulacionViewSet

router = DefaultRouter()
router.register(r'', SimulacionViewSet, basename='simulacion')

urlpatterns = router.urls
