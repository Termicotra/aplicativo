from __future__ import annotations

import json  # Para parsear JSON de APIs
import logging  # Para registrar eventos
import re  # Expresiones regulares
import unicodedata  # Normalizar caracteres acentuados
from datetime import date, datetime, timezone  # Manejo de fechas
from email.utils import parsedate_to_datetime  # Parsear fechas en formato email
from typing import Any  # Type hints
from socket import timeout as socket_timeout  # Para compatibilidad con Python < 3.10
from urllib.error import URLError  # Excepciones de red
from urllib.parse import quote_plus, urlparse  # Codificar URLs y extraer componentes
from urllib.request import Request, urlopen  # Descargar contenido HTTP, esto se encarga de hacer requests HTTP y manejar redirecciones, etc.

from .models import Articulo  # Modelo Django para guardar artículos

logger = logging.getLogger(__name__)  # Logger para registrar eventos de este módulo



# [1. Petición HTTP] ──> [2. Extracción & Búsqueda] ──> [3. Enriquecimiento] ──> [4. Guardado en DB]


# 2. Solo extrae Un título, Un enlace (URL) y Un snippet (un fragmento corto de 1 o 2 oraciones).
# ============== CONFIGURACIÓN DE FUENTES ==============
# ABC Color - búsqueda por API Queryly
ABC_BASE_URL = 'https://www.abc.com.py'
ABC_SEARCH_QUERIES = ('phishing', 'smishing')  # Qué buscar en ABC
ABC_QUERYLY_KEY = '33530b56c6aa4c20'  # API key para búsqueda
ABC_QUERYLY_ENDPOINT = 'https://api.queryly.com/json.aspx'  # Endpoint de búsqueda

# CERT Paraguay - búsqueda por web scraping
CERT_BASE_URL = 'https://www.cert.gov.py'
CERT_SEARCH_TERMS = ('phishing', 'smishing', 'robo')  # Qué buscar en CERT
CERT_EXCLUDED_PATHS = ('/soc-cert-py/',)  # Paths a ignorar

# ============== CONFIGURACIÓN GENERAL ==============
USER_AGENT = 'treck-ingestion-bot/1.0 (+https://localhost)'  # Para los requests HTTP
DEFAULT_CONTENT = 'Sin contenido disponible.'  # Cuando no hay contenido
SOURCE_ABC = 'ABC Color'
SOURCE_CERT = 'CERT Paraguay'
LOOKBACK_YEARS = 3  # Buscar artículos de últimos 3 años
MIN_ALLOWED_DATE = date(2022, 1, 1)  # Fecha mínima permitida

# ============== PALABRAS CLAVE PARA FILTRADO ==============
# Detecta si un artículo es relevante para Paraguay
PARAGUAY_KEYWORDS = (
    'paraguay',
    'paraguayo',
    'paraguaya',
    'asuncion',
    'encarnacion',
    'ciudad del este',
    'ministerio publico',
    'poder judicial',
    'corte suprema de justicia',
    'policia nacional',
    'cert py',
)

# Acciones que hacen los atacantes (envían, redirigen, suplantan, etc.)
ATTACK_ACTION_KEYWORDS = (
    'los atacantes',
    'el atacante',
    'el usuario',
    'envian',
    'envia',
    'redirigen',
    'redirige',
    'suplantan',
    'suplanta',
    'hacen pasar',
    'simulan',
    'simula',
    'capturan credenciales',
    'roban credenciales',
)

# Patrones regex para detectar flujos de ataque (primero...luego, paso a paso)
ATTACK_FLOW_PATTERNS = (
    r'\bprimero\b.{0,120}\bluego\b',  # "primero X luego Y"
    r'\bel proceso consiste en\b',  # "el proceso consiste en"
    r'\bel ataque funciona asi\b',  # "el ataque funciona así"
    r'\bpaso a paso\b',  # "paso a paso"
    r'\bcadena de ataque\b',  # "cadena de ataque"
)

# Palabras específicas sobre operaciones phishing/smishing
PHISHING_OPERATION_KEYWORDS = (
    'campana de phishing',
    'correo falso',
    'correo fraudulento',
    'mensaje fraudulento',
    'sitio falso',
    'pagina falsa',
    'sitio clonado',
    'captura de credenciales',
    'robo de credenciales',
    'suplantacion de identidad',
    'enlace malicioso',
    'url maliciosa',
    'bancos paraguayos',
    'campana de smishing',
    'sms falso',
    'sms fraudulento',
    'mensaje de texto falso',
    'suplantacion por sms',
)

