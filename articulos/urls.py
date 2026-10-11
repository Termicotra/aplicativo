from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import ArticuloViewSet, refresh_data

router = DefaultRouter()
router.register(r'', ArticuloViewSet, basename='articulo')

urlpatterns = [
    path('refresh-data/', refresh_data, name='refresh-data'),
] + router.urls
