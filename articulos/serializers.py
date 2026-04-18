from rest_framework import serializers

from .models import Articulo


class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = [
            'id',
            'titulo',
            'contenido',
            'proceso_ataque',
            'secuencia_ataque',
            'recomendaciones',
            'ejemplos_ataque',
            'origen_ataque',
            'objetivo_ataque',
            'canal_ataque',
            'fuente',
            'url',
            'fecha',
        ]
