from django.contrib import admin

from .models import Simulacion
from .models import AIInteraction


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


	@admin.register(AIInteraction)
	class AIInteractionAdmin(admin.ModelAdmin):
		list_display = ('id', 'usuario', 'model_name', 'success', 'created_at')
		search_fields = ('prompt', 'response', 'model_name', 'usuario__username')
		list_filter = ('model_name', 'success', 'created_at')
