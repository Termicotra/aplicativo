from django.contrib import admin

from .models import Simulacion
from .models import AIInteraction


@admin.register(Simulacion)
class SimulacionAdmin(admin.ModelAdmin):
	list_display = ('articulo', 'es_phishing', 'resultado', 'fecha_creacion')
	search_fields = (
		'articulo__titulo',
		'simulacion_texto',
		'resumen_justificacion',
		'feedback',
	)
	list_filter = ('resultado', 'es_phishing', 'fecha_creacion')


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
	list_display = ('id', 'model_name', 'success', 'created_at')
	search_fields = ('prompt', 'response', 'model_name')
	list_filter = ('model_name', 'success', 'created_at')
