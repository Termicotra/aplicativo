from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from articulos.models import Articulo

from .ai_service import AIServiceError, generar_simulacion_y_feedback
from .models import Simulacion, RespuestaSimulacion
from .serializers import GenerarSimulacionRequestSerializer, SimulacionSerializer, RespuestaSimulacionSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(tags=['Simulaciones'], summary='Listar simulaciones', description='Consulta todas las simulaciones generadas y asociadas a usuarios y artículos.'),
    retrieve=extend_schema(tags=['Simulaciones'], summary='Obtener simulación', description='Devuelve el detalle completo de una simulación específica.'),
    create=extend_schema(tags=['Simulaciones'], summary='Crear simulación', description='Crea una nueva simulación de phishing o legítima.'),
    update=extend_schema(tags=['Simulaciones'], summary='Actualizar simulación', description='Actualiza todos los campos de una simulación existente.'),
    partial_update=extend_schema(tags=['Simulaciones'], summary='Actualizar simulación parcialmente', description='Modifica solo los campos enviados de una simulación existente.'),
    destroy=extend_schema(tags=['Simulaciones'], summary='Eliminar simulación', description='Elimina una simulación del sistema.'),
)
class SimulacionViewSet(viewsets.ModelViewSet):
    queryset = Simulacion.objects.select_related('usuario', 'articulo').all()
    serializer_class = SimulacionSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=['Simulaciones'],
    summary='Generar simulación con IA',
    description='Genera una simulación de phishing o legítima usando información contextual de artículos recientes y feedback educativo.',
    request=GenerarSimulacionRequestSerializer,
    responses={201: None},
)
class GenerarSimulacionAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GenerarSimulacionRequestSerializer

    def post(self, request):
        serializer = GenerarSimulacionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get('usuario_id'):
            usuario = get_object_or_404(User, id=data['usuario_id'])
        elif request.user.is_authenticated:
            usuario = request.user
        else:
            return Response(
                {'detail': 'Debes enviar usuario_id o autenticarte.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if data.get('articulo_id'):
            articulo = get_object_or_404(Articulo, id=data['articulo_id'])
            existente = Simulacion.objects.filter(articulo=articulo).select_related('articulo').first()
            if existente:
                return Response(
                    {
                        'detail': 'Ya existe una simulacion para este articulo.',
                        'simulacion_id': existente.id,
                        'articulo_id': articulo.id,
                        'articulo_titulo': articulo.titulo,
                        'articulo_url': articulo.url,
                        'simulacion': existente.simulacion_texto,
                        'resumen_justificacion': existente.resumen_justificacion,
                        'feedback': existente.feedback,
                        'resultado': existente.resultado,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            articulo = (
                Articulo.objects.annotate(
                    has_simulacion=Exists(
                        Simulacion.objects.filter(articulo_id=OuterRef('pk'))
                    )
                )
                .filter(has_simulacion=False)
                .order_by('-fecha')
                .first()
            )
            if not articulo:
                return Response(
                    {'detail': 'No hay articulos pendientes: ya existe 1 simulacion por cada articulo.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        articulos_recientes_qs = Articulo.objects.order_by('-fecha')[:5]
        articulos_recientes = [
            {
                'titulo': item.titulo,
                'contenido': item.contenido[:600],
                'canal_ataque': item.canal_ataque,
                'fuente': item.fuente,
                'fecha': item.fecha.isoformat(),
            }
            for item in articulos_recientes_qs
        ]
        articulo_base = {
            'titulo': articulo.titulo,
            'contenido': articulo.contenido[:600],
            'proceso_ataque': articulo.proceso_ataque,
            'secuencia_ataque': articulo.secuencia_ataque,
            'recomendaciones': articulo.recomendaciones,
            'ejemplos_ataque': articulo.ejemplos_ataque,
            'origen_ataque': articulo.origen_ataque,
            'objetivo_ataque': articulo.objetivo_ataque,
            'canal_ataque': articulo.canal_ataque,
            'fuente': articulo.fuente,
            'fecha': articulo.fecha.isoformat(),
            'url': articulo.url,
        }

        prompt_usuario = data.get('prompt') or (
            f"Generar una simulacion de {data.get('tipo_simulacion', 'correo phishing')}"
        )

        try:
            ia_output = generar_simulacion_y_feedback(
                prompt_usuario=prompt_usuario,
                articulo_base=articulo_base,
                articulos_recientes=articulos_recientes,
                respuesta_usuario=data.get('respuesta_usuario', ''),
                recipient_email=usuario.email if usuario and getattr(usuario, 'email', None) else None,
            )
        except AIServiceError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {'detail': 'No se pudo generar la simulacion con IA.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        simulacion = Simulacion.objects.create(
            usuario=usuario,
            articulo=articulo,
            simulacion_texto=ia_output['simulacion'],
            resumen_justificacion=ia_output['resumen_justificacion'],
            resultado=ia_output['resultado'],
            feedback=ia_output['feedback'],
        )

        return Response(
            {
                'simulacion_id': simulacion.id,
                'usuario_id': usuario.id,
                'articulo_id': articulo.id,
                'articulo_titulo': articulo.titulo,
                'articulo_url': articulo.url,
                'simulacion': ia_output['simulacion'],
                'sender_email': ia_output.get('sender_email', ''),
                'subject': ia_output.get('subject', ''),
                'attachments': ia_output.get('attachments', []),
                'entidad_objetivo': ia_output.get('entidad_objetivo', ''),
                'enlace_senuelo': ia_output.get('enlace_senuelo', ''),
                'resumen_justificacion': ia_output['resumen_justificacion'],
                'feedback': ia_output['feedback'],
                'resultado': ia_output['resultado'],
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=['Simulaciones'],
    summary='Obtener simulación aleatoria',
    description='Devuelve una simulación aleatoria para que el usuario la evalúe como phishing o legítima.',
    responses={200: SimulacionSerializer},
)
class ObtenerSimulacionAleatoria(APIView):
    """
    Obtiene una simulación aleatoria (phishing o legítima) para mostrar al usuario.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SimulacionSerializer

    def get(self, request):
        # Obtener una simulación aleatoria
        simulacion = Simulacion.objects.order_by('?').first()
        
        if not simulacion:
            return Response(
                {'detail': 'No hay simulaciones disponibles.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Marcar como mostrada
        simulacion.es_mostrada = True
        simulacion.save(update_fields=['es_mostrada'])
        
        return Response(
            {
                'simulacion_id': simulacion.id,
                'articulo_id': simulacion.articulo.id,
                'articulo_titulo': simulacion.articulo.titulo,
                'es_phishing': simulacion.es_phishing,
                'tipo_mensaje': simulacion.tipo_mensaje,
                'sender_email': simulacion.sender_email,
                'recipient_email': request.user.email if request.user.is_authenticated and getattr(request.user, 'email', None) else '',
                'subject': simulacion.subject,
                'attachments': simulacion.attachments,
                'enlace_senuelo': simulacion.enlace_senuelo,
                'simulacion_texto': simulacion.simulacion_texto,
                'entidad_objetivo': simulacion.entidad_objetivo,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Simulaciones'],
    summary='Obtener simulación opuesta',
    description='Recupera la versión contraria de una simulación del mismo artículo para comparar escenarios phishing y legítimos.',
    request=None,
    responses={200: None},
)
class OpuestoSimulacion(APIView):
    """
    Devuelve la simulacion opuesta ya existente para el mismo articulo
    (phishing <-> legitimo). Si no existe, la genera como respaldo.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SimulacionSerializer

    def post(self, request):
        simulacion_id = request.data.get('simulacion_id')
        
        if not simulacion_id:
            return Response(
                {'detail': 'Se requiere simulacion_id.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        simulacion_vieja = get_object_or_404(Simulacion, id=simulacion_id)
        articulo = simulacion_vieja.articulo
        es_phishing_opuesto = not simulacion_vieja.es_phishing

        simulacion_opuesta = (
            Simulacion.objects.filter(articulo=articulo, es_phishing=es_phishing_opuesto)
            .exclude(id=simulacion_vieja.id)
            .order_by('-fecha_creacion')
            .first()
        )

        if simulacion_opuesta:
            simulacion_opuesta.es_mostrada = True
            simulacion_opuesta.tipo_generacion = 'regenerado'
            simulacion_opuesta.save(update_fields=['es_mostrada', 'tipo_generacion'])

            return Response(
                {
                    'simulacion_id': simulacion_opuesta.id,
                    'articulo_id': simulacion_opuesta.articulo.id,
                    'articulo_titulo': simulacion_opuesta.articulo.titulo,
                    'es_phishing': simulacion_opuesta.es_phishing,
                    'tipo_mensaje': simulacion_opuesta.tipo_mensaje,
                    'sender_email': simulacion_opuesta.sender_email,
                    'subject': simulacion_opuesta.subject,
                    'attachments': simulacion_opuesta.attachments,
                    'enlace_senuelo': simulacion_opuesta.enlace_senuelo,
                    'simulacion_texto': simulacion_opuesta.simulacion_texto,
                    'entidad_objetivo': simulacion_opuesta.entidad_objetivo,
                },
                status=status.HTTP_200_OK,
            )

        articulo_base = {
            'titulo': articulo.titulo,
            'contenido': articulo.contenido[:600],
            'proceso_ataque': articulo.proceso_ataque,
            'secuencia_ataque': articulo.secuencia_ataque,
            'recomendaciones': articulo.recomendaciones,
            'ejemplos_ataque': articulo.ejemplos_ataque,
            'origen_ataque': articulo.origen_ataque,
            'objetivo_ataque': articulo.objetivo_ataque,
            'canal_ataque': articulo.canal_ataque,
            'fuente': articulo.fuente,
            'fecha': articulo.fecha.isoformat(),
            'url': articulo.url,
        }

        articulos_recientes_qs = Articulo.objects.order_by('-fecha')[:5]
        articulos_recientes = [
            {
                'titulo': item.titulo,
                'contenido': item.contenido[:600],
                'canal_ataque': item.canal_ataque,
                'fuente': item.fuente,
                'fecha': item.fecha.isoformat(),
            }
            for item in articulos_recientes_qs
        ]

        try:
            resultado = generar_simulacion_y_feedback(
                prompt_usuario="Generar una simulacion opuesta para capacitacion anti-phishing",
                articulo_base=articulo_base,
                articulos_recientes=articulos_recientes,
                force_es_phishing=es_phishing_opuesto,
                recipient_email=simulacion_vieja.usuario.email if getattr(simulacion_vieja, 'usuario', None) and getattr(simulacion_vieja.usuario, 'email', None) else None,
            )
        except AIServiceError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'detail': f'Error al generar opuesto: {str(e)[:100]}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Respaldo: actualizar la MISMA simulacion solo si no existe la opuesta ya generada.
        nueva_simulacion = simulacion_vieja
        nueva_simulacion.es_phishing = es_phishing_opuesto
        nueva_simulacion.simulacion_texto = resultado['simulacion']
        nueva_simulacion.tipo_mensaje = resultado.get('tipo_mensaje', 'correo')
        nueva_simulacion.sender_email = resultado.get('sender_email', '')
        nueva_simulacion.subject = resultado.get('subject', '')
        nueva_simulacion.attachments = resultado.get('attachments', [])
        nueva_simulacion.enlace_senuelo = resultado.get('enlace_senuelo', '')
        nueva_simulacion.entidad_objetivo = resultado.get('entidad_objetivo', '')
        nueva_simulacion.dominio_objetivo = resultado.get('dominio_objetivo', '')
        nueva_simulacion.resumen_justificacion = resultado.get('resumen_justificacion', '')
        nueva_simulacion.feedback = resultado.get('feedback', '')
        nueva_simulacion.tipo_generacion = 'regenerado'
        nueva_simulacion.es_mostrada = True
        nueva_simulacion.save()
        
        return Response(
            {
                'simulacion_id': nueva_simulacion.id,
                'articulo_id': nueva_simulacion.articulo.id,
                'articulo_titulo': nueva_simulacion.articulo.titulo,
                'es_phishing': nueva_simulacion.es_phishing,
                'tipo_mensaje': nueva_simulacion.tipo_mensaje,
                'sender_email': nueva_simulacion.sender_email,
                'subject': nueva_simulacion.subject,
                'attachments': nueva_simulacion.attachments,
                'enlace_senuelo': nueva_simulacion.enlace_senuelo,
                'simulacion_texto': nueva_simulacion.simulacion_texto,
                'entidad_objetivo': nueva_simulacion.entidad_objetivo,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=['Simulaciones'],
    summary='Registrar respuesta del usuario',
    description='Recibe la decisión del usuario sobre una simulación y devuelve si acertó o falló junto con la retroalimentación.',
    responses={200: None},
)
class RegistrarRespuestaSimulacion(APIView):
    """
    Registra la respuesta del usuario (phishing o no-phishing) y evalúa si fue correcta.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SimulacionSerializer

    def post(self, request):
        simulacion_id = request.data.get('simulacion_id')
        respuesta_usuario = request.data.get('respuesta_usuario')  # 'phishing' o 'no-phishing'

        if not simulacion_id or not respuesta_usuario:
            return Response(
                {'detail': 'Se requiere simulacion_id y respuesta_usuario.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if respuesta_usuario not in ['phishing', 'no-phishing']:
            return Response(
                {'detail': 'respuesta_usuario debe ser "phishing" o "no-phishing".'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        simulacion = get_object_or_404(Simulacion, id=simulacion_id)

        # Determinar si fue correcto
        esperado_es_phishing = simulacion.es_phishing
        usuario_dijo_phishing = respuesta_usuario == 'phishing'
        fue_correcto = esperado_es_phishing == usuario_dijo_phishing

        # Registrar respuesta en RespuestaSimulacion
        _, _ = RespuestaSimulacion.objects.update_or_create(
            usuario=request.user,
            simulacion=simulacion,
            defaults={
                'respuesta_usuario': usuario_dijo_phishing,
                'es_correcta': fue_correcto,
            }
        )

        # Registrar respuesta en Simulacion también (compatibilidad)
        simulacion.resultado = 'correcto' if fue_correcto else 'incorrecto'
        simulacion.save(update_fields=['resultado'])

        return Response(
            {
                'simulacion_id': simulacion.id,
                'fue_correcto': fue_correcto,
                'resultado': simulacion.resultado,
                'es_phishing_real': simulacion.es_phishing,
                'respuesta_usuario': respuesta_usuario,
                'feedback': simulacion.feedback,
                'resumen_justificacion': simulacion.resumen_justificacion,
                'articulo_titulo': simulacion.articulo.titulo,
                'articulo_url': simulacion.articulo.url,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Simulaciones'],
    summary='Obtener respuestas del usuario en simulaciones',
    description='Devuelve todas las respuestas que el usuario ha registrado en simulaciones.',
    responses={200: RespuestaSimulacionSerializer(many=True)},
)
class RespuestasSimulacionAPIView(APIView):
    """
    Devuelve las respuestas del usuario en simulaciones.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        respuestas = RespuestaSimulacion.objects.filter(usuario=request.user).select_related('simulacion__articulo')
        serializer = RespuestaSimulacionSerializer(respuestas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Simulaciones'],
    summary='Obtener totales de simulaciones',
    description='Devuelve el total de simulaciones disponibles.',
    responses={200: None},
)
class TotalesSimulacionAPIView(APIView):
    """
    Devuelve los totales de simulaciones disponibles.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        total_simulaciones = Simulacion.objects.count()
        return Response({'total': total_simulaciones}, status=status.HTTP_200_OK)
