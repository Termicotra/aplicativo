#!/usr/bin/env python
"""
Test the complete simulation workflow with response registration
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

def test_complete_workflow():
    """Test the complete simulation workflow including response recording"""
    client = Client()
    
    print("=" * 70)
    print("Testing Complete Simulation Workflow with Response Recording")
    print("=" * 70)
    
    # Step 1: Load random simulation
    print("\n[1/5] Loading random simulation...")
    print("-" * 70)
    
    response = client.get('/api/simulaciones/obtener-aleatoria/')
    if response.status_code != 200:
        print(f"[FAIL] Status {response.status_code}")
        return False
    
    sim = response.json()
    print(f"[OK] Loaded simulation {sim['simulacion_id']}")
    print(f"     Article: {sim['articulo_titulo'][:50]}")
    print(f"     Is phishing: {sim['es_phishing']}")
    sim_id = sim['simulacion_id']
    es_phishing_real = sim['es_phishing']
    
    # Step 2: Register a response (correct)
    print("\n[2/5] Registering CORRECT response...")
    print("-" * 70)
    
    respuesta_usuario = 'phishing' if es_phishing_real else 'no-phishing'
    response = client.post(
        '/api/simulaciones/registrar-respuesta/',
        data=json.dumps({
            'simulacion_id': sim_id,
            'respuesta_usuario': respuesta_usuario
        }),
        content_type='application/json',
        HTTP_X_CSRFTOKEN='dummy'
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Status {response.status_code}")
        print(f"Response: {response.content.decode()[:200]}")
        return False
    
    resultado1 = response.json()
    print(f"[OK] Response registered")
    print(f"     User answered: {resultado1['respuesta_usuario']}")
    print(f"     Real answer: {'phishing' if resultado1['es_phishing_real'] else 'no-phishing'}")
    print(f"     Result: {resultado1['resultado']}")
    print(f"     Was correct: {resultado1['fue_correcto']}")
    
    if not resultado1['fue_correcto']:
        print("[FAIL] Expected correct answer!")
        return False
    
    # Step 3: Load another and register wrong response
    print("\n[3/5] Loading another simulation...")
    print("-" * 70)
    
    response = client.get('/api/simulaciones/obtener-aleatoria/')
    if response.status_code != 200:
        print(f"[FAIL] Status {response.status_code}")
        return False
    
    sim2 = response.json()
    print(f"[OK] Loaded simulation {sim2['simulacion_id']}")
    print(f"     Is phishing: {sim2['es_phishing']}")
    sim2_id = sim2['simulacion_id']
    es_phishing_real2 = sim2['es_phishing']
    
    # Register wrong response
    print("\n[4/5] Registering WRONG response...")
    print("-" * 70)
    
    respuesta_incorrecta = 'no-phishing' if es_phishing_real2 else 'phishing'
    response = client.post(
        '/api/simulaciones/registrar-respuesta/',
        data=json.dumps({
            'simulacion_id': sim2_id,
            'respuesta_usuario': respuesta_incorrecta
        }),
        content_type='application/json',
        HTTP_X_CSRFTOKEN='dummy'
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Status {response.status_code}")
        return False
    
    resultado2 = response.json()
    print(f"[OK] Response registered")
    print(f"     User answered: {resultado2['respuesta_usuario']}")
    print(f"     Real answer: {'phishing' if resultado2['es_phishing_real'] else 'no-phishing'}")
    print(f"     Result: {resultado2['resultado']}")
    print(f"     Was correct: {resultado2['fue_correcto']}")
    
    if resultado2['fue_correcto']:
        print("[FAIL] Expected incorrect answer!")
        return False
    
    # Step 5: Verify database
    print("\n[5/5] Checking database state...")
    print("-" * 70)
    
    sim_obj1 = Simulacion.objects.get(id=sim_id)
    sim_obj2 = Simulacion.objects.get(id=sim2_id)
    
    print(f"[OK] Simulation 1: resultado = {sim_obj1.resultado}")
    print(f"     Simulation 2: resultado = {sim_obj2.resultado}")
    
    print("\n" + "=" * 70)
    print("All workflow tests passed!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
