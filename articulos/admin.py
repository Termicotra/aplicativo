from django.contrib import admin

from .models import Articulo


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'fuente', 'canal_ataque', 'fecha')
	search_fields = (
		'titulo',
		'fuente',
		'url',
		'proceso_ataque',
		'secuencia_ataque',
		'ejemplos_ataque',
	)
	list_filter = ('fuente', 'fecha')

# Register your models here.
