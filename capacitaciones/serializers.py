from rest_framework import serializers
from .models import Leccion, SeccionLeccion, ItemListaSeccion, ProgresoCapacitacion


class ItemListaSeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemListaSeccion
        fields = ['id', 'texto', 'orden']


class SeccionLeccionSerializer(serializers.ModelSerializer):
    items_lista = ItemListaSeccionSerializer(many=True, read_only=True)

    class Meta:
        model = SeccionLeccion
        fields = ['id', 'encabezado', 'texto', 'items_lista', 'orden']


class LeccionListSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    bloqueada = serializers.SerializerMethodField()

    class Meta:
        model = Leccion
        fields = [
            'id',
            'titulo',
            'duracion',
            'orden',
            'activa',
            'bloqueada',
            'fecha_creacion',
            'completed',
        ]

    def get_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ProgresoCapacitacion.objects.filter(
            usuario=request.user,
            leccion=obj,
            completada=True,
        ).exists()

    def get_bloqueada(self, obj):
        request = self.context.get('request')

        if obj.bloqueada:
            return True

        if not request or not request.user.is_authenticated:
            return obj.orden > 1

        if obj.orden == 1:
            return False

        leccion_anterior = Leccion.objects.filter(
            orden=obj.orden - 1,
            activa=True,
        ).first()

        if not leccion_anterior:
            return False

        return not ProgresoCapacitacion.objects.filter(
            usuario=request.user,
            leccion=leccion_anterior,
            completada=True,
        ).exists()


class LeccionDetailSerializer(serializers.ModelSerializer):
    secciones = SeccionLeccionSerializer(many=True, read_only=True)
    contenido = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    bloqueada = serializers.SerializerMethodField()

    class Meta:
        model = Leccion
        fields = [
            'id',
            'titulo',
            'duracion',
            'orden',
            'contenido',
            'activa',
            'bloqueada',
            'fecha_creacion',
            'secciones',
            'completed',
        ]

    def get_contenido(self, obj):
        return {
            'title': obj.contenido_titulo or obj.titulo,
            'sections': [
                {
                    'heading': s.encabezado,
                    'text': s.texto or None,
                    'list': [item.texto for item in s.items_lista.all()] or None,
                }
                for s in obj.secciones.all()
            ],
        }

    def get_completed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return ProgresoCapacitacion.objects.filter(
            usuario=request.user,
            leccion=obj,
            completada=True,
        ).exists()

    def get_bloqueada(self, obj):
        request = self.context.get('request')

        if obj.bloqueada:
            return True

        if not request or not request.user.is_authenticated:
            return obj.orden > 1

        if obj.orden == 1:
            return False

        leccion_anterior = Leccion.objects.filter(
            orden=obj.orden - 1,
            activa=True,
        ).first()

        if not leccion_anterior:
            return False

        return not ProgresoCapacitacion.objects.filter(
            usuario=request.user,
            leccion=leccion_anterior,
            completada=True,
        ).exists()


class ProgresoCapacitacionSerializer(serializers.ModelSerializer):
    leccion_titulo = serializers.CharField(source='leccion.titulo', read_only=True)

    class Meta:
        model = ProgresoCapacitacion
        fields = [
            'id',
            'leccion',
            'leccion_titulo',
            'completada',
            'fecha_inicio',
            'fecha_completacion',
        ]
        read_only_fields = ['fecha_inicio', 'fecha_completacion']
