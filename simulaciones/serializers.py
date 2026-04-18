from rest_framework import serializers

from .models import Simulacion


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
            'simulacion_texto',
            'resumen_justificacion',
            'resultado',
            'feedback',
            'fecha',
        ]
        read_only_fields = ['fecha']


class GenerarSimulacionRequestSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField(required=False)
    articulo_id = serializers.IntegerField(required=False)
    tipo_simulacion = serializers.CharField(required=False, default='correo phishing')
    prompt = serializers.CharField(required=False, allow_blank=True)
    respuesta_usuario = serializers.CharField(required=False, allow_blank=True)
