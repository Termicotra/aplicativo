from rest_framework import serializers

from .models import Simulacion, RespuestaSimulacion


class SimulacionSerializer(serializers.ModelSerializer):
    articulo_titulo = serializers.CharField(source='articulo.titulo', read_only=True)
    articulo_url = serializers.CharField(source='articulo.url', read_only=True)

    class Meta:
        model = Simulacion
        fields = [
            'id',
            'usuario',
            'articulo',
            'articulo_titulo',
            'articulo_url',
            'es_phishing',
            'simulacion_texto',
            'tipo_mensaje',
            'sender_email',
            'subject',
            'attachments',
            'enlace_senuelo',
            'entidad_objetivo',
            'dominio_objetivo',
            'resumen_justificacion',
            'resultado',
            'feedback',
            'tipo_generacion',
            'fecha_creacion',
            'fecha_respuesta',
            'es_mostrada',
        ]
        read_only_fields = ['fecha_creacion', 'fecha_respuesta']


class RespuestaSimulacionSerializer(serializers.ModelSerializer):
    simulacion_titulo = serializers.CharField(source='simulacion.articulo.titulo', read_only=True)

    class Meta:
        model = RespuestaSimulacion
        fields = [
            'id',
            'usuario',
            'simulacion',
            'simulacion_titulo',
            'respuesta_usuario',
            'es_correcta',
            'fecha_respuesta',
        ]
        read_only_fields = ['fecha_respuesta']


class GenerarSimulacionRequestSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField(required=False)
    articulo_id = serializers.IntegerField(required=False)
    tipo_simulacion = serializers.CharField(required=False, default='correo phishing')
    prompt = serializers.CharField(required=False, allow_blank=True)
    respuesta_usuario = serializers.CharField(required=False, allow_blank=True)
