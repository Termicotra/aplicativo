#!/usr/bin/env python
"""Test manual del flujo de ingesta"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import scrape_abc_color, scrape_cert_py, _passes_article_filters, save_articles
from articulos.models import Articulo

print("\n" + "=" * 80)
print("TEST MANUAL DE INGESTA")
print("=" * 80)

print(f"\nArticulos en BD antes: {Articulo.objects.count()}")

# Paso 1: Scrape ABC
print("\n[1] Scraping ABC...")
abc_articles = scrape_abc_color(max_items=5)
print(f"    Scrapeados: {len(abc_articles)}")

# Paso 2: Filtrar
print("\n[2] Filtrando...")
abc_filtered = [a for a in abc_articles if _passes_article_filters(a)]
print(f"    Pasaron filtros: {len(abc_filtered)}/{len(abc_articles)}")

# Paso 3: Guardar
if abc_filtered:
    print("\n[3] Guardando...")
    result = save_articles(abc_filtered)
    print(f"    Guardados: {result}")

# Paso 4: Scrape CERT
print("\n[4] Scraping CERT...")
cert_articles = scrape_cert_py(max_items=5)
print(f"    Scrapeados: {len(cert_articles)}")

# Paso 5: Filtrar
print("\n[5] Filtrando...")
cert_filtered = [a for a in cert_articles if _passes_article_filters(a)]
print(f"    Pasaron filtros: {len(cert_filtered)}/{len(cert_articles)}")

# Paso 6: Guardar
if cert_filtered:
    print("\n[6] Guardando...")
    result = save_articles(cert_filtered)
    print(f"    Guardados: {result}")

print(f"\nArticulos en BD despues: {Articulo.objects.count()}")
print("\n" + "=" * 80)
