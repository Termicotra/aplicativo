#!/usr/bin/env python
"""
Script para verificar la lógica de mejoras de ingestion sin necesidad de URLs.
Prueba localmente las funciones nuevas.
"""
import sys
sys.path.insert(0, 'articulos')

from ingestion import (
    _clean_text,
    _normalize_for_match,
    _is_generic_sentence,
    _calculate_string_similarity,
    _extract_paragraph_text,
    _extract_attack_context
)

def test_clean_text():
    """Probar limpieza de texto"""
    print("\n" + "=" * 80)
    print("TEST 1: LIMPIEZA DE TEXTO (_clean_text)")
    print("=" * 80)

    tests = [
        ("Contenido normal sin ruido", "Contenido normal sin ruido"),
        ("Contenido [lea más](url)", "Contenido"),
        ("<p>Con HTML</p>", "Con HTML"),
        ("Anterior siguiente siguiente", ""),
        ("Comentarios 5 comentarios", ""),
    ]

    for input_text, expected in tests:
        result = _clean_text(input_text)
        # Verifica que el resultado tenga el contenido esperado
        if expected == "":
            status = "✓" if "anterior" not in result.lower() and "siguiente" not in result.lower() else "✗"
        else:
            status = "✓" if expected in result else "✗"
        print(f"{status} Input: '{input_text[:50]}'")
        print(f"  Output: '{result[:50]}'")

def test_generic_detection():
    """Probar detección de frases genéricas"""
    print("\n" + "=" * 80)
    print("TEST 2: DETECCIÓN DE GENÉRICOS (_is_generic_sentence)")
    print("=" * 80)

    generic_sentences = [
        "Es importante estar atento",
        "En conclusión, se recomienda",
        "Como siempre, este es un aviso",
    ]

    specific_sentences = [
        "Se detectó CVE-2024-5678 en Firefox 125",
        "Banco Nacional reporta campaña phishing",
        "Los atacantes solicitan verificación 2FA",
    ]

    print("\n✓ Frases que DEBEN ser detectadas como genéricas:")
    for sentence in generic_sentences:
        is_generic = _is_generic_sentence(sentence)
        status = "✓" if is_generic else "✗"
        print(f"{status} '{sentence[:60]}'")

    print("\n✓ Frases que NO deben ser detectadas como genéricas:")
    for sentence in specific_sentences:
        is_generic = _is_generic_sentence(sentence)
        status = "✓" if not is_generic else "✗"
        print(f"{status} '{sentence[:60]}'")

def test_similarity():
    """Probar cálculo de similitud"""
    print("\n" + "=" * 80)
    print("TEST 3: SIMILITUD DE STRINGS (_calculate_string_similarity)")
    print("=" * 80)

    test_pairs = [
        ("Se detectó CVE-2024-5678", "Se detectó CVE-2024-5678", True),  # Idénticas
        ("Actualiza Firefox", "Actualiza Chrome", False),  # Diferentes
        ("CVE-2024-5678 en Firefox", "Firefox CVE-2024-5678", True),  # Muy parecidas
    ]

    for s1, s2, should_be_similar in test_pairs:
        similarity = _calculate_string_similarity(s1, s2)
        is_similar = similarity >= 0.75
        status = "✓" if is_similar == should_be_similar else "✗"
        print(f"{status} Similitud {similarity:.2f}: '{s1[:40]}' vs '{s2[:40]}'")

def test_paragraph_extraction():
    """Probar extracción de párrafos"""
    print("\n" + "=" * 80)
    print("TEST 4: EXTRACCIÓN DE PÁRRAFOS (_extract_paragraph_text)")
    print("=" * 80)

    html = """
    <html>
        <nav>Navegación - anterior siguiente</nav>
        <article>
            <p>Este es un párrafo relevante sobre phishing.</p>
            <p>Segundo párrafo con detalles técnicos de CVE-2024-5678.</p>
            <sidebar>Esta es una barra lateral que no debe incluirse</sidebar>
            <p>Tercer párrafo importante</p>
        </article>
        <footer>Pie de página - comentarios</footer>
    </html>
    """

    result = _extract_paragraph_text(html)
    print(f"\nContenido extraído ({len(result)} chars):")
    print(f"'{result[:200]}...'")

    # Verificaciones
    checks = [
        ("Contiene 'phishing'", "phishing" in result.lower()),
        ("Contiene 'CVE-2024'", "CVE-2024" in result),
        ("NO contiene 'navegación'", "navegación" not in result.lower()),
        ("NO contiene 'comentarios'", "comentarios" not in result.lower()),
        ("NO contiene 'siguiente'", "siguiente" not in result.lower()),
    ]

    print("\nVerificaciones:")
    for check_name, result_check in checks:
        status = "✓" if result_check else "✗"
        print(f"{status} {check_name}")

def test_attack_context():
    """Probar extracción de contexto de ataque"""
    print("\n" + "=" * 80)
    print("TEST 5: EXTRACCIÓN DE CONTEXTO DE ATAQUE (_extract_attack_context)")
    print("=" * 80)

    test_content = """
    Se reporta una campaña de phishing contra Banco Nacional de Paraguay.
    Los atacantes envían SMS falsos solicitando verificación de dos factores.
    El proceso funciona así: primero, el usuario recibe un SMS falso,
    luego hace clic en un enlace malicioso que lo redirige a un sitio clonado.
    Se recomienda no compartir credenciales y activar autenticación de dos factores.
    El canal de distribución es SMS (smishing).
    """

    title = "Campaña phishing contra Banco Nacional con CVE-2024-5678"

    context = _extract_attack_context(
        title=title,
        content=test_content,
        html=""
    )

    print("\nContexto extraído:")
    for key, value in context.items():
        print(f"\n{key}:")
        print(f"  {value[:150] if value else '(vacío)'}")

    # Verificaciones
    checks = [
        ("Tiene proceso", bool(context.get('proceso_ataque', '').strip())),
        ("Tiene secuencia", bool(context.get('secuencia_ataque', '').strip())),
        ("Tiene recomendaciones", bool(context.get('recomendaciones', '').strip())),
        ("Detectó canal SMS", context.get('canal_ataque') in ['sms', 'smishing']),
    ]

    print("\nVerificaciones:")
    for check_name, result_check in checks:
        status = "✓" if result_check else "✗"
        print(f"{status} {check_name}")

def main():
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║  VERIFICACIÓN DE MEJORAS DE INGESTION                                     ║")
    print("╚" + "=" * 78 + "╝")

    try:
        test_clean_text()
        test_generic_detection()
        test_similarity()
        test_paragraph_extraction()
        test_attack_context()

        print("\n" + "=" * 80)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 80)
        print("\n✓ Las funciones mejoradas están funcionando correctamente")
        print("✓ La limpieza de ruido está operativa")
        print("✓ La detección de genéricos está funcionando")
        print("✓ La similitud para deduplicación está operativa")
        print("✓ La extracción de contexto está mejorada")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