# Objetos técnicos mencionados (URLs, QR, etc.)
TECHNICAL_OBJECT_KEYWORDS = (
    'enlaces falsos',
    'pagina clonada',
    'paginas clonadas',
    'qr malicioso',
    'quishing',
    'deepfake de voz',
    'sms spoofing',
    'sms clonado',
    'spoof de sms',
    'enlace en sms',
    'url acortada',
    'bit.ly',
    'tinyurl',
)

# Palabras de recomendación de seguridad
RECOMMENDATION_KEYWORDS = (
    'se recomienda',
    'recomendamos',
    'no haga clic',
    'no compartir',
    'verifique',
    'activar',
    'doble factor',
    'autenticacion de dos factores',
    'reportar',
    'como evitar',
    'evitar este ataque',
    'prevenir',
    'prevenga',
    'proteja',
    'proteccion',
)

# Marcadores de secuencia en oraciones
SEQUENCE_SENTENCE_MARKERS = (
    'primero',
    'luego',
    'despues',
    'finalmente',
    'el proceso',
    'paso',
)

# Palabras que identifican al origen del ataque
ORIGIN_MARKERS = (
    'los atacantes',
    'ciberdelincuentes',
    'los estafadores',
    'actores maliciosos',
)

# Palabras que identifican el objetivo del ataque
TARGET_MARKERS = (
    'clientes de',
    'usuarios de',
    'personas usuarias',
    'victimas',
)

# Canales de ataque (tupla: nombre -> palabras clave)
CHANNEL_PATTERNS = (
    ('whatsapp', ('whatsapp',)),
    ('sms', ('sms', 'mensaje de texto')),
    ('correo', ('correo electronico', 'email', 'e-mail', 'mail')),
    ('telegram', ('telegram',)),
    ('sitio-web', ('sitio web', 'pagina web', 'enlace', 'url')),
)


def _fetch_xml(url: str, timeout: int = 15) -> str:
    """Descargar HTML/XML desde una URL. Retorna string decodificado UTF-8."""
    request = Request(url, headers={'User-Agent': USER_AGENT})  # Crear request con User-Agent
    with urlopen(request, timeout=timeout) as response:  # Abrir URL con timeout
        return response.read().decode('utf-8', errors='replace')  # Decodificar ignorando errores


def _clean_text(raw: str | None) -> str:
    """Limpiar texto: quotes, HTML, frases innecesarias. Retorna texto compacto."""
    value = raw or ''
    # Normalizar comillas curvas/inteligentes a rectas
    value = value.replace('"', '"').replace('"', '"')  # U+201C, U+201D -> "
    value = value.replace(''', "'").replace(''', "'")  # U+2018, U+2019 -> '
    value = value.replace('«', '"').replace('»', '"')  # U+00AB, U+00BB -> "
    # Eliminar etiquetas HTML
    value = re.sub(r'<[^>]+>', ' ', value)
    # Eliminar frases de "Lea más", "Ver más", "Artículo relacionado"
    value = re.sub(r'(?i)\blea\s+m[áa]s\s*:?\s*', ' ', value)
    value = re.sub(r'(?i)\bver\s+m[áa]s\s*:?\s*', ' ', value)
    value = re.sub(r'(?i)\bart[íi]culo\s+relacionado\b.*$', ' ', value)
    # Colapsar espacios múltiples y recortar
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def _normalize_for_match(text: str) -> str:
    """Normalizar para búsquedas: quitar acentos y convertir a minúsculas."""
    normalized = unicodedata.normalize('NFKD', text)  # Descomponer acentos
    normalized = ''.join(ch for ch in normalized if not unicodedata.combining(ch))  # Quitar marcas diacríticas
    return normalized.lower()  # Convertir a minúsculas


def _split_sentences(text: str) -> list[str]:
    """Dividir texto en oraciones. Solo retorna oraciones con ≥12 caracteres."""
    cleaned = re.sub(r'\s+', ' ', text).strip()  # Colapsar espacios
    if not cleaned:
        return []
    parts = re.split(r'(?<=[\.!?])\s+', cleaned)  # Dividir por . ! ?
    return [item.strip() for item in parts if len(item.strip()) >= 12]  # Filtrar por longitud


