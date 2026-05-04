from rest_framework import serializers

from .models import Ejercicio, OpcionEjercicio


class OpcionEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcionEjercicio
        fields = ['id', 'ejercicio', 'texto', 'orden', 'es_correcta', 'retroalimentacion_opcion']


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
            'opciones',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class ResponderEjercicioSerializer(serializers.Serializer):
    ejercicio_id = serializers.IntegerField()
    opcion_id = serializers.IntegerField()
