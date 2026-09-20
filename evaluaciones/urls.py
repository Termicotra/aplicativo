from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    EjercicioViewSet,
    OpcionEjercicioViewSet,
    ResponderEjercicioAPIView,
    RespuestasEvaluacionAPIView,
    TotalesEvaluacionAPIView,
    EvaluacionesPendientesAPIView,
    EstadisticasEvaluacionAPIView,
    ResetearEvaluacionesAPIView,
)

router = DefaultRouter()
router.register(r'ejercicios', EjercicioViewSet, basename='ejercicio-evaluacion')
router.register(r'opciones', OpcionEjercicioViewSet, basename='opcion-ejercicio-evaluacion')

custom_urls = [
    path('responder/', ResponderEjercicioAPIView.as_view(), name='responder-ejercicio'),
    path('respuestas/', RespuestasEvaluacionAPIView.as_view(), name='mis-respuestas'),
    path('totales/', TotalesEvaluacionAPIView.as_view(), name='totales'),
    path('pendientes/', EvaluacionesPendientesAPIView.as_view(), name='evaluaciones-pendientes'),
    path('estadisticas/', EstadisticasEvaluacionAPIView.as_view(), name='estadisticas-evaluacion'),
    path('resetear/', ResetearEvaluacionesAPIView.as_view(), name='resetear-evaluaciones'),
]

urlpatterns = custom_urls + router.urls
