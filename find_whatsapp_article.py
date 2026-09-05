#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

# Buscar el artículo
articles = Articulo.objects.all()

print("Buscando artículos con 'verificacion en dos pasos' o 'WhatsApp'...")

found_articles = []
for article in articles:
    content_lower = article.contenido.lower()
    if 'verificacion en dos pasos' in content_lower or ('whatsapp' in content_lower and 'pin' in content_lower):
        found_articles.append(article)

print(f"\nEncontrados {len(found_articles)} artículos\n")

for article in found_articles:
    print("=" * 90)
    print(f"[{article.id}] {article.titulo}")
    print("=" * 90)

    print(f"\n[RECOMENDACIONES] ({len(article.recomendaciones)} chars):")
    print(article.recomendaciones[:500])

    print(f"\n[CONTENIDO - Buscando 'se recomienda']:")
    content_lower = article.contenido.lower()

    # Encontrar "se recomienda"
    idx = content_lower.find('se recomienda')
    if idx >= 0:
        print(f"Encontrado en posición {idx}:")
        print(article.contenido[max(0, idx-50):min(len(article.contenido), idx+400)])
    else:
        print("No encontrado 'se recomienda'")

        # Buscar "verificacion en dos pasos"
        idx = content_lower.find('verificacion en dos pasos')
        if idx >= 0:
            print(f"\nEncontrado 'verificacion en dos pasos' en posición {idx}:")
            print(article.contenido[max(0, idx-50):min(len(article.contenido), idx+500)])

    print("\n")
