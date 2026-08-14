from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Leccion, ProgresoCapacitacion
from .serializers import (
    LeccionListSerializer,
    LeccionDetailSerializer,
    ProgresoCapacitacionSerializer,
)


class LeccionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Leccion.objects.filter(activa=True)
    permission_classes = [IsAuthenticated]
    serializer_class = LeccionListSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LeccionDetailSerializer
        return LeccionListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        return Leccion.objects.filter(activa=True).order_by('orden')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def marcar_completada(self, request, pk=None):
        leccion = self.get_object()
        user = request.user

        progreso, _ = ProgresoCapacitacion.objects.update_or_create(
            usuario=user,
            leccion=leccion,
            defaults={
                'completada': True,
                'fecha_completacion': timezone.now(),
            },
        )

        serializer = ProgresoCapacitacionSerializer(progreso)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mi_progreso(self, request):
        user = request.user
        progresos = ProgresoCapacitacion.objects.filter(usuario=user)
        serializer = ProgresoCapacitacionSerializer(progresos, many=True)
        return Response(serializer.data)
