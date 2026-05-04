from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ejercicio, OpcionEjercicio, RespuestaEjercicio
from .serializers import (
    EjercicioSerializer,
    OpcionEjercicioSerializer,
    ResponderEjercicioSerializer,
)


class EjercicioViewSet(viewsets.ModelViewSet):
    queryset = Ejercicio.objects.prefetch_related('opciones').all()
    serializer_class = EjercicioSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        activo = self.request.query_params.get('activo')

        if activo is None:
            return queryset

        return queryset.filter(activo=activo.lower() == 'true')


class OpcionEjercicioViewSet(viewsets.ModelViewSet):
    queryset = OpcionEjercicio.objects.select_related('ejercicio').all()
    serializer_class = OpcionEjercicioSerializer


class ResponderEjercicioAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResponderEjercicioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ejercicio = get_object_or_404(Ejercicio, id=data['ejercicio_id'], activo=True)
        opcion = get_object_or_404(OpcionEjercicio, id=data['opcion_id'], ejercicio=ejercicio)
        opcion_correcta = get_object_or_404(OpcionEjercicio, ejercicio=ejercicio, es_correcta=True)

        es_correcta = opcion.es_correcta

        if request.user.is_authenticated:
            RespuestaEjercicio.objects.create(
                usuario=request.user,
                ejercicio=ejercicio,
                opcion_seleccionada=opcion,
                es_correcta=es_correcta,
            )

        if es_correcta:
            retroalimentacion = (
                opcion.retroalimentacion_opcion
                or 'Respuesta correcta. Buen trabajo identificando el escenario.'
            )
        else:
            retroalimentacion = (
                opcion.retroalimentacion_opcion
                or ejercicio.retroalimentacion
                or 'Respuesta incorrecta. Revisa el concepto y vuelve a intentarlo.'
            )

        return Response(
            {
                'ejercicio_id': ejercicio.id,
                'tema': ejercicio.tema,
                'es_correcta': es_correcta,
                'retroalimentacion': retroalimentacion,
                'respuesta_correcta': {
                    'opcion_id': opcion_correcta.id,
                    'texto': opcion_correcta.texto,
                },
                'concepto': ejercicio.concepto,
                'ejemplo': ejercicio.ejemplo,
            },
            status=status.HTTP_200_OK,
        )
