from django.shortcuts import get_object_or_404
from django.db.models import F
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ejercicio, OpcionEjercicio, RespuestaEjercicio
from .serializers import (
    EjercicioSerializer,
    OpcionEjercicioSerializer,
    ResponderEjercicioSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['Evaluaciones'], summary='Listar ejercicios', description='Obtiene los ejercicios de evaluación disponibles para detectar phishing.'),
    retrieve=extend_schema(tags=['Evaluaciones'], summary='Obtener ejercicio', description='Devuelve el detalle de un ejercicio específico.'),
    create=extend_schema(tags=['Evaluaciones'], summary='Crear ejercicio', description='Registra un nuevo ejercicio de entrenamiento.'),
    update=extend_schema(tags=['Evaluaciones'], summary='Actualizar ejercicio', description='Actualiza todos los datos de un ejercicio existente.'),
    partial_update=extend_schema(tags=['Evaluaciones'], summary='Actualizar ejercicio parcialmente', description='Modifica solo los campos enviados de un ejercicio existente.'),
    destroy=extend_schema(tags=['Evaluaciones'], summary='Eliminar ejercicio', description='Elimina un ejercicio de la plataforma.'),
)
class EjercicioViewSet(viewsets.ModelViewSet):
    queryset = Ejercicio.objects.prefetch_related('opciones').all()
    serializer_class = EjercicioSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        activo = self.request.query_params.get('activo')

        if activo is None:
            return queryset

        return queryset.filter(activo=activo.lower() == 'true')


@extend_schema_view(
    list=extend_schema(tags=['Evaluaciones'], summary='Listar opciones de ejercicio', description='Devuelve todas las opciones asociadas a los ejercicios de entrenamiento.'),
    retrieve=extend_schema(tags=['Evaluaciones'], summary='Obtener opción', description='Devuelve una opción de ejercicio específica.'),
    create=extend_schema(tags=['Evaluaciones'], summary='Crear opción', description='Registra una nueva opción para un ejercicio.'),
    update=extend_schema(tags=['Evaluaciones'], summary='Actualizar opción', description='Actualiza todos los datos de una opción de ejercicio.'),
    partial_update=extend_schema(tags=['Evaluaciones'], summary='Actualizar opción parcialmente', description='Modifica solo los campos enviados de una opción de ejercicio.'),
    destroy=extend_schema(tags=['Evaluaciones'], summary='Eliminar opción', description='Elimina una opción de ejercicio del sistema.'),
)
class OpcionEjercicioViewSet(viewsets.ModelViewSet):
    queryset = OpcionEjercicio.objects.select_related('ejercicio').all()
    serializer_class = OpcionEjercicioSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=['Evaluaciones'],
    summary='Responder ejercicio',
    description='Evalúa la elección del usuario y devuelve retroalimentación educativa contextualizada para reforzar el aprendizaje.',
    request=ResponderEjercicioSerializer,
    responses={200: None},
)
class ResponderEjercicioAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResponderEjercicioSerializer

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


@extend_schema(
    tags=['Evaluaciones'],
    summary='Obtener respuestas del usuario',
    description='Devuelve la última respuesta que el usuario ha registrado en cada evaluación.',
    responses={200: None},
)
class RespuestasEvaluacionAPIView(APIView):
    """
    Devuelve la última respuesta del usuario en cada evaluación.
    Filtra para obtener solo la respuesta más reciente por ejercicio.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Obtener la última respuesta por ejercicio
        respuestas = RespuestaEjercicio.objects.filter(usuario=request.user).select_related('ejercicio').values(
            'id', 'usuario', 'ejercicio', 'es_correcta', 'fecha_respuesta'
        ).annotate(ejercicio_tema=F('ejercicio__tema')).order_by('ejercicio', '-fecha_respuesta').distinct('ejercicio')

        return Response(list(respuestas), status=status.HTTP_200_OK)


@extend_schema(
    tags=['Evaluaciones'],
    summary='Obtener totales de evaluaciones',
    description='Devuelve el total de ejercicios activos disponibles.',
    responses={200: None},
)
class TotalesEvaluacionAPIView(APIView):
    """
    Devuelve los totales de evaluaciones disponibles.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        total_evaluaciones = Ejercicio.objects.filter(activo=True).count()
        return Response({'total': total_evaluaciones}, status=status.HTTP_200_OK)
