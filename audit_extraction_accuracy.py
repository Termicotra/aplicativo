#!/usr/bin/env python
"""
AUDITORÍA MANUAL: Comparar campos extraídos vs contenido real de artículos.
Descarga cada artículo y valida que la extracción tenga sentido.
"""
import os
import django
import re
from urllib.request import Request, urlopen
from urllib.error import URLError
from socket import timeout as socket_timeout

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

def _fetch_content(url: str, timeout: int = 15) -> str:
    """Descargar contenido HTML de una URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = Request(url, headers=headers)
        with urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except (URLError, socket_timeout, Exception) as e:
        return f"ERROR: {type(e).__name__}"

def _extract_text_from_html(html: str) -> str:
    """Extraer texto limpio de HTML"""
    # Eliminar scripts, styles
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.IGNORECASE | re.DOTALL)
    # Eliminar tags HTML
    html = re.sub(r'<[^>]+>', ' ', html)
    # Limpiar espacios
    html = re.sub(r'\s+', ' ', html).strip()
    return html[:5000]

def validate_field(field_name: str, extracted_value: str, original_content: str) -> dict:
    """
    Validar si el campo extraído tiene sentido en el contenido original.
    Retorna análisis detallado.
    """
    if not extracted_value or len(extracted_value) < 20:
        return {
            'field': field_name,
            'status': 'VACIO',
            'issue': 'Campo vacío o muy corto',
            'extracted': extracted_value[:80] if extracted_value else '(vacío)',
        }

    # Normalizar para búsqueda (sin acentos)
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[áà]', 'a', text)
        text = re.sub(r'[éè]', 'e', text)
        text = re.sub(r'[íì]', 'i', text)
        text = re.sub(r'[óò]', 'o', text)
        text = re.sub(r'[úù]', 'u', text)
        return text

    extracted_norm = normalize(extracted_value)
    content_norm = normalize(original_content)

    # Extraer palabras clave del campo extraído (palabras >4 caracteres)
    keywords = [word for word in extracted_norm.split() if len(word) > 4]

    # Contar cuántas palabras clave aparecen en el contenido original
    found_keywords = sum(1 for kw in keywords if kw in content_norm)
    keyword_match_rate = (found_keywords / len(keywords) * 100) if keywords else 0

    # Analizar si las primeras palabras están en el original
    first_50_words = ' '.join(keywords[:10])
    first_words_found = first_50_words in content_norm or any(kw in content_norm for kw in keywords[:3])

    # Determinar status
    if keyword_match_rate >= 70:
        status = 'OK'
        issue = f"Concordancia: {keyword_match_rate:.0f}% de palabras encontradas"
    elif keyword_match_rate >= 40:
        status = 'PARCIAL'
        issue = f"Baja concordancia: solo {keyword_match_rate:.0f}% de palabras encontradas"
    else:
        status = 'FUERA DE CONTEXTO'
        issue = f"Muy baja concordancia: {keyword_match_rate:.0f}% de palabras encontradas"

    return {
        'field': field_name,
        'status': status,
        'issue': issue,
        'extracted': extracted_value[:100],
        'match_rate': keyword_match_rate,
        'keywords_found': found_keywords,
        'total_keywords': len(keywords),
    }

def main():
    articles = Articulo.objects.all()
    print("\n" + "=" * 90)
    print("AUDITORÍA DE EXTRACCIÓN: Comparar campos vs contenido original")
    print("=" * 90)

    total_articles = articles.count()
    print(f"\nAuditando {total_articles} artículos...")

    issues_by_field = {}
    articles_with_issues = []

    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{total_articles}] {article.titulo[:70]}")
        print(f"  URL: {article.url[:80]}")

        # Descargar contenido original
        html = _fetch_content(article.url, timeout=10)
        if html.startswith("ERROR"):
            print(f"  ⚠️  No se pudo descargar: {html}")
            continue

        original_text = _extract_text_from_html(html)

        # Validar cada campo
        fields_to_validate = {
            'proceso_ataque': article.proceso_ataque,
            'secuencia_ataque': article.secuencia_ataque,
            'ejemplos_ataque': article.ejemplos_ataque,
            'recomendaciones': article.recomendaciones,
            'origen_ataque': article.origen_ataque,
            'objetivo_ataque': article.objetivo_ataque,
        }

        article_issues = []
        for field_name, extracted_value in fields_to_validate.items():
            result = validate_field(field_name, extracted_value, original_text)

            if result['status'] != 'OK':
                article_issues.append(result)
                if field_name not in issues_by_field:
                    issues_by_field[field_name] = []
                issues_by_field[field_name].append(result)

            # Mostrar resultado
            status_symbol = "[OK]" if result['status'] == 'OK' else "[FAIL]"
            print(f"  {status_symbol} {field_name:20} | {result['status']:15} | {result['issue']}")

        if article_issues:
            articles_with_issues.append({
                'article_id': article.id,
                'title': article.titulo[:70],
                'url': article.url,
                'issues': article_issues,
            })

    # RESUMEN
    print("\n" + "=" * 90)
    print("RESUMEN DE PROBLEMAS ENCONTRADOS")
    print("=" * 90)

    print(f"\nTotal artículos auditados: {total_articles}")
    print(f"Artículos con problemas: {len(articles_with_issues)}")

    print(f"\nProblemas por campo:")
    for field_name, issues in sorted(issues_by_field.items()):
        bad_count = len([i for i in issues if i['status'] != 'OK'])
        print(f"  {field_name}: {bad_count} problemas")

    if articles_with_issues:
        print("\n" + "=" * 90)
        print("DETALLE DE PROBLEMAS")
        print("=" * 90)

        for article_info in articles_with_issues[:5]:  # Mostrar primeros 5
            print(f"\n[{article_info['article_id']}] {article_info['title']}")
            print(f"URL: {article_info['url']}")

            for issue in article_info['issues']:
                print(f"\n  ✗ {issue['field']}:")
                print(f"    Status: {issue['status']}")
                print(f"    Issue: {issue['issue']}")
                print(f"    Extractado: {issue['extracted'][:80]}...")

if __name__ == '__main__':
    main()
