from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets

from .models import Articulo
from .serializers import ArticuloSerializer


@extend_schema_view(
	list=extend_schema(tags=['Artículos'], summary='Listar artículos', description='Consulta todos los artículos de contexto usados para generar simulaciones.'),
	retrieve=extend_schema(tags=['Artículos'], summary='Obtener artículo', description='Devuelve el detalle de un artículo específico.'),
	create=extend_schema(tags=['Artículos'], summary='Crear artículo', description='Registra un nuevo artículo de contexto para la base de conocimiento.'),
	update=extend_schema(tags=['Artículos'], summary='Actualizar artículo', description='Actualiza todos los datos de un artículo existente.'),
	partial_update=extend_schema(tags=['Artículos'], summary='Actualizar artículo parcialmente', description='Modifica solo los campos enviados de un artículo existente.'),
	destroy=extend_schema(tags=['Artículos'], summary='Eliminar artículo', description='Elimina un artículo de la base de conocimiento.'),
)
class ArticuloViewSet(viewsets.ModelViewSet):
	queryset = Articulo.objects.all()
	serializer_class = ArticuloSerializer
	permission_classes = [permissions.AllowAny]

# Create your views here.
