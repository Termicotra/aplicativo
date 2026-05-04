#!/usr/bin/env python
"""
Test script for simulation endpoints
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from simulaciones.models import Simulacion


def test_endpoints():
    """Test the new simulation endpoints"""
    client = Client()
    
    print("=" * 60)
    print("Testing Simulation Endpoints")
    print("=" * 60)
    
    # Test 1: Obtener simulación aleatoria
    print("\n[TEST 1] GET /api/simulaciones/obtener-aleatoria/")
    print("-" * 60)
    
    response = client.get('/api/simulaciones/obtener-aleatoria/')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Respuesta exitosa")
        print(f"  - Simulación ID: {data['simulacion_id']}")
        print(f"  - Artículo: {data['articulo_titulo']}")
        print(f"  - Es Phishing: {data['es_phishing']}")
        print(f"  - Tipo: {data['tipo_mensaje']}")
        print(f"  - Sender: {data['sender_email']}")
        print(f"  - Asunto: {data['subject']}")
        sim_id = data['simulacion_id']
    else:
        print(f"[ERROR] Error: {response.content.decode()[:200]}")
        return
    
    # Test 2: Generar opuesto
    print("\n[TEST 2] POST /api/simulaciones/opuesto/")
    print("-" * 60)
    print(f"Intentando generar opuesto para simulación ID: {sim_id}")
    
    response = client.post(
        '/api/simulaciones/opuesto/',
        data=json.dumps({'simulacion_id': sim_id}),
        content_type='application/json'
    )
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in (200, 201):
        data = response.json()
        print(f"[OK] Opuesto obtenido")
        print(f"  - Simulación ID: {data['simulacion_id']}")
        print(f"  - Artículo: {data['articulo_titulo']}")
        print(f"  - Es Phishing: {data['es_phishing']}")
        print(f"  - Tipo de Generación: regenerado (debe ser)")
    else:
        print(f"[ERROR] Error: {response.content.decode()[:200]}")
    
    # Test 3: Verificar estadísticas
    print("\n[TEST 3] Estadísticas de Simulaciones")
    print("-" * 60)
    
    total_sims = Simulacion.objects.count()
    phishing_sims = Simulacion.objects.filter(es_phishing=True).count()
    legit_sims = Simulacion.objects.filter(es_phishing=False).count()
    mostradas = Simulacion.objects.filter(es_mostrada=True).count()
    
    print(f"Total Simulaciones: {total_sims}")
    print(f"  - Phishing: {phishing_sims}")
    print(f"  - Legítimas: {legit_sims}")
    print(f"  - Mostradas: {mostradas}")
    
    print("\n" + "=" * 60)
    print("[OK] Pruebas completadas")
    print("=" * 60)


if __name__ == '__main__':
    test_endpoints()
