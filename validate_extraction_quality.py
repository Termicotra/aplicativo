#!/usr/bin/env python
"""
Validar que la CALIDAD de extracción mejoró con el nuevo código.
Verificar que proceso_ataque, secuencia_ataque y ejemplos_ataque están completos.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.models import Articulo

print("\n" + "=" * 80)
print("VALIDACION: CALIDAD DE EXTRACCION CON NUEVO CODIGO")
print("=" * 80)

# Obtener todos los artículos
articles = Articulo.objects.all()
total = articles.count()

print(f"\nTotal articulos: {total}")

if total == 0:
    print("Sin articulos en BD")
    exit(1)

# Validar campos críticos
print("\n" + "=" * 80)
print("VALIDACION 1: PROCESO_ATAQUE (Debe > 50 chars)")
print("=" * 80)

with_process = articles.exclude(proceso_ataque='').count()
without_process = total - with_process
process_precision = (with_process / total * 100) if total > 0 else 0

print(f"\nCon proceso_ataque: {with_process}/{total} ({process_precision:.1f}%)")
print(f"Sin proceso_ataque: {without_process}")

# Ejemplos de buenos proceso_ataque
good_processes = [a for a in articles if len(a.proceso_ataque) >= 100]
print(f"\nBuenos proceso_ataque (>100 chars): {len(good_processes)}/{total}")

print("\n" + "=" * 80)
print("VALIDACION 2: SECUENCIA_ATAQUE (Debe describir pasos)")
print("=" * 80)

with_sequence = articles.exclude(secuencia_ataque='').count()
without_sequence = total - with_sequence
sequence_precision = (with_sequence / total * 100) if total > 0 else 0

print(f"\nCon secuencia_ataque: {with_sequence}/{total} ({sequence_precision:.1f}%)")
print(f"Sin secuencia_ataque: {without_sequence}")

# Ejemplos de buenos secuencia_ataque
good_sequences = articles.filter(secuencia_ataque__length__gte=80).exclude(secuencia_ataque='')
print(f"\nBuenos secuencia_ataque (>80 chars): {good_sequences.count()}/{total}")

print("\n" + "=" * 80)
print("VALIDACION 3: EJEMPLOS_ATAQUE (Tácticas de phishing)")
print("=" * 80)

with_examples = articles.exclude(ejemplos_ataque='').count()
without_examples = total - with_examples
examples_precision = (with_examples / total * 100) if total > 0 else 0

print(f"\nCon ejemplos_ataque: {with_examples}/{total} ({examples_precision:.1f}%)")
print(f"Sin ejemplos_ataque: {without_examples}")

# Ejemplos de buenos ejemplos_ataque
good_examples = articles.filter(ejemplos_ataque__length__gte=50).exclude(ejemplos_ataque='')
print(f"\nBuenos ejemplos_ataque (>50 chars): {good_examples.count()}/{total}")

print("\n" + "=" * 80)
print("VALIDACION 4: DISTRIBUCION DE CAMPOS")
print("=" * 80)

field_stats = {
    'proceso_ataque': articles.exclude(proceso_ataque='').count(),
    'secuencia_ataque': articles.exclude(secuencia_ataque='').count(),
    'ejemplos_ataque': articles.exclude(ejemplos_ataque='').count(),
    'recomendaciones': articles.exclude(recomendaciones='').count(),
    'origen_ataque': articles.exclude(origen_ataque='').count(),
    'objetivo_ataque': articles.exclude(objetivo_ataque='').count(),
}

print("\nCampos poblados:")
for field, count in field_stats.items():
    percentage = (count / total * 100) if total > 0 else 0
    status = "[OK]" if count >= total * 0.6 else "[BAJO]"
    print(f"  {status} {field}: {count}/{total} ({percentage:.0f}%)")

print("\n" + "=" * 80)
print("EJEMPLOS DETALLADOS (Primeros 3 articulos)")
print("=" * 80)

for i, article in enumerate(articles[:3], 1):
    print(f"\n[{i}] {article.titulo[:70]}")
    print(f"    Fuente: {article.fuente}")

    print(f"\n    Proceso ({len(article.proceso_ataque)} chars):")
    preview = article.proceso_ataque[:150]
    if len(preview) < len(article.proceso_ataque):
        preview += "..."
    print(f"      {preview}")

    print(f"\n    Secuencia ({len(article.secuencia_ataque)} chars):")
    preview = article.secuencia_ataque[:150]
    if len(preview) < len(article.secuencia_ataque):
        preview += "..."
    print(f"      {preview}")

    print(f"\n    Ejemplos ({len(article.ejemplos_ataque)} chars):")
    preview = article.ejemplos_ataque[:150]
    if len(preview) < len(article.ejemplos_ataque):
        preview += "..."
    print(f"      {preview}")

print("\n" + "=" * 80)
print("VALIDACION 5: BUSQUEDA DE RUIDO TECNICO")
print("=" * 80)

# Buscar palabras clave de ruido técnico
technical_noise = [
    'CVE-',
    'vulnerabilidad',
    'exploit',
    'versión',
    'navegador',
    'Firefox',
    'Chrome',
    'Edge',
]

articles_with_noise = 0
for article in articles:
    full_text = f"{article.titulo} {article.proceso_ataque} {article.ejemplos_ataque}"
    has_noise = any(noise.lower() in full_text.lower() for noise in technical_noise)
    if has_noise:
        articles_with_noise += 1

noise_percentage = (articles_with_noise / total * 100) if total > 0 else 0
print(f"\nArticulos con posible ruido técnico: {articles_with_noise}/{total} ({noise_percentage:.1f}%)")

if noise_percentage < 10:
    print("[OK] Ruido técnico bajo (<10%)")
elif noise_percentage < 30:
    print("[MEDIO] Ruido técnico medio (10-30%)")
else:
    print("[ALTO] Ruido técnico alto (>30%)")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)

print(f"\nMetricas:")
print(f"  proceso_ataque: {process_precision:.1f}%")
print(f"  secuencia_ataque: {sequence_precision:.1f}%")
print(f"  ejemplos_ataque: {examples_precision:.1f}%")
print(f"  ruido técnico: {noise_percentage:.1f}%")

avg_precision = (process_precision + sequence_precision + examples_precision) / 3
print(f"\nPromedio de extracción: {avg_precision:.1f}%")

if avg_precision >= 80:
    print("[OK] Extraccion de alta calidad (>=80%)")
elif avg_precision >= 60:
    print("[MEDIO] Extraccion de calidad media (60-80%)")
else:
    print("[BAJO] Extraccion de baja calidad (<60%)")
