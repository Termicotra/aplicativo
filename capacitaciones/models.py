from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class Leccion(models.Model):
    titulo = models.CharField(max_length=255)
    duracion = models.CharField(max_length=50, default='5 min')
    orden = models.PositiveSmallIntegerField(default=0)
    contenido_titulo = models.CharField(max_length=255, blank=True)
    activa = models.BooleanField(default=True)
    bloqueada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leccion_capacitacion'
        ordering = ['orden', 'id']

    def __str__(self):
        return self.titulo


class SeccionLeccion(models.Model):
    leccion = models.ForeignKey(
        Leccion,
        on_delete=models.CASCADE,
        related_name='secciones',
    )
    encabezado = models.CharField(max_length=255)
    texto = models.TextField(blank=True, default='')
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'seccion_leccion'
        ordering = ['leccion', 'orden']

    def __str__(self):
        return f'{self.leccion.titulo} - {self.encabezado}'


class ItemListaSeccion(models.Model):
    seccion = models.ForeignKey(
        SeccionLeccion,
        on_delete=models.CASCADE,
        related_name='items_lista',
    )
    texto = models.TextField()
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'item_lista_seccion'
        ordering = ['seccion', 'orden']

    def __str__(self):
        return f'{self.seccion.leccion.titulo} - Item {self.orden}'


class ProgresoCapacitacion(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progreso_capacitaciones',
    )
    leccion = models.ForeignKey(
        Leccion,
        on_delete=models.CASCADE,
        related_name='progresos',
    )
    completada = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'progreso_capacitacion'
        unique_together = ['usuario', 'leccion']
        ordering = ['-fecha_completacion', '-fecha_inicio']

    def __str__(self):
        return f'{self.usuario.username} - {self.leccion.titulo}'
