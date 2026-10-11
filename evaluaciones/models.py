from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

User = get_user_model()


class Ejercicio(models.Model):
    tema = models.CharField(max_length=120)
    pregunta = models.TextField()
    concepto = models.TextField()
    ejemplo = models.TextField(default='')
    retroalimentacion = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ejercicio_evaluacion'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.tema}: {self.pregunta[:50]}'


class OpcionEjercicio(models.Model):
    ejercicio = models.ForeignKey(
        Ejercicio,
        on_delete=models.CASCADE,
        related_name='opciones',
    )
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    retroalimentacion_opcion = models.TextField(blank=True, default='')
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = 'opcion_evaluacion'
        ordering = ['orden', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['ejercicio', 'orden'],
                name='unique_orden_por_ejercicio',
            ),
            models.UniqueConstraint(
                fields=['ejercicio'],
                condition=Q(es_correcta=True),
                name='unique_respuesta_correcta_por_ejercicio',
            ),
        ]

    def __str__(self):
        return f'{self.ejercicio.tema} - Opcion {self.orden}'


class RespuestaEjercicio(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='respuestas_capacitacion',
    )
    ejercicio = models.ForeignKey(
        Ejercicio,
        on_delete=models.CASCADE,
        related_name='respuestas',
    )
    opcion_seleccionada = models.ForeignKey(
        OpcionEjercicio,
        on_delete=models.CASCADE,
        related_name='respuestas',
    )
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'respuesta_evaluacion'
        ordering = ['-fecha_respuesta']

    def __str__(self):
        estado = 'Correcta' if self.es_correcta else 'Incorrecta'
        return f'{self.usuario.username} - {self.ejercicio.tema} - {estado}'
