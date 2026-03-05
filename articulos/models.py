from django.db import models


class Articulo(models.Model):
	titulo = models.CharField(max_length=255)
	contenido = models.TextField()
	fuente = models.CharField(max_length=100)
	url = models.URLField(unique=True)
	fecha = models.DateField()

	class Meta:
		db_table = 'articulo'
		ordering = ['-fecha']

	def __str__(self):
		return self.titulo
