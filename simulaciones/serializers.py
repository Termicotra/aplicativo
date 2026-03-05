from rest_framework import serializers

from .models import Simulacion


class SimulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simulacion
        fields = ['id', 'usuario', 'articulo', 'resultado', 'feedback', 'fecha']
        read_only_fields = ['fecha']
