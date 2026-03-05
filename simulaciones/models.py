from django.contrib.auth import get_user_model
from django.db import models

from articulos.models import Articulo

User = get_user_model()


class Simulacion(models.Model):
    RESULTADO_CHOICES = (
        ('correcto', 'Correcto'),
        ('incorrecto', 'Incorrecto'),
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='simulaciones',
    )
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.CASCADE,
        related_name='simulaciones',
    )
    resultado = models.CharField(max_length=10, choices=RESULTADO_CHOICES)
    feedback = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'simulacion'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} - {self.resultado}'
