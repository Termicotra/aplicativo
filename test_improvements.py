#!/usr/bin/env python
"""
Script para testear las mejoras:
1. Limpiar BD
2. Ejecutar ingestion mejorada
3. Verificar resultados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo
from articulos.ingestion import scrape_cert_py, scrape_abc_color
from django.db.models import Q

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def clear_articles():
    """Limpiar tabla de artículos"""
    print_header("PASO 1: LIMPIAR BASE DE DATOS")

    count = Articulo.objects.count()
    print(f"\nArticulos antes: {count}")

    if count > 0:
        Articulo.objects.all().delete()
        print(f"✓ Eliminados: {count} artículos")

    print(f"Articulos después: {Articulo.objects.count()}")

def run_ingestion():
    """Ejecutar la ingestion mejorada"""
    print_header("PASO 2: EJECUTAR INGESTION MEJORADA")

    cert_articles = []
    abc_articles = []

    print("\n[1/2] Scrapeando CERT Paraguay...")
    try:
        cert_articles = scrape_cert_py(max_items=5)
        print(f"✓ Obtenidos {len(cert_articles)} artículos de CERT")
    except Exception as e:
        print(f"✗ Error en CERT: {e}")

    print("\n[2/2] Scrapeando ABC Color...")
    try:
        abc_articles = scrape_abc_color(max_items=5)
        print(f"✓ Obtenidos {len(abc_articles)} artículos de ABC")
    except Exception as e:
        print(f"✗ Error en ABC: {e}")

    total = len(cert_articles) + len(abc_articles)
    print(f"\nTotal extraído: {total} artículos")

    return cert_articles + abc_articles

def analyze_extraction(articles):
    """Analizar calidad de extracción"""
    print_header("PASO 3: VALIDAR CALIDAD DE EXTRACCIÓN")

    if not articles:
        print("⚠ Sin artículos para analizar")
        return

    print(f"\nTotal de artículos: {len(articles)}")

    # Analizar campos
    with_title = sum(1 for a in articles if a.get('titulo', '').strip())
    with_content = sum(1 for a in articles if a.get('contenido', '').strip())
    with_process = sum(1 for a in articles if a.get('proceso_ataque', '').strip())
    with_sequence = sum(1 for a in articles if a.get('secuencia_ataque', '').strip())
    with_recommendations = sum(1 for a in articles if a.get('recomendaciones', '').strip())
    with_examples = sum(1 for a in articles if a.get('ejemplos_ataque', '').strip())
    with_channel = sum(1 for a in articles if a.get('canal_ataque', 'indefinido').strip() != 'indefinido')

    print(f"\n✓ Títulos: {with_title}/{len(articles)}")
    print(f"✓ Contenido: {with_content}/{len(articles)}")
    print(f"✓ Proceso de ataque: {with_process}/{len(articles)}")
    print(f"✓ Secuencia: {with_sequence}/{len(articles)}")
    print(f"✓ Recomendaciones: {with_recommendations}/{len(articles)}")
    print(f"✓ Ejemplos: {with_examples}/{len(articles)}")
    print(f"✓ Canal detectado: {with_channel}/{len(articles)}")

    # Medir limpieza (ausencia de ruido)
    noise_indicators = ['lea más', 'ver más', 'siguiente', 'anterior', 'comentarios']
    articles_with_noise = 0

    for article in articles:
        full_text = f"{article.get('titulo', '')} {article.get('contenido', '')}"
        if any(indicator in full_text.lower() for indicator in noise_indicators):
            articles_with_noise += 1

    noise_percentage = (articles_with_noise / len(articles)) * 100 if articles else 0
    print(f"\n⚠ Artículos con potencial ruido: {articles_with_noise}/{len(articles)} ({noise_percentage:.1f}%)")
    print(f"✓ Limpieza: {100 - noise_percentage:.1f}%")

    # Mostrar ejemplos
    print(f"\n" + "=" * 80)
    print("EJEMPLOS DE ARTÍCULOS EXTRAÍDOS:")
    print("=" * 80)

    for idx, article in enumerate(articles[:3], 1):
        print(f"\n[{idx}] {article.get('fuente', 'Unknown')}")
        print(f"    Título: {article.get('titulo', '')[:70]}")
        print(f"    Contenido (chars): {len(article.get('contenido', ''))}")
        print(f"    Proceso ataque (chars): {len(article.get('proceso_ataque', ''))}")
        print(f"    Secuencia ataque (chars): {len(article.get('secuencia_ataque', ''))}")
        print(f"    Recomendaciones (chars): {len(article.get('recomendaciones', ''))}")
        print(f"    Canal: {article.get('canal_ataque', 'indefinido')}")

def verify_database():
    """Verificar que todo se guardó en BD"""
    print_header("PASO 4: VERIFICAR BASE DE DATOS")

    total = Articulo.objects.count()
    print(f"\nTotal de artículos en BD: {total}")

    if total == 0:
        print("⚠ La BD está vacía")
        return

    # Estadísticas
    cert_count = Articulo.objects.filter(fuente='CERT Paraguay').count()
    abc_count = Articulo.objects.filter(fuente='ABC Color').count()

    print(f"  • CERT Paraguay: {cert_count}")
    print(f"  • ABC Color: {abc_count}")

    # Verificar campos llenados
    with_process = Articulo.objects.exclude(proceso_ataque='').count()
    with_sequence = Articulo.objects.exclude(secuencia_ataque='').count()
    with_recom = Articulo.objects.exclude(recomendaciones='').count()

    print(f"\nCampos completados:")
    print(f"  • Con proceso: {with_process}/{total}")
    print(f"  • Con secuencia: {with_sequence}/{total}")
    print(f"  • Con recomendaciones: {with_recom}/{total}")

    # Ejemplo de artículo
    if total > 0:
        article = Articulo.objects.first()
        print(f"\nEjemplo de artículo (ID: {article.id}):")
        print(f"  Título: {article.titulo[:60]}")
        print(f"  Fuente: {article.fuente}")
        print(f"  Proceso ({len(article.proceso_ataque)} chars): {article.proceso_ataque[:80]}...")
        print(f"  Secuencia ({len(article.secuencia_ataque)} chars): {article.secuencia_ataque[:80]}...")

def main():
    """Ejecutar todo el pipeline de testing"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║  TEST DE MEJORAS DE INGESTION                                              ║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Paso 1: Limpiar
        clear_articles()

        # Paso 2: Ingestion
        articles = run_ingestion()

        # Paso 3: Analizar
        analyze_extraction(articles)

        # Paso 4: Verificar BD
        verify_database()

        print("\n" + "=" * 80)
        print("✅ TEST COMPLETADO")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
