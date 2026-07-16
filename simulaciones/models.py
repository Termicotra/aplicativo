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


class AIInteraction(models.Model):
    """Registra los prompts enviados a la API de IA y sus respuestas."""
    # Identificador único secuencial para auditoría externa
    # Se rellenará por migración y en producción se configurará con una secuencia DB.
    id_iainteraction = models.BigIntegerField(unique=True, editable=False)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='ai_interactions',
        null=True,
        blank=True,
    )
    prompt = models.TextField()
    prompt_metadata = models.JSONField(default=dict, blank=True)
    response = models.TextField()
    response_metadata = models.JSONField(default=dict, blank=True)
    model_name = models.CharField(max_length=100, default='', blank=True)
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_interaction'
        ordering = ['-created_at']

    def __str__(self):
        return f'AIInteraction {self.id} - {self.model_name}'
