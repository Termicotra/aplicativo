from django.contrib.auth import get_user_model
from django.db import models

from articulos.models import Articulo

User = get_user_model()


class Simulacion(models.Model):
    RESULTADO_CHOICES = (
        ('correcto', 'Correcto'),
        ('incorrecto', 'Incorrecto'),
        ('sin-responder', 'Sin responder'),
    )
    
    TIPO_GENERACION_CHOICES = (
        ('inicial', 'Inicial'),
        ('regenerado', 'Regenerado'),
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='simulaciones',
        null=True,
        blank=True,
    )
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.CASCADE,
        related_name='simulaciones_generadas',
    )
    es_phishing = models.BooleanField(default=True)
    simulacion_texto = models.TextField(default='')
    tipo_mensaje = models.CharField(max_length=20, default='correo')
    sender_email = models.CharField(max_length=255, default='')
    subject = models.CharField(max_length=255, default='')
    attachments = models.JSONField(default=list)
    enlace_senuelo = models.TextField(default='')
    entidad_objetivo = models.CharField(max_length=255, default='')
    dominio_objetivo = models.CharField(max_length=255, default='')
    resumen_justificacion = models.TextField(default='')
    resultado = models.CharField(max_length=20, choices=RESULTADO_CHOICES, default='sin-responder')
    feedback = models.TextField(default='')
    tipo_generacion = models.CharField(max_length=20, choices=TIPO_GENERACION_CHOICES, default='inicial')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(auto_now=True)
    es_mostrada = models.BooleanField(default=False)

    class Meta:
        db_table = 'simulacion'
        ordering = ['-fecha_creacion']

    def __str__(self):
        tipo = 'Phishing' if self.es_phishing else 'Legítimo'
        return f'{self.articulo.titulo[:30]} - {tipo}'
