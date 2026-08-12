import json
import os
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from articulos.models import Articulo
from articulos.serializers import ArticuloSerializer
from capacitaciones.models import Ejercicio, OpcionEjercicio
from capacitaciones.serializers import EjercicioSerializer, OpcionEjercicioSerializer
from simulaciones.ai_service import generar_simulacion_y_feedback
from simulaciones.models import Simulacion
from simulaciones.serializers import SimulacionSerializer

User = get_user_model()


class SimulacionSerializerTestCase(TestCase):
    def test_serializer_includes_all_simulacion_fields(self):
        user = User.objects.create_user(username='demo', email='demo@example.com', password='secret123')
        articulo = Articulo.objects.create(
            titulo='Articulo prueba',
            contenido='Contenido del artículo',
            fuente='CERT Paraguay',
            url='https://example.com/articulo-prueba',
            fecha='2026-08-01',
        )
        simulacion = Simulacion.objects.create(
            usuario=user,
            articulo=articulo,
            es_phishing=True,
            simulacion_texto='Contenido simulado',
            tipo_mensaje='correo',
            sender_email='remitente@ejemplo.com',
            subject='Asunto',
            attachments=['archivo.pdf'],
            enlace_senuelo='https://phishing.example.com',
            entidad_objetivo='Banco',
            dominio_objetivo='ejemplo.com',
            resumen_justificacion='Resumen',
            resultado='correcto',
            feedback='Feedback',
            tipo_generacion='inicial',
            es_mostrada=True,
        )

        data = SimulacionSerializer(simulacion).data

        for field in [
            'id',
            'usuario',
            'articulo',
            'es_phishing',
            'simulacion_texto',
            'tipo_mensaje',
            'sender_email',
            'subject',
            'attachments',
            'enlace_senuelo',
            'entidad_objetivo',
            'dominio_objetivo',
            'resumen_justificacion',
            'resultado',
            'feedback',
            'tipo_generacion',
            'fecha_creacion',
            'fecha_respuesta',
            'es_mostrada',
        ]:
            self.assertIn(field, data)


class ArticuloSerializerTestCase(TestCase):
    def test_serializer_includes_all_model_fields(self):
        articulo = Articulo.objects.create(
            titulo='Articulo de prueba',
            contenido='Contenido del articulo',
            proceso_ataque='Proceso',
            secuencia_ataque='Secuencia',
            recomendaciones='Recomendaciones',
            ejemplos_ataque='Ejemplo',
            origen_ataque='Origen',
            objetivo_ataque='Objetivo',
            canal_ataque='correo',
            fuente='CERT Paraguay',
            url='https://example.com/articulo-2',
            fecha='2026-08-03',
        )

        data = ArticuloSerializer(articulo).data

        for field in [
            'id',
            'titulo',
            'contenido',
            'proceso_ataque',
            'secuencia_ataque',
            'recomendaciones',
            'ejemplos_ataque',
            'origen_ataque',
            'objetivo_ataque',
            'canal_ataque',
            'fuente',
            'url',
            'fecha',
        ]:
            self.assertIn(field, data)


class EjercicioSerializerTestCase(TestCase):
    def test_serializer_includes_all_model_fields(self):
        ejercicio = Ejercicio.objects.create(
            tema='Phishing',
            pregunta='¿Qué es phishing?',
            concepto='Concepto',
            ejemplo='Ejemplo',
            retroalimentacion='Retroalimentacion',
            activo=True,
        )
        opcion = OpcionEjercicio.objects.create(
            ejercicio=ejercicio,
            texto='Opción correcta',
            es_correcta=True,
            retroalimentacion_opcion='Muy bien',
            orden=1,
        )

        data = EjercicioSerializer(ejercicio).data
        opcion_data = OpcionEjercicioSerializer(opcion).data

        for field in [
            'id',
            'tema',
            'pregunta',
            'concepto',
            'ejemplo',
            'retroalimentacion',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
            'opciones',
        ]:
            self.assertIn(field, data)

        for field in ['id', 'ejercicio', 'texto', 'es_correcta', 'retroalimentacion_opcion', 'orden']:
            self.assertIn(field, opcion_data)


class GeneracionSimulacionTestCase(TestCase):
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key', 'OPENAI_MODEL': 'gpt-4o-mini'}, clear=False)
    @patch('openai.OpenAI')
    def test_no_phishing_never_includes_attachments(self, openai_mock):
        completion = MagicMock()
        completion.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        'simulacion': 'Este es un mensaje oficial del Banco Nacional.',
                        'tipo_mensaje': 'correo',
                        'sender_email': 'info@bna.com.py',
                        'subject': 'Actualizacion de seguridad',
                        'attachments': ['factura.pdf', 'documento.xlsx'],
                        'es_phishing': False,
                        'feedback': 'El mensaje es legítimo.',
                        'resultado': 'correcto',
                        'resumen_justificacion': 'Es una comunicacion oficial sin indicios de fraude.',
                    })
                )
            )
        ]
        openai_mock.return_value.chat.completions.create.return_value = completion

        result = generar_simulacion_y_feedback(
            prompt_usuario='Genera una simulación legítima',
            articulos_recientes=[{
                'titulo': 'Aviso de seguridad',
                'contenido': 'Se informa a clientes sobre seguridad.',
                'canal_ataque': 'correo',
                'fuente': 'Banco Nacional',
                'fecha': '2026-08-12',
            }],
            articulo_base={
                'titulo': 'Aviso de seguridad',
                'contenido': 'Se informa a clientes sobre seguridad.',
                'proceso_ataque': 'Aviso interno',
                'secuencia_ataque': 'Se confirma credencial',
                'recomendaciones': 'Revisa el sitio oficial',
                'ejemplos_ataque': 'Phishing',
                'origen_ataque': 'A nivel interno',
                'objetivo_ataque': 'Educación',
                'canal_ataque': 'correo',
                'fuente': 'Banco Nacional',
                'fecha': '2026-08-12',
                'url': 'https://www.bna.com.py',
            },
            force_es_phishing=False,
        )

        self.assertEqual(result['es_phishing'], 'false')
        self.assertEqual(result['attachments'], [])
