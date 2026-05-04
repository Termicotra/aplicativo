from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Ejercicio, OpcionEjercicio, RespuestaEjercicio

User = get_user_model()


class CapacitacionesAPITestCase(APITestCase):
	def setUp(self):
		self.ejercicio = Ejercicio.objects.create(
			tema='Phishing',
			pregunta='Cual de estas opciones es una senal de phishing?',
			concepto='El phishing busca robar datos con suplantacion de identidad.',
			ejemplo='Correo falso que pide validar cuenta bancaria.',
			retroalimentacion='Verifica remitente, enlaces y urgencia del mensaje.',
		)
		self.opcion_correcta = OpcionEjercicio.objects.create(
			ejercicio=self.ejercicio,
			texto='El mensaje pide credenciales por un enlace acortado.',
			orden=1,
			es_correcta=True,
			retroalimentacion_opcion='Correcto. Solicitar credenciales por enlace es una alerta comun.',
		)
		self.opcion_incorrecta = OpcionEjercicio.objects.create(
			ejercicio=self.ejercicio,
			texto='El correo viene de un dominio oficial verificado.',
			orden=2,
			es_correcta=False,
			retroalimentacion_opcion='Incorrecto. En este caso no hay un indicador claro de fraude.',
		)

	def test_listar_ejercicios_con_opciones_publicas(self):
		response = self.client.get('/api/capacitaciones/ejercicios/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(len(response.data[0]['opciones']), 2)
		self.assertNotIn('es_correcta', response.data[0]['opciones'][0])

	def test_responder_ejercicio_correctamente(self):
		response = self.client.post(
			'/api/capacitaciones/responder/',
			{'ejercicio_id': self.ejercicio.id, 'opcion_id': self.opcion_correcta.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data['es_correcta'])
		self.assertEqual(response.data['respuesta_correcta']['opcion_id'], self.opcion_correcta.id)

	def test_responder_ejercicio_incorrectamente(self):
		response = self.client.post(
			'/api/capacitaciones/responder/',
			{'ejercicio_id': self.ejercicio.id, 'opcion_id': self.opcion_incorrecta.id},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(response.data['es_correcta'])
		self.assertEqual(response.data['respuesta_correcta']['opcion_id'], self.opcion_correcta.id)


class CapacitacionesWebViewTestCase(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='tester', password='pass12345')
		self.client.login(username='tester', password='pass12345')
		self.ejercicio = Ejercicio.objects.create(
			tema='Phishing',
			pregunta='Que debes revisar antes de abrir un enlace?',
			concepto='Verifica remitente y dominio real.',
			ejemplo='Un correo urgente solicita actualizar datos.',
			retroalimentacion='Debes validar el dominio del enlace.',
		)
		self.opcion_correcta = OpcionEjercicio.objects.create(
			ejercicio=self.ejercicio,
			texto='Revisar remitente y dominio oficial.',
			orden=1,
			es_correcta=True,
		)
		self.opcion_incorrecta = OpcionEjercicio.objects.create(
			ejercicio=self.ejercicio,
			texto='Hacer clic de inmediato para no perder acceso.',
			orden=2,
			es_correcta=False,
		)

	def test_capacitaciones_section_renderiza(self):
		response = self.client.get('/capacitaciones/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertContains(response, 'Modulo de Capacitaciones')
		self.assertContains(response, self.ejercicio.pregunta)

	def test_capacitaciones_section_responder(self):
		response = self.client.post(
			'/capacitaciones/',
			{'ejercicio_id': self.ejercicio.id, 'opcion_id': self.opcion_correcta.id},
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertContains(response, 'Respuesta correcta')
		self.assertEqual(RespuestaEjercicio.objects.filter(usuario=self.user).count(), 1)

	def test_dashboard_muestra_progreso_capacitaciones(self):
		RespuestaEjercicio.objects.create(
			usuario=self.user,
			ejercicio=self.ejercicio,
			opcion_seleccionada=self.opcion_correcta,
			es_correcta=True,
		)
		RespuestaEjercicio.objects.create(
			usuario=self.user,
			ejercicio=self.ejercicio,
			opcion_seleccionada=self.opcion_incorrecta,
			es_correcta=False,
		)

		response = self.client.get('/dashboard/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertContains(response, 'Progreso de capacitaciones')
		self.assertContains(response, 'Total respuestas:')
		self.assertContains(response, '2')


class SeedCapacitacionesCommandTestCase(TestCase):
	def test_seed_capacitaciones_crea_ejercicios_y_opciones(self):
		output = StringIO()
		call_command('seed_capacitaciones', stdout=output)

		self.assertGreaterEqual(Ejercicio.objects.count(), 3)
		for ejercicio in Ejercicio.objects.all():
			self.assertEqual(ejercicio.opciones.filter(es_correcta=True).count(), 1)
			self.assertGreaterEqual(ejercicio.opciones.count(), 3)
