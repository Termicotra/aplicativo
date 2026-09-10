#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from simulaciones.models import Simulacion

FRAUD_KEYWORDS = [
    'dominio falso', 'false domain', 'fake domain',
    'urgencia artificial', 'artificial urgency', 'urgencia',
    'amenaza', 'threat', 'amenazante',
    'phishing', 'estafa', 'fraud', 'fraude',
    'robo', 'theft', 'steal',
    'suplanta', 'suplantación', 'impersonat',
    'intento de robo', 'intento de estafa',
    'credenciales', 'credentials', 'contraseña',
    'solicita datos', 'requests data',
    'presión', 'pressure', 'presion',
]

print("=== COHERENCE VERIFICATION ===\n")

legitimate_sims = Simulacion.objects.filter(es_phishing=False)
phishing_sims = Simulacion.objects.filter(es_phishing=True)

print(f"Total: {Simulacion.objects.count()}")
print(f"  Phishing: {phishing_sims.count()}")
print(f"  Legitimate: {legitimate_sims.count()}\n")

incoherent = []
for sim in legitimate_sims:
    feedback_lower = sim.feedback.lower()
    found = [kw for kw in FRAUD_KEYWORDS if kw in feedback_lower]
    if found:
        incoherent.append({'id': sim.id, 'keywords': found, 'feedback': sim.feedback[:80]})

if incoherent:
    print(f"[FAIL] {len(incoherent)}/{legitimate_sims.count()} incoherent:")
    for item in incoherent[:3]:
        print(f"  ID {item['id']}: {item['keywords']}")
else:
    print(f"[OK] All {legitimate_sims.count()} legitimate simulations coherent")

print(f"\n[CHECK] {sum(1 for s in phishing_sims if any(kw in s.feedback.lower() for kw in FRAUD_KEYWORDS))}/{phishing_sims.count()} phishing describe fraud")

sys.exit(0 if not incoherent else 1)
