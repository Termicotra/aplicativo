#!/usr/bin/env python
"""
Test de la LÓGICA del nuevo ingestion.py sin descargar artículos.
Prueba las funciones de filtrado y extracción localmente.
"""
import os
import django
import unicodedata
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import (
    _normalize_for_match,
    _has_attack_flow_description,
    _extract_attack_context,
)

def test_has_attack_flow():
    """Prueba la función _has_attack_flow_description con casos reales"""
    print("\n" + "=" * 80)
    print("TEST 1: DETECCIÓN DE FLUJO DE PHISHING (Nuevo criterio)")
    print("=" * 80)

    test_cases = [
        {
            'name': 'Phishing directo (tácticas + acciones)',
            'title': 'Phishing contra Banco Nacional',
            'content': 'Los atacantes envían correos falsos que parecen de Banco Nacional. '
                      'Solicitan verificación 2FA a través de un enlace malicioso. '
                      'El usuario es redirigido a un sitio clonado donde ingresa credenciales.',
            'expected': True,
        },
        {
            'name': 'Phishing con ingeniería social',
            'title': 'Campaña de smishing con urgencia',
            'content': 'Se reporta campaña phishing. Los atacantes crean urgencia diciendo que '
                      'la cuenta será bloqueada inmediatamente. El mensaje solicita confirmación '
                      'de identidad a través de un enlace falso. Esto es manipulación psicológica.',
            'expected': True,
        },
        {
            'name': 'Solo información técnica (debe rechazarse)',
            'title': 'CVE-2024-5678 en Firefox',
            'content': 'Se descubre vulnerabilidad CVE-2024-5678. Afecta a navegador Firefox '
                      'en versión 125. La explotación requiere script malicioso. Se recomienda actualizar.',
            'expected': False,
        },
        {
            'name': 'Flujo explícito + tácticas',
            'title': 'Cómo funciona el phishing por SMS',
            'content': 'Primero, el usuario recibe un SMS falso del banco. Luego, hace clic en '
                      'el enlace malicioso. Después, es redirigido a un sitio clonado. Finalmente, '
                      'ingresa sus credenciales y la cuenta es comprometida.',
            'expected': True,
        },
    ]

    for test in test_cases:
        result = _has_attack_flow_description(title=test['title'], content=test['content'])
        status = "[PASS]" if result == test['expected'] else "[FAIL]"
        expected_str = "Debe aceptar" if test['expected'] else "Debe rechazar"
        actual_str = "Aceptado" if result else "Rechazado"
        print(f"\n{status} | {test['name']}")
        print(f"  Esperado: {expected_str}")
        print(f"  Resultado: {actual_str}")

def test_extract_context():
    """Prueba la función _extract_attack_context"""
    print("\n" + "=" * 80)
    print("TEST 2: EXTRACCIÓN DE CONTEXTO DE ATAQUE")
    print("=" * 80)

    title = "Phishing contra Banco Nacional"
    content = """
    Los atacantes han lanzado una campaña phishing dirigida a clientes de Banco Nacional.
    En esta campaña, envían correos falsos que parecen legitimamente del banco.
    Los correos solicitan que el usuario verifique su identidad a través de un enlace.
    El enlace redirige a un sitio clonado que es idéntico al sitio oficial del banco.
    El usuario ingresa sus credenciales pensando que es el banco real.
    Los atacantes capturan estas credenciales y obtienen acceso a la cuenta.

    El proceso funciona así:
    Primero, el usuario recibe el correo falso.
    Luego, hace clic en el enlace del correo.
    Después, es redirigido al sitio clonado.
    Finalmente, ingresa sus credenciales de acceso.

    Esta es una técnica de suplantación de identidad muy común.
    Se recomienda no hacer clic en enlaces desconocidos.
    """

    result = _extract_attack_context(title=title, content=content)

    print(f"\nTítulo: {title}")
    print(f"\nCampos extraídos:")

    for field, value in result.items():
        char_count = len(value)
        preview = value[:100] + "..." if len(value) > 100 else value
        print(f"\n  {field} ({char_count} chars):")
        print(f"    {preview}")

    # Validaciones
    print(f"\n{'='*80}")
    print("VALIDACIONES:")
    print(f"{'='*80}")

    checks = [
        ('proceso_ataque', lambda r: r.get('proceso_ataque', ''), 'Debe contener información de cómo funciona'),
        ('secuencia_ataque', lambda r: r.get('secuencia_ataque', ''), 'Debe contener pasos (primero, luego, etc)'),
        ('ejemplos_ataque', lambda r: r.get('ejemplos_ataque', ''), 'Debe contener ejemplos de tácticas phishing'),
    ]

    for field, getter, description in checks:
        value = getter(result)
        has_content = len(value) > 50
        status = "[OK]" if has_content else "[ERROR]"
        print(f"\n{status} {field}:")
        print(f"  {description}")
        print(f"  Resultado: {'Extraído correctamente' if has_content else 'SIN CONTENIDO (ERROR)'}")

def main():
    print("\n" + "=" * 80)
    print("TEST DE LÓGICA: NUEVO INGESTION.PY (PHISHING PURO)")
    print("=" * 80)

    test_has_attack_flow()
    test_extract_context()

    print("\n" + "=" * 80)
    print("[SUCCESS] TESTS COMPLETADOS")
    print("=" * 80)
    print("\nNota: Estos tests validan que:")
    print("  1. La detección de flujo rechaza artículos técnicos (CVE, versiones)")
    print("  2. La detección acepta phishing puro (tácticas, ingeniería social)")
    print("  3. La extracción obtiene proceso, secuencia y ejemplos correctamente")
    print("\n")

if __name__ == '__main__':
    main()
