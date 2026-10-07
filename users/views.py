from django.contrib.auth import get_user_model, authenticate
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
	AuthUserSerializer,
	ChangePasswordSerializer,
	LoginSerializer,
	RegisterSerializer,
	UserSerializer,
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['Autenticación'], summary='Listar usuarios', description='Endpoint administrativo para consultar usuarios registrados.'),
    retrieve=extend_schema(tags=['Autenticación'], summary='Obtener usuario', description='Devuelve los datos de un usuario específico.'),
    create=extend_schema(tags=['Autenticación'], summary='Crear usuario', description='Crea un nuevo registro de usuario.'),
    update=extend_schema(tags=['Autenticación'], summary='Actualizar usuario', description='Actualiza todos los datos de un usuario existente.'),
    partial_update=extend_schema(tags=['Autenticación'], summary='Actualizar usuario parcialmente', description='Actualiza solo los campos enviados para un usuario existente.'),
    destroy=extend_schema(tags=['Autenticación'], summary='Eliminar usuario', description='Elimina un usuario del sistema.'),
)
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all().order_by('id')
	serializer_class = UserSerializer
	permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['username'] = user.username
		token['email'] = user.email
		return token

	def validate(self, attrs):
		# Hacer login case-insensitive: buscar usuario por username en minúsculas
		username = attrs.get('username', '').lower()
		password = attrs.get('password', '')

		try:
			user = User.objects.get(username__iexact=username)
			attrs['username'] = user.username
		except User.DoesNotExist:
			pass

		data = super().validate(attrs)
		data['user'] = AuthUserSerializer(self.user).data
		return data


@extend_schema(
	tags=['Autenticación'],
	summary='Iniciar sesión',
	description='Autentica un usuario y devuelve un JWT junto con la información pública del perfil.',
)
class LoginView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
	tags=['Autenticación'],
	summary='Registrar usuario',
	description='Crea un nuevo usuario con nombre, correo y contraseña segura.',
	request=RegisterSerializer,
	responses={201: AuthUserSerializer},
)
class RegisterAPIView(APIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = RegisterSerializer

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		return Response(
			{
				'message': 'Usuario registrado correctamente.',
				'user': AuthUserSerializer(user).data,
			},
			status=status.HTTP_201_CREATED,
		)


@extend_schema(
	tags=['Autenticación'],
	summary='Cambiar contraseña',
	description='Actualiza la contraseña del usuario autenticado validando la contraseña actual.',
	request=ChangePasswordSerializer,
	responses={200: None},
)
class ChangePasswordAPIView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ChangePasswordSerializer

	def post(self, request):
		serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception=True)
		request.user.set_password(serializer.validated_data['new_password'])
		request.user.save(update_fields=['password'])
		return Response({'message': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)


@extend_schema(
	tags=['Progreso'],
	summary='Obtener progreso general',
	description='Devuelve el progreso completo del usuario: lecciones, simulaciones y evaluaciones.',
	responses={200: None},
)
class MiProgresoAPIView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		user = request.user

		# ============ LECCIONES ============
		from capacitaciones.models import ProgresoCapacitacion, Leccion
		lecciones_completadas = ProgresoCapacitacion.objects.filter(
			usuario=user,
			completada=True
		).count()
		lecciones_totales = Leccion.objects.filter(activa=True).count()

		# ============ SIMULACIONES ============
		from simulaciones.models import RespuestaSimulacion
		simulaciones_correctas = RespuestaSimulacion.objects.filter(
			usuario=user,
			es_correcta=True
		).count()
		simulaciones_totales = RespuestaSimulacion.objects.filter(usuario=user).count()

		# ============ EVALUACIONES ============
		from evaluaciones.models import RespuestaEjercicio, Ejercicio
		evaluaciones_correctas = RespuestaEjercicio.objects.filter(
			usuario=user,
			es_correcta=True
		).count()
		evaluaciones_totales = RespuestaEjercicio.objects.filter(usuario=user).count()
		ejercicios_totales = Ejercicio.objects.filter(activo=True).count()

		# ============ CÁLCULO DINÁMICO DE PROGRESO ============
		# Cada módulo contribuye 1/3 al progreso general
		progreso_lecciones = (lecciones_completadas / lecciones_totales * 100) if lecciones_totales > 0 else 0
		progreso_simulaciones = (simulaciones_correctas / simulaciones_totales * 100) if simulaciones_totales > 0 else 0
		progreso_evaluaciones = (evaluaciones_correctas / evaluaciones_totales * 100) if evaluaciones_totales > 0 else 0

		# Promedio ponderado: 33% cada uno
		progreso_general = round((progreso_lecciones + progreso_simulaciones + progreso_evaluaciones) / 3, 2)

		# Cap al 100% máximo
		progreso_general = min(progreso_general, 100.0)

		return Response({
			'progreso_general': progreso_general,
			'puntaje_promedio': round((evaluaciones_correctas / evaluaciones_totales * 100), 2) if evaluaciones_totales > 0 else 0,
			'lecciones': {
				'completadas': lecciones_completadas,
				'totales': lecciones_totales,
				'porcentaje': round((lecciones_completadas / lecciones_totales * 100), 2) if lecciones_totales > 0 else 0,
			},
			'simulaciones': {
				'correctas': simulaciones_correctas,
				'totales': simulaciones_totales,
				'porcentaje': round((simulaciones_correctas / simulaciones_totales * 100), 2) if simulaciones_totales > 0 else 0,
			},
			'evaluaciones': {
				'correctas': evaluaciones_correctas,
				'totales': evaluaciones_totales,
				'porcentaje': round((evaluaciones_correctas / evaluaciones_totales * 100), 2) if evaluaciones_totales > 0 else 0,
				'ejercicios_pendientes': ejercicios_totales - evaluaciones_totales,
			},
		}, status=status.HTTP_200_OK)
