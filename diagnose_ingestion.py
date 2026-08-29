#!/usr/bin/env python
"""
Diagnóstico de por qué falla la ingesta real.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import (
    scrape_abc_color,
    scrape_cert_py,
    run_weekly_ingestion,
    _passes_article_filters,
)
from articulos.models import Articulo

print("\n" + "=" * 80)
print("DIAGNOSTICO: POR QUE FALLA LA INGESTA")
print("=" * 80)

# Verificar BD antes
print(f"\nArticulos en BD antes: {Articulo.objects.count()}")

# Intentar ingesta simple
print("\nIntentando scrape desde ABC...")
try:
    abc_articles = scrape_abc_color(max_items=5)
    print(f"  ABC retorno: {len(abc_articles) if abc_articles else 0} articulos")

    # Verificar cuáles pasan los filtros
    if abc_articles:
        passed = sum(1 for art in abc_articles if _passes_article_filters(art))
        print(f"  Pasaron filtros: {passed}/{len(abc_articles)}")
        for i, art in enumerate(abc_articles[:2]):
            titulo = art.get('titulo', 'SIN TITULO')[:60]
            print(f"    [{i+1}] {titulo}")
except Exception as e:
    print(f"  ERROR ABC: {type(e).__name__}: {e}")

print("\nIntentando scrape desde CERT...")
try:
    cert_articles = scrape_cert_py(max_items=5)
    print(f"  CERT retorno: {len(cert_articles) if cert_articles else 0} articulos")

    # Verificar cuáles pasan los filtros
    if cert_articles:
        passed = sum(1 for art in cert_articles if _passes_article_filters(art))
        print(f"  Pasaron filtros: {passed}/{len(cert_articles)}")
        for i, art in enumerate(cert_articles[:2]):
            titulo = art.get('titulo', 'SIN TITULO')[:60]
            print(f"    [{i+1}] {titulo}")
except Exception as e:
    print(f"  ERROR CERT: {type(e).__name__}: {e}")

# Intentar run_weekly_ingestion
print("\nIntentando run_weekly_ingestion...")
try:
    result = run_weekly_ingestion(max_items_per_source=5)
    print(f"  Resultado: {result}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")

# Verificar BD después
print(f"\nArticulos en BD despues: {Articulo.objects.count()}")

print("\n" + "=" * 80)
