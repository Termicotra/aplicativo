#!/usr/bin/env python
"""
Re-ejecutar ingesta con palabras clave expandidas.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import run_weekly_ingestion
from articulos.models import Articulo

print("\n" + "=" * 80)
print("RE-EJECUTAR INGESTA CON PALABRAS CLAVE EXPANDIDAS")
print("=" * 80)

print(f"\nArticulos en BD antes: {Articulo.objects.count()}")

print("\nEjecutando ingesta...")
result = run_weekly_ingestion(max_items_per_source=20)

print(f"\nArticulos en BD despues: {Articulo.objects.count()}")

print("\nResultado de ingesta:")
for key, value in result.items():
    print(f"  {key}: {value}")
