#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

# Buscar el artículo
articles = Articulo.objects.all()

# Buscar el que tiene "verificacion en dos pasos"
found = None
for article in articles:
    if 'verificacion en dos pasos' in article.contenido.lower() or 'whatsapp' in article.contenido.lower():
        found = article
        break

if not found:
    print("No encontrado, mostrando primer artículo")
    found = articles.first()

print("\n" + "=" * 90)
print(f"ARTICULO {found.id}: {found.titulo}")
print("=" * 90)

print(f"\n[RECOMENDACIONES] ({len(found.recomendaciones)} chars):")
print("-" * 90)
print(found.recomendaciones[:800])
print("-" * 90)

print(f"\n[PROCESO_ATAQUE] ({len(found.proceso_ataque)} chars):")
print("-" * 90)
print(found.proceso_ataque[:400])
print("-" * 90)

print(f"\n[CONTENIDO ORIGINAL] (primeros 1000 chars):")
print("-" * 90)
print(found.contenido[:1000])
print("-" * 90)

# Buscar si hay duplicación
print("\n[ANÁLISIS]:")
rec_lower = found.recomendaciones.lower()
proc_lower = found.proceso_ataque.lower()

# Verificar si recomendaciones contiene contenido de proceso
if proc_lower and rec_lower:
    # Extraer palabras comunes
    rec_words = set(rec_lower.split()[:30])  # primeras 30 palabras
    proc_words = set(proc_lower.split()[:30])
    common = rec_words & proc_words
    print(f"Palabras comunes entre recomendaciones y proceso: {common if common else 'Ninguna'}")

# Verificar si hay "se recomienda" en contenido pero no en recomendaciones
if 'se recomienda' in found.contenido.lower() and 'se recomienda' not in found.recomendaciones.lower():
    print("[!] PROBLEMA: Contenido tiene 'se recomienda' pero NO está en campo recomendaciones")

    # Encontrar dónde está
    content_lower = found.contenido.lower()
    idx = content_lower.find('se recomienda')
    print(f"\nEn contenido (posición {idx}):")
    print(found.contenido[max(0, idx-100):idx+200])
