from rest_framework import viewsets

from .models import Simulacion
from .serializers import SimulacionSerializer


class SimulacionViewSet(viewsets.ModelViewSet):
	queryset = Simulacion.objects.select_related('usuario', 'articulo').all()
	serializer_class = SimulacionSerializer

# Create your views here.
