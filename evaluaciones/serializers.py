from rest_framework import serializers

from .models import Ejercicio, OpcionEjercicio


class OpcionEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionEjercicio
        fields = ['id', 'ejercicio', 'texto', 'es_correcta', 'retroalimentacion_opcion', 'orden']


class OpcionEjercicioPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionEjercicio
        fields = ['id', 'texto', 'orden']


class EjercicioSerializer(serializers.ModelSerializer):
    opciones = OpcionEjercicioPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Ejercicio
        fields = [
            'id',
            'tema',
            'pregunta',
            'concepto',
            'ejemplo',
            'retroalimentacion',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
            'opciones',
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion', 'opciones']


class ResponderEjercicioSerializer(serializers.Serializer):
    ejercicio_id = serializers.IntegerField()
    opcion_id = serializers.IntegerField()