def _infer_attack_channel(text_normalized: str) -> str:
    """Detectar canal de ataque (SMS, WhatsApp, correo, etc.) desde el texto normalizado."""
    for channel, markers in CHANNEL_PATTERNS:  # Iterar sobre canales y sus palabras clave
        if any(marker in text_normalized for marker in markers):  # Si encuentra algún marcador
            return channel  # Retorna el canal (ej: 'sms', 'whatsapp')
    return 'indefinido'  # Si no encuentra nada, marca como indefinido


def _extract_list_items_from_html(html: str, marker_text: str, max_items: int = 10) -> list[str]:
    """Extraer items de listas <li> después de un marcador de texto (ej: 'ejemplos son', 'se recomienda')."""
    try:
        # Buscar la sección que contiene el marcador
        marker_pattern = re.escape(marker_text)  # Escapar caracteres especiales
        section_match = re.search(
            rf'{marker_pattern}.*?(?=<(?:h\d|p|div)[^>]*>|$)',  # Hasta el siguiente h/p/div o fin
            html,
            re.IGNORECASE | re.DOTALL
        )
        if not section_match:
            return []

        section_html = section_match.group(0)  # Obtener la sección

        # Extraer todos los <li> de esa sección
        lis = re.findall(r'<li[^>]*>(.*?)</li>', section_html, re.IGNORECASE | re.DOTALL)

        # Limpiar y procesar items
        items = []
        for li in lis[:max_items]:
            cleaned = re.sub(r'<[^>]+>', '', li)  # Eliminar HTML
            # Decodificar HTML entities (&ldquo; -> ")
            cleaned = cleaned.replace('&ldquo;', '"').replace('&rdquo;', '"')
            cleaned = cleaned.replace('&lsquo;', "'").replace('&rsquo;', "'")
            cleaned = cleaned.replace('&amp;', '&')
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Colapsar espacios
            if cleaned:
                items.append(cleaned)

        return items
    except (IndexError, AttributeError, ValueError, re.error) as exc:
        logger.warning('Failed to extract list items from HTML: %s', exc)
        return []  # En caso de error, retorna lista vacía


def _extract_attack_context(*, title: str, content: str, html: str = '') -> dict[str, str]:
    """Extraer 7 campos estructurados del ataque: proceso, secuencia, recomendaciones, ejemplos, origen, objetivo, canal."""
    # Dividir en oraciones y normalizar para búsqueda
    sentences = _split_sentences(f'{title}. {content}')
    normalized_sentences = [_normalize_for_match(item) for item in sentences]

    # Inicializar listas para cada tipo de información
    process_lines: list[str] = []  # Cómo funciona el ataque
    sequence_lines: list[str] = []  # Pasos (primero, luego, después)
    recommendation_lines: list[str] = []  # Recomendaciones de seguridad
    example_lines: list[str] = []  # Objetos técnicos (URLs, QR, etc.)
    origin_line = ''  # Quién ataca
    target_line = ''  # A quién ataca
    recommendation_tail = 0  # Contador para capturar oraciones después de recomendaciones

    # Iterar sobre cada oración y clasificarla
    for raw, normalized in zip(sentences, normalized_sentences):
        # Capturar acciones del atacante (máx 4)
        if any(keyword in normalized for keyword in ATTACK_ACTION_KEYWORDS) and len(process_lines) < 4:
            process_lines.append(raw)

        # Capturar oraciones de secuencia (máx 4)
        if any(marker in normalized for marker in SEQUENCE_SENTENCE_MARKERS) and len(sequence_lines) < 4:
            sequence_lines.append(raw)

        # Si detecta recomendación, añade y prepara para capturar oraciones siguientes
        recommendation_triggered = any(keyword in normalized for keyword in RECOMMENDATION_KEYWORDS)
        if recommendation_triggered and len(recommendation_lines) < 4:
            recommendation_lines.append(raw)
            recommendation_tail = 3  # Capturar las próximas 3 oraciones
            continue

        # Capturar variantes de "evite", "prevenir", etc.
        if any(keyword in normalized for keyword in ('evite', 'evitar', 'prevenir', 'proteja', 'proteccion', 'cambie', 'verifique')) and len(recommendation_lines) < 6:
            if raw not in recommendation_lines:
                recommendation_lines.append(raw)

        # Si estamos en la "cola" de recomendaciones (3 oraciones después), añadir
        if recommendation_tail > 0 and len(recommendation_lines) < 8:
            if raw not in recommendation_lines:
                recommendation_lines.append(raw)
            recommendation_tail -= 1
            continue

        # Decrementar el contador de cola
        if recommendation_tail > 0:
            recommendation_tail -= 1

        # Capturar objetos técnicos mencionados (máx 4)
        if any(keyword in normalized for keyword in TECHNICAL_OBJECT_KEYWORDS) and len(example_lines) < 4:
            example_lines.append(raw)

        # Capturar solo la PRIMERA mención del origen del ataque
        if not origin_line and any(marker in normalized for marker in ORIGIN_MARKERS):
            origin_line = raw

        # Capturar solo la PRIMERA mención del objetivo del ataque
        if not target_line and any(marker in normalized for marker in TARGET_MARKERS):
            target_line = raw

    # Extraer listas estructuradas del HTML si está disponible
    if html:
        list_examples = _extract_list_items_from_html(html, 'ejemplos son', max_items=10)
        list_recommendations = _extract_list_items_from_html(html, 'se recomienda', max_items=10)

        # Priorizar listas HTML sobre extracción de oraciones
        if list_examples:
            example_lines.extend(list_examples)
        if list_recommendations:
            recommendation_lines.extend(list_recommendations)

    # Detectar canal de ataque desde el título+contenido completo
    full_text_normalized = _normalize_for_match(f'{title} {content}')
    channel = _infer_attack_channel(full_text_normalized)

    # Retornar diccionario con todos los campos (máx 1200 caracteres cada uno)
    return {
        'proceso_ataque': ' '.join(process_lines)[:1200],
        'secuencia_ataque': ' '.join(sequence_lines)[:1200],
        'recomendaciones': ' '.join(recommendation_lines)[:1200],
        'ejemplos_ataque': ' '.join(example_lines)[:1200],
        'origen_ataque': origin_line[:600],
        'objetivo_ataque': target_line[:600],
        'canal_ataque': channel,
    }


