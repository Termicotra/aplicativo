from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    SimulacionViewSet,
    ObtenerSimulacionAleatoria,
    OpuestoSimulacion,
    RegistrarRespuestaSimulacion,
    RespuestasSimulacionAPIView,
    TotalesSimulacionAPIView,
)

router = DefaultRouter()
router.register(r'', SimulacionViewSet, basename='simulacion')

# URL patterns for custom endpoints
custom_urls = [
    path('obtener-aleatoria/', ObtenerSimulacionAleatoria.as_view(), name='obtener-simulacion-aleatoria'),
    path('opuesto/', OpuestoSimulacion.as_view(), name='opuesto-simulacion'),
    path('registrar-respuesta/', RegistrarRespuestaSimulacion.as_view(), name='registrar-respuesta'),
    path('mis-respuestas/', RespuestasSimulacionAPIView.as_view(), name='mis-respuestas'),
    path('totales/', TotalesSimulacionAPIView.as_view(), name='totales'),
]

urlpatterns = custom_urls + router.urls
