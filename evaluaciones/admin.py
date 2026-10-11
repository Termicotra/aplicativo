from django.contrib import admin

from .models import Ejercicio, OpcionEjercicio, RespuestaEjercicio


class OpcionEjercicioInline(admin.TabularInline):
    model = OpcionEjercicio
    extra = 1


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('tema', 'pregunta_corta', 'activo', 'fecha_creacion')
    search_fields = ('tema', 'pregunta', 'concepto', 'ejemplo', 'retroalimentacion')
    list_filter = ('tema', 'activo', 'fecha_creacion')
    inlines = [OpcionEjercicioInline]

    @staticmethod
    def pregunta_corta(obj):
        return obj.pregunta[:60]


@admin.register(OpcionEjercicio)
class OpcionEjercicioAdmin(admin.ModelAdmin):
    list_display = ('ejercicio', 'orden', 'es_correcta')
    search_fields = ('ejercicio__tema', 'ejercicio__pregunta', 'texto')
    list_filter = ('es_correcta',)


@admin.register(RespuestaEjercicio)
class RespuestaEjercicioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ejercicio', 'es_correcta', 'fecha_respuesta')
    search_fields = ('usuario__username', 'ejercicio__tema', 'ejercicio__pregunta')
    list_filter = ('es_correcta', 'fecha_respuesta')
