#!/usr/bin/env python
"""
Análisis detallado de por qué falla la extracción de proceso_ataque.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

def analyze_failures():
    """Analizar artículos que NO tienen proceso_ataque"""
    print("\n" + "=" * 80)
    print("ANÁLISIS DE FALLOS EN EXTRACCIÓN DE PROCESO_ATAQUE")
    print("=" * 80)

    # Total
    total = Articulo.objects.count()
    print(f"\nTotal de artículos: {total}")

    # Con proceso_ataque
    with_process = Articulo.objects.exclude(proceso_ataque='').count()
    without_process = total - with_process

    print(f"Con proceso_ataque: {with_process}")
    print(f"SIN proceso_ataque: {without_process}")

    if without_process == 0:
        print("✓ TODOS los artículos tienen proceso_ataque!")
        return

    print(f"\n{'='*80}")
    print("ARTÍCULOS SIN PROCESO_ATAQUE:")
    print(f"{'='*80}")

    # Mostrar detalles de artículos sin proceso
    for article in Articulo.objects.filter(proceso_ataque=''):
        print(f"\n[{article.id}] {article.fuente}")
        print(f"Título: {article.titulo[:70]}")
        print(f"\nCampos disponibles:")
        print(f"  • Contenido: {len(article.contenido)} chars")
        print(f"  • Proceso: {len(article.proceso_ataque)} chars (VACÍO)")
        print(f"  • Secuencia: {len(article.secuencia_ataque)} chars")
        print(f"  • Recomendaciones: {len(article.recomendaciones)} chars")
        print(f"  • Ejemplos: {len(article.ejemplos_ataque)} chars")
        print(f"  • Origen: {len(article.origen_ataque)} chars")
        print(f"  • Objetivo: {len(article.objetivo_ataque)} chars")
        print(f"  • Canal: {article.canal_ataque}")

        # Analizar contenido para ver qué SÍ tiene
        content_lower = article.contenido.lower()
        has_attack_keywords = any(kw in content_lower for kw in [
            'atacante', 'ataque', 'envía', 'redirige', 'suplanta',
            'captura', 'robo', 'malicioso', 'falso', 'fraudulento',
            'phishing', 'smishing', 'vishing'
        ])

        print(f"\n  Análisis del contenido:")
        print(f"  • Tiene palabras de ataque: {'SÍ' if has_attack_keywords else 'NO'}")
        print(f"  • Primeras 200 chars: {article.contenido[:200]}...")

    print(f"\n{'='*80}")
    print("ARTÍCULOS CON PROCESO_ATAQUE:")
    print(f"{'='*80}")

    # Mostrar ejemplo de artículo EXITOSO
    for article in Articulo.objects.exclude(proceso_ataque=''):
        print(f"\n[{article.id}] {article.fuente}")
        print(f"Título: {article.titulo[:70]}")
        print(f"Proceso ({len(article.proceso_ataque)} chars):")
        print(f"  {article.proceso_ataque[:200]}...")
        break  # Solo el primero

def main():
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║  ANÁLISIS DE FALLOS EN EXTRACCIÓN                                         ║")
    print("╚" + "=" * 78 + "╝")

    analyze_failures()

if __name__ == '__main__':
    main()
