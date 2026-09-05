#!/usr/bin/env python
"""
Análisis rápido de campos sin descargar: detectar anomalías en lo extraído.
"""
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

def analyze_field_consistency(article):
    """Analizar si los campos tienen consistencia lógica"""
    issues = []

    # 1. proceso_ataque debe contener palabras del título
    if article.proceso_ataque and article.titulo:
        titulo_words = set(re.findall(r'\b\w{4,}\b', article.titulo.lower()))
        proceso_words = set(re.findall(r'\b\w{4,}\b', article.proceso_ataque.lower()))

        common = titulo_words & proceso_words
        if len(common) < 2:
            issues.append({
                'field': 'proceso_ataque',
                'issue': f'Muy pocas palabras en común con título ({len(common)} de {len(titulo_words)})',
                'severity': 'ALTO'
            })

    # 2. secuencia_ataque debe tener palabras de secuencia (primero, luego, después, paso)
    if article.secuencia_ataque:
        sequence_markers = ['primero', 'luego', 'después', 'paso', 'entonces', 'siguiente', 'recibe', 'hace clic']
        has_markers = any(marker in article.secuencia_ataque.lower() for marker in sequence_markers)

        if not has_markers and len(article.secuencia_ataque) > 100:
            issues.append({
                'field': 'secuencia_ataque',
                'issue': 'No contiene marcadores de secuencia (primero, luego, paso, etc)',
                'severity': 'MEDIO'
            })

    # 3. ejemplos_ataque debe contener palabras relacionadas con phishing
    if article.ejemplos_ataque:
        phishing_keywords = ['enlace', 'falso', 'clonado', 'suplanta', 'correo', 'sms', 'formulario', 'página', 'sitio', 'qr', 'deepfake']
        has_phishing = any(kw in article.ejemplos_ataque.lower() for kw in phishing_keywords)

        if not has_phishing and len(article.ejemplos_ataque) > 100:
            issues.append({
                'field': 'ejemplos_ataque',
                'issue': 'No contiene palabras phishing (enlace, falso, clonado, etc)',
                'severity': 'ALTO'
            })

    # 4. origen_ataque debe hablar de "atacantes" o actores maliciosos
    if article.origen_ataque:
        origin_keywords = ['atacante', 'delincuente', 'estafador', 'ciberdelincuente', 'grupo', 'banda', 'actor', 'criminal']
        has_origin = any(kw in article.origen_ataque.lower() for kw in origin_keywords)

        if not has_origin and len(article.origen_ataque) > 50:
            issues.append({
                'field': 'origen_ataque',
                'issue': 'No contiene palabras sobre atacantes/delincuentes',
                'severity': 'ALTO'
            })

    # 5. objetivo_ataque debe hablar de víctimas o blancos
    if article.objetivo_ataque:
        target_keywords = ['usuario', 'cliente', 'víctima', 'persona', 'empresa', 'banco', 'institución', 'empleado', 'cuenta']
        has_target = any(kw in article.objetivo_ataque.lower() for kw in target_keywords)

        if not has_target and len(article.objetivo_ataque) > 50:
            issues.append({
                'field': 'objetivo_ataque',
                'issue': 'No contiene palabras sobre víctimas/objetivos',
                'severity': 'ALTO'
            })

    # 6. recomendaciones debe contener consejos de seguridad
    if article.recomendaciones:
        recommendation_keywords = ['no', 'no hacer', 'verific', 'actualiz', 'cambiar', 'proteg', 'cuidado', 'alerta', 'reportar', 'denuncia', 'evitar', 'segur']
        has_recommendation = any(kw in article.recomendaciones.lower() for kw in recommendation_keywords)

        if not has_recommendation and len(article.recomendaciones) > 100:
            issues.append({
                'field': 'recomendaciones',
                'issue': 'No contiene palabras de recomendación (no, verificar, actualizar, etc)',
                'severity': 'ALTO'
            })

    # 7. Campo completamente duplicado (copiar-pega error)
    if (article.proceso_ataque and article.titulo and
        article.proceso_ataque.lower() == article.titulo.lower()):
        issues.append({
            'field': 'proceso_ataque',
            'issue': 'DUPLICADO EXACTO DEL TÍTULO (error de extracción)',
            'severity': 'CRITICO'
        })

    if (article.ejemplos_ataque and article.proceso_ataque and
        article.ejemplos_ataque.lower() == article.proceso_ataque.lower()):
        issues.append({
            'field': 'ejemplos_ataque',
            'issue': 'DUPLICADO DE PROCESO_ATAQUE',
            'severity': 'CRITICO'
        })

    return issues

def main():
    articles = Articulo.objects.all()

    print("\n" + "=" * 90)
    print("ANÁLISIS RÁPIDO: Anomalías en campos extraídos")
    print("=" * 90)

    total_issues = 0
    critical_issues = []
    high_issues = []
    medium_issues = []

    for i, article in enumerate(articles, 1):
        issues = analyze_field_consistency(article)

        if issues:
            total_issues += len(issues)
            print(f"\n[{i}] {article.titulo[:70]}")
            print(f"    Fuente: {article.fuente} | URL: {article.url[:60]}")

            for issue in issues:
                severity = issue['severity']
                symbol = "[!!!]" if severity == 'CRITICO' else "[!!]" if severity == 'ALTO' else "[!]"
                print(f"    {symbol} [{severity:7}] {issue['field']:20} | {issue['issue']}")

                if severity == 'CRITICO':
                    critical_issues.append((article.id, article.titulo[:50], issue))
                elif severity == 'ALTO':
                    high_issues.append((article.id, article.titulo[:50], issue))
                else:
                    medium_issues.append((article.id, article.titulo[:50], issue))

    # RESUMEN
    print("\n" + "=" * 90)
    print("RESUMEN DE ANOMALÍAS")
    print("=" * 90)

    print(f"\nTotal artículos: {articles.count()}")
    print(f"Total anomalías encontradas: {total_issues}")
    print(f"\nDistribución:")
    print(f"  [!!!] CRITICAS: {len(critical_issues)}")
    print(f"  [!!]  ALTAS: {len(high_issues)}")
    print(f"  [!]   MEDIAS: {len(medium_issues)}")

    if critical_issues:
        print("\n" + "=" * 90)
        print("PROBLEMAS CRÍTICOS (Requieren revisión)")
        print("=" * 90)
        for article_id, title, issue in critical_issues:
            print(f"\n[{article_id}] {title}")
            print(f"  Campo: {issue['field']}")
            print(f"  Problema: {issue['issue']}")

    if high_issues:
        print("\n" + "=" * 90)
        print("PROBLEMAS ALTOS (Revisión recomendada)")
        print("=" * 90)

        # Agrupar por campo
        by_field = {}
        for article_id, title, issue in high_issues:
            field = issue['field']
            if field not in by_field:
                by_field[field] = []
            by_field[field].append((article_id, title, issue))

        for field, items in sorted(by_field.items()):
            print(f"\n{field} ({len(items)} problemas):")
            for article_id, title, issue in items[:3]:  # Mostrar primeros 3
                print(f"  [{article_id}] {title} | {issue['issue']}")

if __name__ == '__main__':
    main()