def _extract_paragraph_text(html: str) -> str:
    """Extraer texto limpio de párrafos HTML. Retorna hasta 5000 caracteres."""
    # Eliminar scripts, styles, SVGs que no tienen contenido útil
    cleaned_html = re.sub(
        r'<(script|style|noscript|svg)[^>]*>.*?</\1>',
        ' ',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Si hay <article>, usar solo eso (descarta navegación, headers, etc.)
    article_match = re.search(r'<article[^>]*>(.*?)</article>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    if article_match:
        cleaned_html = article_match.group(1)

    # Extraer párrafos <p>
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    # Si no hay párrafos, intentar con <li>
    if not paragraphs:
        paragraphs = re.findall(r'<li[^>]*>(.*?)</li>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

    # Limpiar cada párrafo
    cleaned = [_clean_text(item) for item in paragraphs]
    # Concatenar, eliminar vacíos, truncar a 5000 caracteres
    compact = ' '.join(item for item in cleaned if item)
    return compact[:5000].strip()


def _enrich_article_content(url: str, fallback: str) -> str:
    """Descargar artículo desde URL y enriquecer con contenido completo. Si falla, retorna fallback."""
    try:
        html = _fetch_xml(url)  # Descargar HTML
    except (URLError, TimeoutError, socket_timeout, ValueError):
        return fallback  # Si hay error, usar fallback

    detailed = _extract_paragraph_text(html)  # Extraer párrafos limpios
    if not detailed:
        return fallback  # Si no hay párrafos, usar fallback

    # Combinar fallback + contenido detallado
    if fallback and fallback not in detailed:
        return f'{fallback} {detailed}'[:5000]
    return detailed[:5000]


def _enrich_article_content_with_html(url: str, fallback: str) -> tuple[str, str]:
    """Descargar artículo y retornar AMBOS contenido enriquecido E HTML raw. Necesario para extraer listas después."""
    try:
        html = _fetch_xml(url)  # Descargar HTML
    except (URLError, TimeoutError, socket_timeout, ValueError):
        return (fallback, '')  # Si hay error, retorna fallback + HTML vacío

    detailed = _extract_paragraph_text(html)  # Extraer párrafos limpios
    if not detailed:
        return (fallback, html)  # Si no hay párrafos, retorna fallback + HTML raw

    # Combinar fallback + contenido detallado
    if fallback and fallback not in detailed:
        content = f'{fallback} {detailed}'[:5000]
    else:
        content = detailed[:5000]

    return (content, html)  # Retorna contenido limpio Y HTML raw


def _is_paraguay_relevant(*, title: str, content: str, url: str) -> bool:
    """Validar si el artículo es relevante para Paraguay. Busca palabras clave, dominios .py, URLs .py."""
    combined = _normalize_for_match(f'{title} {content}')
    # Buscar palabras clave de Paraguay
    if any(term in combined for term in PARAGUAY_KEYWORDS):
        return True

    # Buscar URLs con dominio .py en el contenido
    if re.search(r'https?://[^\s]+\.py\b', content, flags=re.IGNORECASE):
        return True

    # Validar si la URL es de dominio .py
    parsed = urlparse(url)
    return parsed.netloc.endswith('.py') or '.com.py' in parsed.netloc


def _has_attack_flow_description(*, title: str, content: str) -> bool:
    """Validar si describe un flujo de ataque. Múltiples criterios: acciones, flujos, objetos técnicos, operaciones."""
    text = _normalize_for_match(f'{title} {content}')

    # Contar cuántas palabras clave de cada tipo aparecen
    action_hits = sum(1 for keyword in ATTACK_ACTION_KEYWORDS if keyword in text)  # Qué hacen los atacantes
    flow_hit = any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in ATTACK_FLOW_PATTERNS)  # Pasos
    technical_hit = any(keyword in text for keyword in TECHNICAL_OBJECT_KEYWORDS)  # Objetos técnicos
    operation_hits = sum(1 for keyword in PHISHING_OPERATION_KEYWORDS if keyword in text)  # Operaciones phishing

    # Criterio 1: Tiene flujo explícito (primero...luego) + ≥2 acciones
    if flow_hit and action_hits >= 2:
        return True

    # Criterio 2: ≥4 acciones de ataque (sin flujo explícito)
    if action_hits >= 4:
        return True

    # Criterio 3: Objeto técnico + ≥2 acciones
    if technical_hit and action_hits >= 2:
        return True

    # Criterio 4: ≥2 operaciones phishing (CERT a menudo describe sin "primero/luego")
    if operation_hits >= 2:
        return True

    # Criterio 5: Artículo educativo (objeto técnico + ≥1 operación)
    if technical_hit and operation_hits >= 1:
        return True

    # Criterio 6: Solo objeto técnico (artículos informativos sobre qué es smishing, QR malicioso, etc.)
    if technical_hit:
        return True

    return False  # No cumple ningún criterio


def _passes_article_filters(article: dict[str, Any]) -> bool:
    """Validar que el artículo sea relevante para Paraguay Y describa un flujo de ataque."""
    title = str(article.get('titulo', ''))
    content = str(article.get('contenido', ''))
    url = str(article.get('url', ''))

    # Filtro 1: Es relevante para Paraguay
    if not _is_paraguay_relevant(title=title, content=content, url=url):
        return False

    # Filtro 2: Describe un flujo de ataque
    if not _has_attack_flow_description(title=title, content=content):
        return False

    return True  # Pasó ambos filtros


def _parse_date_strict(raw_date: str | None) -> date | None:
    """Parsear fecha con múltiples formatos. Si falla todos, retorna None (sin fallback a hoy)."""
    if not raw_date:
        return None

    candidate = raw_date.strip()
    if not candidate:
        return None

    # Intento 1: Formato ISO (ej: 2025-09-10T08:30:00-03:00)
    iso_candidate = candidate.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(iso_candidate).date()
    except ValueError:
        pass

    # Intento 2: Formato email
    try:
        return parsedate_to_datetime(candidate).date()
    except (TypeError, ValueError, OverflowError):
        pass

    # Intento 3: Formatos locales (DD/MM/YYYY, DD-MM-YYYY)
    for fmt in ('%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(candidate, fmt).date()
        except ValueError:
            continue

    return None  # Todos los intentos fallaron


def _oldest_allowed_date() -> date:
    """Calcular la fecha más antigua permitida: hoy - LOOKBACK_YEARS (3 años)."""
    today = date.today()
    try:
        return today.replace(year=today.year - LOOKBACK_YEARS)  # Restar 3 años
    except ValueError:
        # Manejo especial para Feb 29 (años bisiestos)
        return today.replace(month=2, day=28, year=today.year - LOOKBACK_YEARS)


def _is_recent_enough(published: date) -> bool:
    """Validar que la fecha esté dentro del rango permitido: últimos 3 años O después de 2022-01-01 (el que sea más flexible)."""
    dynamic_floor = _oldest_allowed_date()  # Hace 3 años
    floor = min(MIN_ALLOWED_DATE, dynamic_floor)  # Usar el más antiguo (menos restrictivo)
    return published >= floor  # Retorna True si la fecha está dentro del rango


def _extract_cert_search_entries(search_html: str) -> list[dict[str, str]]:
    """Parsear resultados de búsqueda de CERT. Extrae: URL, título, contenido, fecha de cada <article>."""
    # Buscar todos los <article class="...">
    article_blocks = re.findall(
        r'<article[^>]*class=["\']([^"\']*)["\'][^>]*>(.*?)</article>',
        search_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    entries: list[dict[str, str]] = []
    for class_value, block in article_blocks:
        # Filtro: Solo posts (no páginas ni otros tipos)
        if 'type-post' not in class_value:
            continue

        # Extraer URL y título (búsqueda en <h1-6 class="entry-title"> <a href>)
        link_match = re.search(
            r'<h[1-6][^>]*class=["\'][^"\']*entry-title[^"\']*["\'][^>]*>\s*'
            r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not link_match:
            continue  # Si no hay link/título, saltar

        # Extraer fecha (búsqueda en <span class="mh-meta-date">)
        date_match = re.search(
            r'<span[^>]*class=["\'][^"\']*mh-meta-date[^"\']*["\'][^>]*>(.*?)</span>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        # Extraer excerpt/contenido (búsqueda en <div class="mh-excerpt"> <p>)
        excerpt_match = re.search(
            r'<div[^>]*class=["\'][^"\']*mh-excerpt[^"\']*["\'][^>]*>\s*<p>(.*?)</p>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Añadir entrada con datos extraídos (fecha y contenido son opcionales)
        entries.append(
            {
                'url': _clean_text(link_match.group(1)),
                'titulo': _clean_text(link_match.group(2)),
                'contenido': _clean_text(excerpt_match.group(1) if excerpt_match else ''),
                'fecha_raw': _clean_text(date_match.group(1) if date_match else ''),
            }
        )

    return entries



# Iteración por palabras clave: Recorre la lista CERT_SEARCH_TERMS ('phishing', 'smishing', 'robo'). 
#  Parsing HTML de resultados (_extract_cert_search_entries): Usa expresiones regulares para rastrear los bloques <article> 
# que contienen la clase type-post (descartando páginas estáticas). 
# De allí extrae:  
#   URL de la noticia (<a href="...">).  
#   Título (<h1-6 class="entry-title">).  
#   Resumen/Snippet (<div class="mh-excerpt">).  
#   Fecha de publicación (<span class="mh-meta-date">).  
# Filtro de URLs: Descarta recursos estáticos (/wp-content/), índices (/category/, /tag/) o rutas excluidas (ej. /soc-cert-py/).

def _scrape_cert_from_search(max_items: int) -> list[dict[str, Any]]:
    """Buscar artículos en CERT Paraguay por términos clave. Enriquece, filtra y valida cada uno."""
    collected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()  # Para evitar duplicados

    # Iterar sobre cada término de búsqueda
    for term in CERT_SEARCH_TERMS:
        search_url = f'{CERT_BASE_URL}/?s={quote_plus(term)}'  # Construir URL de búsqueda
        try:
            search_html = _fetch_xml(search_url)  # Descargar página de búsqueda
        except URLError as exc:
            logger.warning('Failed CERT search request %s: %s', search_url, exc)
            continue  # Si falla, pasar al siguiente término

        # Procesar cada entrada encontrada en la búsqueda
        for row in _extract_cert_search_entries(search_html):
            url = row['url']
            # Si es URL relativa, convertir a absoluta
            if url.startswith('/'):
                url = f'{CERT_BASE_URL}{url}'

            # Validar que la URL sea válida
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                continue

            # Filtro: Excluir rutas administrativas
            if '/wp-content/' in url or '/category/' in url or '/tag/' in url:
                continue

            # Filtro: Excluir paths específicos de CERT
            if any(parsed.path.rstrip('/') == blocked.rstrip('/') for blocked in CERT_EXCLUDED_PATHS):
                continue

            # Filtro: Ya procesamos esta URL antes
            if url in seen_urls:
                continue

            # Parsear la fecha strict (sin fallback a hoy)
            parsed_date = _parse_date_strict(row['fecha_raw'])
            if parsed_date is None:
                continue  # Si no se puede parsear, rechazar

            # Descargar artículo completo y extraer contexto
            enriched_content, article_html = _enrich_article_content_with_html(url, row['contenido'] or DEFAULT_CONTENT)

            # Construir artículo con todos los campos (extrae contexto CON título completo)
            article = {
                'titulo': row['titulo'][:255],
                'contenido': enriched_content[:5000],
                **_extract_attack_context(title=row['titulo'], content=enriched_content, html=article_html),  # Extrae 7 campos
                'fuente': SOURCE_CERT,
                'url': url,
                'fecha': parsed_date,
            }

            # Filtro: Validar que sea reciente
            if not _is_recent_enough(article['fecha']):
                continue

            # Filtro: Validar que sea relevante para Paraguay Y describa un ataque
            if not _passes_article_filters(article):
                continue

            # Si pasó todos los filtros, añadir a resultados
            seen_urls.add(url)
            collected.append(article)

            # Parar cuando alcance max_items
            if len(collected) >= max_items:
                return collected

    return collected


def _scrape_abc_from_search(max_items: int) -> list[dict[str, Any]]:
    """Buscar en ABC Color por términos clave. Paginación con API Queryly. Valida y filtra cada item."""
    items: list[dict[str, Any]] = []
    seen_urls: set[str] = set()  # Evitar duplicados entre queries
    # Distribuir max_items entre las queries (ej: 20 items / 2 queries = 10 por query)
    target_items = max(1, max_items // len(ABC_SEARCH_QUERIES))

    for query in ABC_SEARCH_QUERIES:
        # Si ya alcanzamos max_items, parar
        if len(items) >= max_items:
            break

        # Configurar paginación
        end_index = 0  # Índice para paginación
        batch_size = min(20, target_items)  # Tamaño de batch (máx 20)
        query_items = []  # Items encontrados para esta query

        # Loop de paginación: buscar hasta tener target_items
        while len(query_items) < target_items:
            # Construir URL de búsqueda (API Queryly)
            search_url = (
                f'{ABC_QUERYLY_ENDPOINT}?queryly_key={ABC_QUERYLY_KEY}'
                f'&query={query}&endindex={end_index}&batchsize={batch_size}'
                '&showfaceted=true'
            )

            # Descargar página de búsqueda
            try:
                payload = _fetch_xml(search_url)
            except URLError as exc:
                logger.warning('Failed ABC search request %s: %s', search_url, exc)
                break  # Si falla, pasar a siguiente query

            # Parsear JSON
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as exc:
                logger.warning('Invalid JSON returned from ABC search endpoint: %s', exc)
                break

            # Extraer items del lote
            batch = data.get('items', [])
            if not batch:
                break  # Si no hay resultados, parar paginación

            # Procesar cada item del lote
            for row in batch:
                normalized = _normalize_abc_search_item(row)  # Validar y enriquecer
                if normalized is None:
                    continue  # Si no pasa filtros, saltar

                # Evitar duplicados entre queries
                if normalized['url'] in seen_urls:
                    continue

                query_items.append(normalized)
                seen_urls.add(normalized['url'])
                # Si alcanzó target_items, parar
                if len(query_items) >= target_items:
                    break

            # Avanzar al siguiente lote (paginación)
            end_index += batch_size

        # Añadir items de esta query al total
        items.extend(query_items)

    return items[:max_items]  # Retorna hasta max_items


def scrape_abc_color(max_items: int = 20) -> list[dict[str, Any]]:
    """API pública: Scrape ABC Color. ABC usa solo búsqueda (sin feeds RSS)."""
    # ABC solo busca por "phishing" y "smishing" (sin fallbacks a otros términos)
    return _scrape_abc_from_search(max_items=max_items)


def scrape_cert_py(max_items: int = 20) -> list[dict[str, Any]]:
    """API pública: Scrape CERT Paraguay. CERT usa búsqueda web (no RSS)."""
    return _scrape_cert_from_search(max_items=max_items)


def _build_article_fields(item: dict[str, Any]) -> dict[str, Any]:
    """Helper para construir campos de artículo de manera consistente (evita duplicación)."""
    return {
        'titulo': item['titulo'],
        'contenido': item['contenido'] or DEFAULT_CONTENT,
        'proceso_ataque': item.get('proceso_ataque', ''),
        'secuencia_ataque': item.get('secuencia_ataque', ''),
        'recomendaciones': item.get('recomendaciones', ''),
        'ejemplos_ataque': item.get('ejemplos_ataque', ''),
        'origen_ataque': item.get('origen_ataque', ''),
        'objetivo_ataque': item.get('objetivo_ataque', ''),
        'canal_ataque': item.get('canal_ataque', 'indefinido'),
        'fuente': item['fuente'],
        'fecha': item['fecha'],
    }


def save_articles(articles: list[dict[str, Any]]) -> dict[str, int]:
    """Guardar artículos en BD. Crea nuevos, actualiza existentes (por URL). Retorna estadísticas."""
    created = 0
    skipped = 0  # Actualizados (URLs que ya existían)

    for item in articles:
        # get_or_create: crea si no existe (URL única), obtiene si existe
        articulo, was_created = Articulo.objects.get_or_create(
            url=item['url'],
            defaults=_build_article_fields(item),  # Campos a usar si se crea uno nuevo
        )
        if was_created:
            created += 1
        else:
            # Si ya existe, actualizar todos los campos
            fields = _build_article_fields(item)
            for key, value in fields.items():
                setattr(articulo, key, value)
            articulo.save()
            skipped += 1

    return {'created': created, 'skipped': skipped, 'total': len(articles)}


def run_weekly_ingestion(max_items_per_source: int = 20) -> dict[str, Any]:
    """FUNCIÓN PRINCIPAL: Ejecuta ingestion semanal. Scrape ABC + CERT, guarda en BD, retorna estadísticas."""
    # Scrape de ABC Color
    abc_items = scrape_abc_color(max_items=max_items_per_source)
    # Scrape de CERT Paraguay
    cert_items = scrape_cert_py(max_items=max_items_per_source)

    # Combinar todos los artículos
    all_items = abc_items + cert_items
    # Guardar en BD
    save_result = save_articles(all_items)

    # Retornar estadísticas
    return {
        'abc_count': len(abc_items),
        'cert_count': len(cert_items),
        **save_result,  # Incluye: created, skipped, total
    }


def _normalize_abc_search_item(row: dict[str, Any]) -> dict[str, Any] | None:
    """Validar, enriquecer y filtrar un item de búsqueda de ABC. Retorna artículo normalizado o None si no pasa filtros."""
    # Extraer campos básicos del item
    title = _clean_text(row.get('title', ''))
    description = _clean_text(row.get('description', ''))
    link = _clean_text(row.get('link', ''))
    pubdateunix = row.get('pubdateunix')  # Timestamp Unix

    # Validar que tenga título y link
    if not title or not link:
        return None

    # Convertir URL relativa a absoluta
    if link.startswith('/'):
        link = f'{ABC_BASE_URL}{link}'

    # Validar que la URL sea válida
    parsed = urlparse(link)
    if not parsed.scheme or not parsed.netloc:
        return None

    # Parsear fecha estricta (rechazar si no es válida, consistente con CERT)
    parsed_date: date | None = None
    if pubdateunix:
        try:
            parsed_date = datetime.fromtimestamp(int(pubdateunix), tz=timezone.utc).date()
        except (TypeError, ValueError, OverflowError):
            pass
    if parsed_date is None:
        parsed_date = _parse_date_strict(row.get('pubdate'))
    # Rechazar si no hay fecha válida
    if parsed_date is None:
        return None
    # Validar que sea reciente
    if not _is_recent_enough(parsed_date):
        return None

    # Descargar artículo completo y enriquecer
    enriched_content, article_html = _enrich_article_content_with_html(link, description or DEFAULT_CONTENT)

    # Construir artículo con todos los campos (extrae contexto CON título completo)
    normalized = {
        'titulo': title[:255],
        'contenido': enriched_content[:5000],
        **_extract_attack_context(title=title, content=enriched_content, html=article_html),  # Extrae 7 campos
        'fuente': SOURCE_ABC,
        'url': link,
        'fecha': parsed_date,
    }

    # Filtro final: Validar que sea relevante para Paraguay Y describa un ataque
    if not _passes_article_filters(normalized):
        return None

    return normalized  # Si pasó todos los filtros, retorna


