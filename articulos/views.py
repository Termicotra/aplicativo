from rest_framework import viewsets

from .models import Articulo
from .serializers import ArticuloSerializer


class ArticuloViewSet(viewsets.ModelViewSet):
	queryset = Articulo.objects.all()
	serializer_class = ArticuloSerializer

# Create your views here.
