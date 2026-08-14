from django.contrib import admin
from .models import Leccion, SeccionLeccion, ItemListaSeccion, ProgresoCapacitacion


class ItemListaSeccionInline(admin.TabularInline):
    model = ItemListaSeccion
    extra = 1


class SeccionLeccionInline(admin.StackedInline):
    model = SeccionLeccion
    extra = 1
    inlines = [ItemListaSeccionInline]


@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'orden', 'duracion', 'activa', 'bloqueada', 'fecha_creacion')
    search_fields = ('titulo', 'contenido_titulo')
    list_filter = ('activa', 'bloqueada', 'fecha_creacion')
    ordering = ('orden',)
    inlines = [SeccionLeccionInline]


@admin.register(SeccionLeccion)
class SeccionLeccionAdmin(admin.ModelAdmin):
    list_display = ('leccion', 'orden', 'encabezado')
    search_fields = ('leccion__titulo', 'encabezado', 'texto')
    list_filter = ('leccion',)
    inlines = [ItemListaSeccionInline]


@admin.register(ItemListaSeccion)
class ItemListaSeccionAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'orden', 'texto_corto')
    search_fields = ('seccion__leccion__titulo', 'seccion__encabezado', 'texto')
    list_filter = ('seccion__leccion',)

    @staticmethod
    def texto_corto(obj):
        return obj.texto[:60]


@admin.register(ProgresoCapacitacion)
class ProgresoCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'leccion', 'completada', 'fecha_inicio', 'fecha_completacion')
    search_fields = ('usuario__username', 'leccion__titulo')
    list_filter = ('completada', 'fecha_inicio', 'fecha_completacion')
    readonly_fields = ('fecha_inicio', 'fecha_completacion')
