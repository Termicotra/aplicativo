from django.contrib import admin

from .models import Simulacion


@admin.register(Simulacion)
class SimulacionAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'articulo', 'es_phishing', 'resultado', 'fecha_creacion')
	search_fields = (
		'usuario__username',
		'articulo__titulo',
		'simulacion_texto',
		'resumen_justificacion',
		'feedback',
	)
	list_filter = ('resultado', 'es_phishing', 'fecha_creacion')

# Register your models here.
