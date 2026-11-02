import json
import os
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from articulos.models import Articulo
from articulos.serializers import ArticuloSerializer
from evaluaciones.models import Ejercicio, OpcionEjercicio
from evaluaciones.serializers import EjercicioSerializer, OpcionEjercicioSerializer
from simulaciones.ai_service import generar_simulacion_y_feedback
from simulaciones.models import RespuestaSimulacion, Simulacion
from simulaciones.serializers import SimulacionSerializer
from simulaciones.views import cantidad_a_mostrar

User = get_user_model()


class SimulacionSerializerTestCase(TestCase):
    def test_serializer_includes_all_simulacion_fields(self):
        articulo = Articulo.objects.create(
            titulo='Articulo prueba',
            contenido='Contenido del artículo',
            fuente='CERT Paraguay',
            url='https://example.com/articulo-prueba',
            fecha='2026-08-01',
        )
        simulacion = Simulacion.objects.create(
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


class CantidadARondaTestCase(SimpleTestCase):
    def test_cantidad_a_mostrar_segun_total_disponible(self):
        casos = {
            0: 0,
            1: 1,
            14: 14,
            15: 15,
            19: 15,
            20: 20,
            50: 20,
        }
        for total, esperado in casos.items():
            with self.subTest(total=total):
                self.assertEqual(cantidad_a_mostrar(total), esperado)


class FiltroSimulacionesParaUsuarioTestCase(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='alumno', email='alumno@example.com', password='secret123')
        self.otro = User.objects.create_user(username='otro', email='otro@example.com', password='secret123')
        self.articulo = Articulo.objects.create(
            titulo='Articulo base',
            contenido='Contenido',
            fuente='CERT Paraguay',
            url='https://example.com/base',
            fecha='2026-08-01',
        )
        self.client.force_authenticate(self.usuario)

    def _crear_simulaciones(self, cantidad):
        return [
            Simulacion.objects.create(
                articulo=self.articulo,
                es_phishing=(i % 2 == 0),
                simulacion_texto=f'Simulacion {i}',
            )
            for i in range(cantidad)
        ]

    def _para_usuario(self):
        response = self.client.get(reverse('para-usuario'))
        self.assertEqual(response.status_code, 200)
        return response.data

    def test_ronda_completa_de_20_cuando_hay_25_disponibles(self):
        self._crear_simulaciones(25)

        data = self._para_usuario()

        self.assertEqual(data['total_disponibles'], 25)
        self.assertEqual(data['cantidad_ronda'], 20)
        self.assertEqual(len(data['simulaciones']), 20)

    def test_ronda_de_15_cuando_hay_18_disponibles(self):
        self._crear_simulaciones(18)

        data = self._para_usuario()

        self.assertEqual(data['cantidad_ronda'], 15)
        self.assertEqual(len(data['simulaciones']), 15)

    def test_muestra_todas_cuando_hay_menos_de_15(self):
        self._crear_simulaciones(7)

        data = self._para_usuario()

        self.assertEqual(data['cantidad_ronda'], 7)
        self.assertEqual(len(data['simulaciones']), 7)

    def test_no_vuelve_a_pedir_simulaciones_ya_respondidas(self):
        simulaciones = self._crear_simulaciones(25)
        respondidas = simulaciones[:5]
        for simulacion in respondidas:
            RespuestaSimulacion.objects.create(
                usuario=self.usuario,
                simulacion=simulacion,
                respuesta_usuario=True,
                es_correcta=True,
            )

        data = self._para_usuario()
        ids_pendientes = {item['id'] for item in data['simulaciones']}

        self.assertEqual(data['respondidas'], 5)
        self.assertEqual(data['correctas'], 5)
        self.assertEqual(len(data['simulaciones']), 15)
        self.assertTrue(ids_pendientes.isdisjoint({s.id for s in respondidas}))

    def test_ronda_completa_no_devuelve_pendientes(self):
        simulaciones = self._crear_simulaciones(25)
        for simulacion in simulaciones[:20]:
            RespuestaSimulacion.objects.create(
                usuario=self.usuario, simulacion=simulacion, respuesta_usuario=False, es_correcta=False,
            )

        data = self._para_usuario()

        self.assertEqual(data['respondidas'], 20)
        self.assertEqual(data['simulaciones'], [])

    def test_respuestas_de_otro_usuario_no_descuentan_la_ronda(self):
        simulaciones = self._crear_simulaciones(25)
        for simulacion in simulaciones[:10]:
            RespuestaSimulacion.objects.create(
                usuario=self.otro, simulacion=simulacion, respuesta_usuario=True, es_correcta=True,
            )

        data = self._para_usuario()

        self.assertEqual(data['respondidas'], 0)
        self.assertEqual(len(data['simulaciones']), 20)

    def test_reiniciar_vuelve_a_mostrar_la_ronda_completa(self):
        simulaciones = self._crear_simulaciones(25)
        for simulacion in simulaciones[:20]:
            RespuestaSimulacion.objects.create(
                usuario=self.usuario, simulacion=simulacion, respuesta_usuario=True, es_correcta=True,
            )

        response = self.client.post(reverse('reiniciar-simulaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['respuestas_eliminadas'], 20)

        data = self._para_usuario()
        self.assertEqual(data['respondidas'], 0)
        self.assertEqual(len(data['simulaciones']), 20)

    def test_registrar_respuesta_evalua_correctamente(self):
        phishing = self._crear_simulaciones(2)  # índice 0 es phishing, índice 1 es legítimo

        acierto = self.client.post(
            reverse('registrar-respuesta'),
            {'simulacion_id': phishing[0].id, 'respuesta_usuario': 'phishing'},
            format='json',
        )
        fallo = self.client.post(
            reverse('registrar-respuesta'),
            {'simulacion_id': phishing[1].id, 'respuesta_usuario': 'phishing'},
            format='json',
        )

        self.assertTrue(acierto.data['fue_correcto'])
        self.assertFalse(fallo.data['fue_correcto'])
        self.assertTrue(RespuestaSimulacion.objects.get(usuario=self.usuario, simulacion=phishing[0]).es_correcta)
        self.assertFalse(RespuestaSimulacion.objects.get(usuario=self.usuario, simulacion=phishing[1]).es_correcta)
