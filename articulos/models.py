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
	canal_ataque = models.CharField(max_length=30, default='indefinido')
	fuente = models.CharField(max_length=100)
	url = models.URLField(unique=True)
	fecha = models.DateField()

	class Meta:
		db_table = 'articulo'
		ordering = ['-fecha']

	def __str__(self):
		return self.titulo
