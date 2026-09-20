from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.management import call_command
from django.http import JsonResponse

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


@api_view(['POST'])
@extend_schema(
	tags=['Tareas'],
	summary='Ejecutar refresco de datos',
	description='Ejecuta la tarea de refresco: borra artículos y simulaciones, luego regenera.'
)
def refresh_data(request):
	"""
	Ejecuta el comando de refresco de datos.
	Solo POST permitido.
	"""
	try:
		call_command('refresh_data')
		return Response(
			{'status': 'success', 'message': 'Datos refrescados exitosamente'},
			status=status.HTTP_200_OK
		)
	except Exception as e:
		return Response(
			{'status': 'error', 'message': str(e)},
			status=status.HTTP_500_INTERNAL_SERVER_ERROR
		)
