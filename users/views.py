from django.contrib.auth import get_user_model
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

# Create your views here.
