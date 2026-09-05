#!/usr/bin/env python
"""
VALIDAR que las correcciones funcionaron.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

def validate_no_duplicates():
    """Verificar que ejemplos_ataque no sea duplicado de proceso_ataque"""
    articles = Articulo.objects.exclude(proceso_ataque='').exclude(ejemplos_ataque='')

    duplicates = 0
    for article in articles:
        if article.proceso_ataque.lower() == article.ejemplos_ataque.lower():
            duplicates += 1
            print(f"[DUPLICADO] Articulo {article.id}: {article.titulo[:50]}")

    return duplicates

def validate_sequence_markers():
    """Verificar que secuencia_ataque tenga marcadores de secuencia"""
    articles = Articulo.objects.exclude(secuencia_ataque='')

    sequence_markers = ['primero', 'luego', 'despues', 'paso', 'recibe', 'hace clic', 'ingresa', 'es redirigido']

    without_markers = 0
    for article in articles:
        seq_lower = article.secuencia_ataque.lower()
        has_marker = any(marker in seq_lower for marker in sequence_markers)

        if not has_marker and len(article.secuencia_ataque) > 100:
            without_markers += 1

    return without_markers, len(articles)

def validate_origin_target():
    """Verificar que origen/objetivo tengan contenido relevante"""
    articles = Articulo.objects.all()

    origin_keywords = ['atacante', 'delincuente', 'estafador', 'ciberdelincuente', 'grupo', 'banda']
    target_keywords = ['usuario', 'cliente', 'victima', 'persona', 'empresa', 'banco', 'institucion', 'empleado']

    bad_origins = 0
    bad_targets = 0

    for article in articles:
        # Verificar origen
        if article.origen_ataque:
            origin_lower = article.origen_ataque.lower()
            has_origin = any(kw in origin_lower for kw in origin_keywords)
            if not has_origin:
                bad_origins += 1

        # Verificar objetivo
        if article.objetivo_ataque:
            target_lower = article.objetivo_ataque.lower()
            has_target = any(kw in target_lower for kw in target_keywords)
            if not has_target:
                bad_targets += 1

    return bad_origins, bad_targets, len(articles)

def main():
    total = Articulo.objects.count()

    if total == 0:
        print("\n[!] Sin articulos en BD aun. Ingesta sigue en progreso...")
        return

    print("\n" + "=" * 80)
    print("VALIDACION DE CORRECCIONES")
    print("=" * 80)

    print(f"\nTotal articulos: {total}")

    # Validar duplicados
    print("\n[1] Duplicados (ejemplos_ataque = proceso_ataque):")
    duplicates = validate_no_duplicates()
    if duplicates == 0:
        print("    [OK] Sin duplicados encontrados!")
    else:
        print(f"    [ERROR] {duplicates} duplicados encontrados")

    # Validar secuencia con marcadores
    print("\n[2] Secuencia sin marcadores (>100 chars):")
    without_markers, seq_count = validate_sequence_markers()
    if without_markers == 0:
        print(f"    [OK] Todas las secuencias tienen marcadores")
    else:
        print(f"    [ERROR] {without_markers}/{seq_count} sin marcadores")

    # Validar origen/objetivo
    print("\n[3] Origen/Objetivo sin palabras relevantes:")
    bad_origins, bad_targets, total_articles = validate_origin_target()
    print(f"    Origenes sin palabras phishing: {bad_origins}/{total_articles}")
    print(f"    Objetivos sin palabras phishing: {bad_targets}/{total_articles}")

    if bad_origins == 0 and bad_targets == 0:
        print("    [OK] Todos tienen contenido relevante")

    print("\n" + "=" * 80)
    if duplicates == 0 and without_markers == 0 and bad_origins == 0 and bad_targets == 0:
        print("✓ TODAS LAS CORRECCIONES VALIDADAS")
    else:
        print("[!] Aun hay problemas por resolver")

if __name__ == '__main__':
    main()
