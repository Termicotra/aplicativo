#!/usr/bin/env python
"""
Validar las mejoras de scraping con los casos REALES que fallaron.
Salida ASCII-only para evitar problemas de encoding en consola Windows.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from articulos.ingestion import (
    _clean_text,
    _looks_promising,
    _calculate_relevance_score,
    _is_boilerplate_paragraph,
    _deduplicate_by_title,
    MIN_RELEVANCE_SCORE,
)

passed = 0
failed = 0


def check(label, condition, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label}  {detail}")


print("=" * 78)
print("TEST 1: Decodificacion de entidades HTML")
print("=" * 78)

t1 = _clean_text('Alerta de seguridad &#8211; Multiples ataques phishing')
check("Decodifica &#8211;", '&#8211;' not in t1 and '-' in t1, f"-> {t1!r}")

t2 = _clean_text('activacion de&nbsp;verificacion en dos pasos')
check("Decodifica &nbsp;", '&nbsp;' not in t2, f"-> {t2!r}")

t3 = _clean_text('Banco &amp; Financiera')
check("Decodifica &amp;", '&' in t3 and '&amp;' not in t3, f"-> {t3!r}")


print()
print("=" * 78)
print("TEST 2: Eliminacion de boilerplate del portal")
print("=" * 78)

t4 = _clean_text('Unite al canal de ABC en WhatsApp Desde el sector oficial recuerdan no ingresar a enlaces sospechosos')
check("Elimina 'Unite al canal de ABC en WhatsApp'", 'unite al canal' not in t4.lower(), f"-> {t4[:70]!r}")

t5 = _clean_text('Se reporta un nuevo metodo 01/06/2022 Noticias 0 que afecta a WhatsApp')
check("Elimina metadata CERT '01/06/2022 Noticias 0'", 'Noticias 0' not in t5, f"-> {t5[:70]!r}")

check("Detecta parrafo promocional corto",
      _is_boilerplate_paragraph('Unite al canal de ABC en WhatsApp'))
check("Detecta teaser truncado",
      _is_boilerplate_paragraph('Se ha reportado un nuevo metodo de robo [...]'))
check("NO marca contenido real como boilerplate",
      not _is_boilerplate_paragraph(
          'Los atacantes envian correos falsos que suplantan al Banco Nacional y solicitan credenciales de acceso.'))


print()
print("=" * 78)
print("TEST 3: Pre-filtro _looks_promising (evita descargas inutiles)")
print("=" * 78)

cases_promising = [
    ("Phishing en el Poder Judicial", "Alerta de phishing en el Poder Judicial",
     "Se detectaron correos falsos que suplantan al Poder Judicial", True),
    ("Web falsa Tekopora", "Que no te estafen por querer cobrar Tekopora: usan web falsa",
     "Usan una web falsa para suplantar el Portal Paraguay", True),
    ("Vulnerabilidad Zoho (RECHAZAR)", "Vulnerabilidad en productos Zoho",
     "Se reporta una vulnerabilidad critica en productos Zoho, version afectada 5.2", False),
    ("CVE tecnico (RECHAZAR)", "Vulnerabilidad critica en Apache Struts",
     "CVE-2024-1234 permite ejecucion remota de codigo", False),
    ("Deportes (RECHAZAR)", "Cerro Porteno gano el clasico",
     "El equipo se consagro campeon en el estadio", False),
]

for label, title, snippet, expected in cases_promising:
    result = _looks_promising(title=title, snippet=snippet)
    check(f"{label}: {'acepta' if expected else 'rechaza'}",
          result == expected, f"-> obtuvo {result}")


print()
print("=" * 78)
print("TEST 4: Puntaje de relevancia (modo estricto)")
print("=" * 78)
print(f"  Umbral minimo: {MIN_RELEVANCE_SCORE}")
print()

cases_score = [
    (
        "Tekopora web falsa (ACEPTAR)",
        "Que no te estafen por querer cobrar Tekopora: usan web falsa para suplantar el Portal Paraguay",
        "Desde el Ministerio de Tecnologias de la Informacion y Comunicacion (Mitic) de Paraguay instan a la "
        "poblacion a no ingresar datos personales. Los atacantes usan una web falsa que suplanta el Portal "
        "Paraguay y solicita credenciales con urgencia. Se trata de una estafa conocida como phishing.",
        "https://www.abc.com.py/nacionales/2026/08/27/tekopora/",
        True,
    ),
    (
        "Credito hipotecario Mexico (RECHAZAR)",
        "Credito hipotecario crecera hasta un 6 % en Mexico en 2026 entre riesgos de fraude",
        "En ese contexto, el economista especialista en mercado inmobiliario en Mexico senalo que la banca "
        "privada coloco en 2025 alrededor de 236.000 millones de pesos mexicanos y que el mercado crecera.",
        "https://www.abc.com.py/internacionales/2026/08/28/credito-hipotecario/",
        False,
    ),
    (
        "Vulnerabilidad Zoho (RECHAZAR)",
        "Vulnerabilidad en productos Zoho",
        "Se ha reportado una vulnerabilidad en productos Zoho. La version afectada requiere un parche de "
        "seguridad inmediato. Permite escalada de privilegios en el servidor.",
        "https://www.cert.gov.py/vulnerabilidad-en-productos-zoho-2/",
        False,
    ),
    (
        "Campana phishing bancos PY (ACEPTAR)",
        "Campana de phishing contra clientes de bancos paraguayos",
        "Los atacantes envian correos falsos que suplantan la identidad de bancos paraguayos. El correo "
        "solicita credenciales con caracter urgente e incluye un enlace malicioso que redirige a una pagina "
        "clonada. Se recomienda verificar el remitente.",
        "https://www.cert.gov.py/campana-de-phishing/",
        True,
    ),
    (
        "Robo WhatsApp con PIN (ACEPTAR)",
        "Nuevo metodo de robo de cuentas de WhatsApp",
        "Se ha reportado un nuevo metodo para el robo de credenciales que afecta a WhatsApp. Un atacante "
        "puede secuestrar la cuenta mediante suplantacion y desvio de llamadas. Se recomienda la activacion "
        "de verificacion en dos pasos.",
        "https://www.cert.gov.py/nuevo-metodo-robo-whatsapp/",
        True,
    ),
]

for label, title, content, url, should_accept in cases_score:
    score = _calculate_relevance_score(title=title, content=content, url=url)
    accepted = score >= MIN_RELEVANCE_SCORE
    check(f"{label}: puntaje {score}",
          accepted == should_accept,
          f"-> {'acepto' if accepted else 'rechazo'}, esperaba {'aceptar' if should_accept else 'rechazar'}")


print()
print("=" * 78)
print("TEST 5: Deduplicacion por titulo")
print("=" * 78)

dupes = [
    {'titulo': 'Alerta de phishing en el Poder Judicial', 'url': 'a'},
    {'titulo': 'Alerta de phishing en el Poder Judicial', 'url': 'b'},
    {'titulo': 'Campana de smishing contra bancos', 'url': 'c'},
]
result = _deduplicate_by_title(dupes)
check(f"Reduce 3 -> 2 articulos", len(result) == 2, f"-> obtuvo {len(result)}")


print()
print("=" * 78)
print(f"RESULTADO: {passed} PASS / {failed} FAIL")
print("=" * 78)
