from rest_framework.routers import DefaultRouter

from .views import ArticuloViewSet

router = DefaultRouter()
router.register(r'', ArticuloViewSet, basename='articulo')

urlpatterns = router.urls
