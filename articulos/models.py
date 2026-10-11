from django.db import models


class Articulo(models.Model):
	titulo = models.CharField(max_length=255)
	contenido = models.TextField()
	proceso_ataque = models.TextField(default='')
	secuencia_ataque = models.TextField(default='')
	recomendaciones = models.TextField(default='')
	ejemplos_ataque = models.TextField(default='')
	origen_ataque = models.TextField(default='')
	objetivo_ataque = models.TextField(default='')
	canal_ataque = models.TextField(default='')  # Cambiar a TextField para valores largos de IA
	fuente = models.CharField(max_length=100)
	url = models.URLField(unique=True)
	fecha = models.DateField()
	respuesta_ia = models.JSONField(default=dict, blank=True, null=True)  # JSON de ChatGPT con extracción de campos

	class Meta:
		db_table = 'articulo'
		ordering = ['-fecha']

	def __str__(self):
		return self.titulo
