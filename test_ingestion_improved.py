#!/usr/bin/env python
"""
Script de prueba para validar las mejoras en ingestion.py
Ejecuta la ingestion y valida la calidad de extracción
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aplicativo.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"⚠ Django setup warning (might be OK if testing locally): {e}")

from articulos.ingestion import scrape_cert_py, scrape_abc_color

def validate_extraction(articles: list[dict]) -> dict:
    """Validar la calidad de extracción de artículos"""
    stats = {
        'total': len(articles),
        'with_clean_title': 0,
        'with_process': 0,
        'with_sequence': 0,
        'with_recommendations': 0,
        'with_examples': 0,
        'with_origin': 0,
        'with_target': 0,
        'with_channel': 0,
        'clean_quality': [],
        'avg_process_len': 0,
        'avg_sequence_len': 0,
        'avg_recommendations_len': 0,
    }

    process_lengths = []
    sequence_lengths = []
    recommendations_lengths = []

    for article in articles:
        # Check title quality
        title = str(article.get('titulo', '')).strip()
        if title and len(title) > 10:
            stats['with_clean_title'] += 1

        # Check extracted fields
        proceso = str(article.get('proceso_ataque', '')).strip()
        secuencia = str(article.get('secuencia_ataque', '')).strip()
        recomendaciones = str(article.get('recomendaciones', '')).strip()
        ejemplos = str(article.get('ejemplos_ataque', '')).strip()
        origen = str(article.get('origen_ataque', '')).strip()
        objetivo = str(article.get('objetivo_ataque', '')).strip()
        canal = str(article.get('canal_ataque', '')).strip()

        if proceso:
            stats['with_process'] += 1
            process_lengths.append(len(proceso))
        if secuencia:
            stats['with_sequence'] += 1
            sequence_lengths.append(len(secuencia))
        if recomendaciones:
            stats['with_recommendations'] += 1
            recommendations_lengths.append(len(recomendaciones))
        if ejemplos:
            stats['with_examples'] += 1
        if origen:
            stats['with_origin'] += 1
        if objetivo:
            stats['with_target'] += 1
        if canal and canal != 'indefinido':
            stats['with_channel'] += 1

        # Quality check: text shouldn't contain common noise patterns
        noise_patterns = [
            'lea más',
            'ver más',
            'siguiente',
            'anterior',
            'comentarios',
            'compartir',
        ]

        full_text = f"{title} {proceso} {secuencia} {recomendaciones}".lower()
        has_noise = any(pattern in full_text for pattern in noise_patterns)

        quality = 'CLEAN' if not has_noise else 'HAS_NOISE'
        stats['clean_quality'].append({
            'titulo': title[:60],
            'quality': quality,
            'proceso_len': len(proceso),
            'secuencia_len': len(secuencia),
            'recomendaciones_len': len(recomendaciones),
        })

    if process_lengths:
        stats['avg_process_len'] = sum(process_lengths) / len(process_lengths)
    if sequence_lengths:
        stats['avg_sequence_len'] = sum(sequence_lengths) / len(sequence_lengths)
    if recommendations_lengths:
        stats['avg_recommendations_len'] = sum(recommendations_lengths) / len(recommendations_lengths)

    return stats


def main():
    print("\n" + "=" * 80)
    print("TESTING INGESTION.PY IMPROVEMENTS")
    print("=" * 80)

    print("\n[1/2] Scraping CERT Paraguay...")
    try:
        cert_articles = scrape_cert_py(max_items=5)
        print(f"✓ Got {len(cert_articles)} articles from CERT")
    except Exception as e:
        print(f"✗ CERT scraping failed: {e}")
        cert_articles = []

    print("\n[2/2] Scraping ABC Color...")
    try:
        abc_articles = scrape_abc_color(max_items=5)
        print(f"✓ Got {len(abc_articles)} articles from ABC")
    except Exception as e:
        print(f"✗ ABC scraping failed: {e}")
        abc_articles = []

    all_articles = cert_articles + abc_articles

    if not all_articles:
        print("\n⚠ No articles extracted. This might be normal if sites are down.")
        print("  Check if cert.gov.py and abc.com.py are accessible.")
        return

    print("\n" + "=" * 80)
    print("EXTRACTION QUALITY ANALYSIS")
    print("=" * 80)

    stats = validate_extraction(all_articles)

    print(f"\nTotal articles extracted: {stats['total']}")
    print(f"Articles with clean title: {stats['with_clean_title']}/{stats['total']}")
    print(f"Articles with process extraction: {stats['with_process']}/{stats['total']}")
    print(f"Articles with sequence extraction: {stats['with_sequence']}/{stats['total']}")
    print(f"Articles with recommendations: {stats['with_recommendations']}/{stats['total']}")
    print(f"Articles with examples: {stats['with_examples']}/{stats['total']}")
    print(f"Articles with origin: {stats['with_origin']}/{stats['total']}")
    print(f"Articles with target: {stats['with_target']}/{stats['total']}")
    print(f"Articles with channel: {stats['with_channel']}/{stats['total']}")

    print(f"\nAverage text lengths:")
    print(f"  Process: {stats['avg_process_len']:.0f} chars")
    print(f"  Sequence: {stats['avg_sequence_len']:.0f} chars")
    print(f"  Recommendations: {stats['avg_recommendations_len']:.0f} chars")

    print(f"\n" + "=" * 80)
    print("SAMPLE ARTICLES (first 3)")
    print("=" * 80)

    for idx, article in enumerate(all_articles[:3], 1):
        print(f"\n[{idx}] {article.get('fuente', 'Unknown')}")
        print(f"Title: {article.get('titulo', '')[:70]}")
        print(f"Process ({len(article.get('proceso_ataque', ''))} chars): {article.get('proceso_ataque', '')[:100]}...")
        print(f"Sequence ({len(article.get('secuencia_ataque', ''))} chars): {article.get('secuencia_ataque', '')[:100]}...")
        print(f"Recommendations ({len(article.get('recomendaciones', ''))} chars): {article.get('recomendaciones', '')[:100]}...")
        print(f"Channel: {article.get('canal_ataque', 'undefined')}")

    print(f"\n" + "=" * 80)
    print("QUALITY SUMMARY")
    print("=" * 80)

    clean_count = sum(1 for q in stats['clean_quality'] if q['quality'] == 'CLEAN')
    print(f"\nArticles without noise patterns: {clean_count}/{len(stats['clean_quality'])}")

    avg_extraction_score = (
        (stats['with_process'] + stats['with_sequence'] + stats['with_recommendations'] + stats['with_examples']) /
        (stats['total'] * 4) * 100
    ) if stats['total'] > 0 else 0

    print(f"Average extraction completeness: {avg_extraction_score:.1f}%")

    if avg_extraction_score >= 60:
        print("\n✓ IMPROVEMENT VALIDATED: Extraction quality is good!")
    elif avg_extraction_score >= 40:
        print("\n⚠ IMPROVEMENT PARTIAL: Some fields need more work")
    else:
        print("\n✗ IMPROVEMENT NEEDED: Extraction still has issues")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
