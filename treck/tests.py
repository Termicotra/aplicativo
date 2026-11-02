"""Pruebas de sistema: recorren el flujo completo de un usuario a través de la API.

Cubren registro, autenticación JWT, artículos, simulaciones, evaluaciones y capacitaciones.
Los filtros de ingesta y de selección de simulaciones tienen sus pruebas en
articulos/tests.py y simulaciones/tests.py.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from articulos.models import Articulo
from evaluaciones.models import Ejercicio, OpcionEjercicio
from simulaciones.models import RespuestaSimulacion, Simulacion

User = get_user_model()

PASSWORD = 'clave-segura-123'


class FlujoUsuarioSistemaTests(APITestCase):
    """Un usuario nuevo se registra, entrena y consulta su progreso."""

    def setUp(self):
        self.articulo = Articulo.objects.create(
            titulo='Phishing bancario en Paraguay',
            contenido='Los atacantes envían correos falsos a clientes.',
            proceso_ataque='Envío de correo falso con enlace.',
            secuencia_ataque='La víctima ingresa credenciales en la página clonada.',
            ejemplos_ataque='Caso reportado por CERT Paraguay.',
            canal_ataque='correo',
            fuente='CERT Paraguay',
            url='https://www.cert.gov.py/alerta-sistema',
            fecha='2026-08-01',
        )

    def _registrar_y_loguear(self):
        response = self.client.post(
            reverse('api_register'),
            {
                'username': 'nuevo',
                'email': 'nuevo@example.com',
                'password': PASSWORD,
                'password_confirm': PASSWORD,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            reverse('api_login'),
            {'username': 'nuevo', 'password': PASSWORD},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return User.objects.get(username='nuevo')

    def test_flujo_completo_de_un_usuario(self):
        usuario = self._registrar_y_loguear()

        # Progreso inicial disponible para el usuario autenticado
        self.assertEqual(self.client.get(reverse('mi_progreso')).status_code, 200)

        # Artículos públicos
        response = self.client.get(reverse('articulo-list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Phishing bancario en Paraguay', str(response.data))

        # Simulaciones: ronda con 3 casos, responder uno y volver a pedir pendientes
        simulaciones = [
            Simulacion.objects.create(articulo=self.articulo, es_phishing=True, simulacion_texto=f'Caso {i}')
            for i in range(3)
        ]
        ronda = self.client.get(reverse('para-usuario')).data
        self.assertEqual(ronda['cantidad_ronda'], 3)
        self.assertEqual(len(ronda['simulaciones']), 3)

        respuesta = self.client.post(
            reverse('registrar-respuesta'),
            {'simulacion_id': simulaciones[0].id, 'respuesta_usuario': 'phishing'},
            format='json',
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.data['fue_correcto'])

        ronda = self.client.get(reverse('para-usuario')).data
        self.assertEqual(ronda['respondidas'], 1)
        self.assertEqual(ronda['correctas'], 1)
        self.assertEqual(len(ronda['simulaciones']), 2)
        self.assertTrue(RespuestaSimulacion.objects.filter(usuario=usuario).exists())
        self.assertEqual(self.client.get(reverse('mis-respuestas')).status_code, 200)

        # Evaluaciones: ejercicio con una opción correcta y una incorrecta
        ejercicio = Ejercicio.objects.create(
            tema='Phishing',
            pregunta='¿Cuál es la señal de phishing?',
            concepto='Urgencia excesiva',
            retroalimentacion='Revisa siempre el remitente.',
        )
        correcta = OpcionEjercicio.objects.create(
            ejercicio=ejercicio, texto='Urgencia y enlace raro', es_correcta=True, orden=1,
        )
        OpcionEjercicio.objects.create(
            ejercicio=ejercicio, texto='Saludo formal', es_correcta=False, orden=2,
        )

        pendientes = self.client.get(reverse('evaluaciones-pendientes'))
        self.assertEqual(pendientes.status_code, 200)
        self.assertEqual(pendientes.data['total_ejercicios'], 1)
        self.assertEqual(pendientes.data['total_pendientes'], 1)

        respuesta = self.client.post(
            reverse('responder-ejercicio'),
            {'ejercicio_id': ejercicio.id, 'opcion_id': correcta.id},
            format='json',
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(self.client.get(reverse('evaluaciones-pendientes')).data['total_pendientes'], 0)
        self.assertEqual(self.client.get(reverse('estadisticas-evaluacion')).status_code, 200)

        # Opción que no pertenece al ejercicio no se acepta
        otro = Ejercicio.objects.create(tema='Otro', pregunta='?', concepto='?', retroalimentacion='?')
        opcion_ajena = OpcionEjercicio.objects.create(ejercicio=otro, texto='x', es_correcta=True, orden=1)
        respuesta = self.client.post(
            reverse('responder-ejercicio'),
            {'ejercicio_id': ejercicio.id, 'opcion_id': opcion_ajena.id},
            format='json',
        )
        self.assertEqual(respuesta.status_code, 404)

        # Capacitaciones disponibles para usuarios autenticados
        self.assertEqual(self.client.get('/api/capacitaciones/lecciones/').status_code, 200)

        # Reiniciar la práctica de simulaciones borra sus respuestas
        reinicio = self.client.post(reverse('reiniciar-simulaciones'))
        self.assertEqual(reinicio.status_code, 200)
        self.assertEqual(reinicio.data['respuestas_eliminadas'], 1)
        self.assertEqual(self.client.get(reverse('para-usuario')).data['respondidas'], 0)

    def test_endpoints_privados_rechazan_usuarios_anonimos(self):
        cliente = APIClient()

        privados = [
            reverse('mi_progreso'),
            reverse('para-usuario'),
            reverse('mis-respuestas'),
            reverse('evaluaciones-pendientes'),
            reverse('estadisticas-evaluacion'),
            '/api/capacitaciones/lecciones/',
        ]
        for url in privados:
            with self.subTest(url=url):
                self.assertIn(cliente.get(url).status_code, (401, 403))

    def test_login_con_credenciales_incorrectas_falla(self):
        User.objects.create_user(username='nuevo', email='nuevo@example.com', password=PASSWORD)

        response = self.client.post(
            reverse('api_login'),
            {'username': 'nuevo', 'password': 'contraseña-equivocada'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)
        self.assertNotIn('access', response.data)

    def test_registro_rechaza_contrasenas_que_no_coinciden(self):
        response = self.client.post(
            reverse('api_register'),
            {
                'username': 'otro',
                'email': 'otro@example.com',
                'password': PASSWORD,
                'password_confirm': 'distinta-clave-456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username='otro').exists())


class PaginasWebSistemaTests(TestCase):
    def test_paginas_publicas_responden(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('register')).status_code, 200)

    def test_dashboard_redirige_a_login_si_no_hay_sesion(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])
