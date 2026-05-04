#!/usr/bin/env python
"""
Test script to verify the new simulation display workflow
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
import json

def test_workflow():
    """Test the complete simulation workflow"""
    client = Client()
    
    print("=" * 70)
    print("Testing Complete Simulation Workflow")
    print("=" * 70)
    
    # Test 1: Load random simulation
    print("\n[1/4] Loading random simulation...")
    print("-" * 70)
    
    response = client.get('/api/simulaciones/obtener-aleatoria/')
    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        return False
    
    sim1 = response.json()
    print(f"[OK] Loaded simulation {sim1['simulacion_id']}")
    print(f"     Article: {sim1['articulo_titulo'][:50]}")
    print(f"     Type: {sim1['tipo_mensaje']}")
    print(f"     Is phishing: {sim1['es_phishing']}")
    
    # Test 2: Generate opposite type for same simulation
    print("\n[2/4] Generating opposite simulation...")
    print("-" * 70)
    
    response = client.post(
        '/api/simulaciones/opuesto/',
        data=json.dumps({'simulacion_id': sim1['simulacion_id']}),
        content_type='application/json',
        HTTP_X_CSRFTOKEN='dummy'  # For testing
    )
    if response.status_code not in (200, 201):
        print(f"FAILED: Status {response.status_code}")
        print(f"Response: {response.content.decode()[:200]}")
        return False
    
    sim2 = response.json()
    print(f"[OK] Opposite simulation obtained {sim2['simulacion_id']}")
    print(f"     Article: {sim2['articulo_titulo'][:50]}")
    print(f"     Type: {sim2['tipo_mensaje']}")
    print(f"     Is phishing: {sim2['es_phishing']}")
    print(f"     Generation type: {sim2.get('tipo_generacion', 'N/A')}")
    
    # Test 3: Load another random
    print("\n[3/4] Loading another random simulation...")
    print("-" * 70)
    
    response = client.get('/api/simulaciones/obtener-aleatoria/')
    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        return False
    
    sim3 = response.json()
    print(f"[OK] Loaded simulation {sim3['simulacion_id']}")
    print(f"     Article: {sim3['articulo_titulo'][:50]}")
    
    # Test 4: Verify database state
    print("\n[4/4] Checking database state...")
    print("-" * 70)
    
    from simulaciones.models import Simulacion
    
    total = Simulacion.objects.count()
    mostradas = Simulacion.objects.filter(es_mostrada=True).count()
    regeneradas = Simulacion.objects.filter(tipo_generacion='regenerado').count()
    
    print(f"[OK] Total simulations: {total}")
    print(f"     Marked as shown: {mostradas}")
    print(f"     Regenerated: {regeneradas}")
    
    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_workflow()
    sys.exit(0 if success else 1)
