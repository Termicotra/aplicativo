from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EjercicioViewSet, OpcionEjercicioViewSet, ResponderEjercicioAPIView

router = DefaultRouter()
router.register(r'ejercicios', EjercicioViewSet, basename='ejercicio-evaluacion')
router.register(r'opciones', OpcionEjercicioViewSet, basename='opcion-ejercicio-evaluacion')

custom_urls = [
    path('responder/', ResponderEjercicioAPIView.as_view(), name='responder-ejercicio'),
]

urlpatterns = custom_urls + router.urls
