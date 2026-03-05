from django.contrib import admin

from .models import Simulacion


@admin.register(Simulacion)
class SimulacionAdmin(admin.ModelAdmin):
	list_display = ('usuario', 'articulo', 'resultado', 'fecha')
	search_fields = ('usuario__username', 'articulo__titulo', 'feedback')
	list_filter = ('resultado', 'fecha')

# Register your models here.
