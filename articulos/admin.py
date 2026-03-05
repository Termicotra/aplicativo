from django.contrib import admin

from .models import Articulo


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
	list_display = ('titulo', 'fuente', 'fecha')
	search_fields = ('titulo', 'fuente', 'url')
	list_filter = ('fuente', 'fecha')

# Register your models here.
