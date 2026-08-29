#!/usr/bin/env python
"""
Test del nuevo código de ingestion con enfoque phishing-puro.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import run_weekly_ingestion
from articulos.models import Articulo

print("\n" + "=" * 80)
print("TEST: INGESTA CON NUEVO CÓDIGO ENFOCADO EN PHISHING PURO")
print("=" * 80)

# Ejecutar ingesta
print("\nEjecutando ingesta...")
result = run_weekly_ingestion(max_items_per_source=20)

# Resultados
print("\n" + "=" * 80)
print("RESULTADOS")
print("=" * 80)

total_saved = result.get('total_saved', 0)
total_processed = result.get('total_processed', 0)
cert_created = result.get('CERT_created', 0)
cert_processed = result.get('CERT_processed', 0)
abc_created = result.get('ABC_created', 0)
abc_processed = result.get('ABC_processed', 0)

print(f"\nTOTAL:")
print(f"  Artículos creados: {total_saved}")
print(f"  Artículos procesados: {total_processed}")
print(f"  Artículos rechazados: {total_processed - total_saved}")

print(f"\nCERT Paraguay:")
print(f"  Creados: {cert_created}")
print(f"  Procesados: {cert_processed}")

print(f"\nABC Color:")
print(f"  Creados: {abc_created}")
print(f"  Procesados: {abc_processed}")

# Validar proceso_ataque
print("\n" + "=" * 80)
print("VALIDACIÓN: PROCESO_ATAQUE (Debe estar presente)")
print("=" * 80)

all_articles = Articulo.objects.all()
with_process = all_articles.exclude(proceso_ataque='').count()
without_process = all_articles.count() - with_process
process_precision = (with_process / all_articles.count() * 100) if all_articles.count() > 0 else 0

print(f"\nTotal artículos: {all_articles.count()}")
print(f"Con proceso_ataque: {with_process}")
print(f"Sin proceso_ataque: {without_process}")
print(f"Precisión: {process_precision:.1f}%")

# Mostrar ejemplo
if all_articles.exists():
    print("\n" + "=" * 80)
    print("EJEMPLO DE ARTÍCULO EXTRAÍDO")
    print("=" * 80)
    article = all_articles.first()
    print(f"\n[{article.id}] {article.titulo[:80]}")
    print(f"Fuente: {article.fuente}")
    print(f"Canal: {article.canal_ataque}")
    print(f"\nProceso ({len(article.proceso_ataque)} chars):")
    print(f"  {article.proceso_ataque[:200]}...")
    print(f"\nSecuencia ({len(article.secuencia_ataque)} chars):")
    print(f"  {article.secuencia_ataque[:200]}...")
    print(f"\nEjemplos ({len(article.ejemplos_ataque)} chars):")
    print(f"  {article.ejemplos_ataque[:200]}...")

print("\n" + "=" * 80)
print("✅ INGESTA COMPLETADA")
print("=" * 80)
