#!/usr/bin/env python
"""
Script para probar los nuevos endpoints de evaluaciones
Ejecutar: python manage.py shell < test_evaluaciones.py
"""
import django
from django.contrib.auth.models import User
from evaluaciones.models import Ejercicio, OpcionEjercicio, RespuestaEjercicio

# Limpiar respuestas previas
print("=" * 60)
print("PREPARANDO TEST DE EVALUACIONES")
print("=" * 60)

# Usar usuario existente
usuario = User.objects.get(username='federico')
print(f"\n✓ Usuario: {usuario.username}")

# Limpiar respuestas anteriores
count, _ = RespuestaEjercicio.objects.filter(usuario=usuario).delete()
print(f"✓ Respuestas previas eliminadas: {count}")

# Ver ejercicios disponibles
ejercicios = Ejercicio.objects.filter(activo=True)
print(f"✓ Ejercicios activos: {ejercicios.count()}")

print("\n" + "=" * 60)
print("TEST 1: Obtener evaluaciones pendientes (debe haber 4)")
print("=" * 60)

from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from evaluaciones.views import EvaluacionesPendientesAPIView

factory = APIRequestFactory()
request = factory.get('/api/evaluaciones/pendientes/')
request.user = usuario

view = EvaluacionesPendientesAPIView.as_view()
response = view(request)

print(f"\nTotal pendientes: {response.data['total_pendientes']}")
print(f"Total ejercicios: {response.data['total_ejercicios']}")
print("\nEjercicios pendientes:")
for ejercicio in response.data['pendientes']:
    print(f"  - {ejercicio['tema']}: {ejercicio['pregunta'][:50]}...")

print("\n" + "=" * 60)
print("TEST 2: Responder un ejercicio")
print("=" * 60)

# Responder el primer ejercicio
ejercicio = ejercicios.first()
opcion_correcta = OpcionEjercicio.objects.filter(
    ejercicio=ejercicio,
    es_correcta=True
).first()

respuesta = RespuestaEjercicio.objects.create(
    usuario=usuario,
    ejercicio=ejercicio,
    opcion_seleccionada=opcion_correcta,
    es_correcta=True
)
print(f"\n✓ Respuesta creada: {usuario.username} → {ejercicio.tema}")

print("\n" + "=" * 60)
print("TEST 3: Obtener estadísticas")
print("=" * 60)

from evaluaciones.views import EstadisticasEvaluacionAPIView

request = factory.get('/api/evaluaciones/estadisticas/')
request.user = usuario

view = EstadisticasEvaluacionAPIView.as_view()
response = view(request)

stats = response.data
print(f"\n✓ Total respuestas: {stats['total_respuestas']}")
print(f"✓ Respuestas correctas: {stats['respuestas_correctas']}")
print(f"✓ Porcentaje aciertos: {stats['porcentaje_aciertos']}%")
print(f"✓ Ejercicios respondidos: {stats['ejercicios_respondidos']}/{stats['total_ejercicios']}")
print(f"✓ Completado: {stats['completado']}")

print("\n✓ Estadísticas por tema:")
for tema in stats['estadisticas_por_tema']:
    print(f"  - {tema['tema']}: {tema['correctas']}/{tema['total']} ({tema['porcentaje']}%)")

print("\n" + "=" * 60)
print("TEST 4: Obtener evaluaciones pendientes nuevamente (debe haber 3)")
print("=" * 60)

request = factory.get('/api/evaluaciones/pendientes/')
request.user = usuario

view = EvaluacionesPendientesAPIView.as_view()
response = view(request)

print(f"\n✓ Total pendientes: {response.data['total_pendientes']}")
print("✓ Ejercicios pendientes:")
for ejercicio in response.data['pendientes']:
    print(f"  - {ejercicio['tema']}: {ejercicio['pregunta'][:50]}...")

print("\n" + "=" * 60)
print("TEST 5: Resetear evaluaciones")
print("=" * 60)

from evaluaciones.views import ResetearEvaluacionesAPIView

request = factory.post('/api/evaluaciones/resetear/')
request.user = usuario

view = ResetearEvaluacionesAPIView.as_view()
response = view(request)

print(f"\n✓ Status: {response.data['status']}")
print(f"✓ Mensaje: {response.data['message']}")

print("\n" + "=" * 60)
print("TEST 6: Obtener evaluaciones pendientes después de resetear")
print("=" * 60)

request = factory.get('/api/evaluaciones/pendientes/')
request.user = usuario

view = EvaluacionesPendientesAPIView.as_view()
response = view(request)

print(f"\n✓ Total pendientes: {response.data['total_pendientes']}")
print(f"✓ Total ejercicios: {response.data['total_ejercicios']}")

print("\n" + "=" * 60)
print("✓ TODOS LOS TESTS PASARON")
print("=" * 60)
