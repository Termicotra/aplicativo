#!/usr/bin/env python
"""
Verify that all simulations have coherent feedback.
- Phishing simulations should describe fraud characteristics
- Legitimate simulations should NEVER describe fraud characteristics
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from simulaciones.models import Simulacion

# Fraud keywords that should NEVER appear in legitimate feedback
FRAUD_KEYWORDS = [
    'dominio falso', 'false domain', 'fake domain',
    'urgencia artificial', 'artificial urgency', 'urgencia',
    'amenaza', 'threat', 'amenazante',
    'phishing', 'estafa', 'fraud', 'fraude',
    'robo', 'theft', 'steal',
    'suplanta', 'suplantación', 'impersonat',
    'intento de robo', 'intento de estafa',
    'credenciales', 'credentials', 'contraseña', 'password',
    'solicita datos', 'requests data',
    'presión', 'pressure', 'presion',
]

def check_coherence():
    print("=== COHERENCE VERIFICATION ===\n")

    # Check legitimate simulations
    legitimate_sims = Simulacion.objects.filter(es_phishing=False)
    phishing_sims = Simulacion.objects.filter(es_phishing=True)

    print(f"Total simulations: {Simulacion.objects.count()}")
    print(f"  - Phishing: {phishing_sims.count()}")
    print(f"  - Legitimate: {legitimate_sims.count()}\n")

    # Check legitimate feedback
    incoherent = []
    for sim in legitimate_sims:
        feedback_lower = sim.feedback.lower()
        found_keywords = [kw for kw in FRAUD_KEYWORDS if kw in feedback_lower]
        if found_keywords:
            incoherent.append({
                'id': sim.id,
                'keywords': found_keywords,
                'feedback_sample': sim.feedback[:100]
            })

    if incoherent:
        print(f"[FAIL] {len(incoherent)}/{legitimate_sims.count()} legitimate simulations have incoherent feedback:")
        for item in incoherent[:5]:  # Show first 5
            print(f"  ID {item['id']}: {item['keywords']}")
            print(f"    Feedback: {item['feedback_sample']}...")
        if len(incoherent) > 5:
            print(f"  ... and {len(incoherent) - 5} more")
    else:
        print(f"[OK] All {legitimate_sims.count()} legitimate simulations have coherent feedback")

    # Quick check of phishing feedback (should describe fraud)
    phishing_good = sum(1 for sim in phishing_sims if any(kw in sim.feedback.lower() for kw in FRAUD_KEYWORDS))
    print(f"\n[CHECK] {phishing_good}/{phishing_sims.count()} phishing simulations describe fraud characteristics")

    # Summary
    print(f"\n=== RESULT ===")
    if not incoherent:
        print("[OK] PASSED - All simulations are coherent")
        return 0
    else:
        print(f"[FAIL] FAILED - {len(incoherent)} incoherent legitimate simulations")
        return 1

if __name__ == '__main__':
    sys.exit(check_coherence())
