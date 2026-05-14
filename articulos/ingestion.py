from __future__ import annotations

import json
import logging
import re
import unicodedata
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.error import URLError
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from .models import Articulo

logger = logging.getLogger(__name__)

ABC_BASE_URL = 'https://www.abc.com.py'
ABC_SEARCH_QUERIES = ('phishing', 'smishing')
ABC_QUERYLY_KEY = '33530b56c6aa4c20'
ABC_QUERYLY_ENDPOINT = 'https://api.queryly.com/json.aspx'

CERT_FEEDS = [
    'https://www.cert.gov.py/feed/',
    'https://www.cert.gov.py/?feed=rss2',
]
CERT_BASE_URL = 'https://www.cert.gov.py'
CERT_SEARCH_TERMS = ('phishing', 'smishing', 'robo')
CERT_EXCLUDED_PATHS = (
    '/soc-cert-py/',
)

USER_AGENT = 'treck-ingestion-bot/1.0 (+https://localhost)'
DEFAULT_CONTENT = 'Sin contenido disponible.'
SOURCE_ABC = 'ABC Color'
SOURCE_CERT = 'CERT Paraguay'
LOOKBACK_YEARS = 3
MIN_ALLOWED_DATE = date(2022, 1, 1)

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

ATTACK_FLOW_PATTERNS = (
    r'\bprimero\b.{0,120}\bluego\b',
    r'\bel proceso consiste en\b',
    r'\bel ataque funciona asi\b',
    r'\bpaso a paso\b',
    r'\bcadena de ataque\b',
)

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

SEQUENCE_SENTENCE_MARKERS = (
    'primero',
    'luego',
    'despues',
    'finalmente',
    'el proceso',
    'paso',
)

ORIGIN_MARKERS = (
    'los atacantes',
    'ciberdelincuentes',
    'los estafadores',
    'actores maliciosos',
)

TARGET_MARKERS = (
    'clientes de',
    'usuarios de',
    'personas usuarias',
    'victimas',
)

CHANNEL_PATTERNS = (
    ('whatsapp', ('whatsapp',)),
    ('sms', ('sms', 'mensaje de texto')), 
    ('correo', ('correo electronico', 'email', 'e-mail', 'mail')),
    ('telegram', ('telegram',)),
    ('sitio-web', ('sitio web', 'pagina web', 'enlace', 'url')),
)


def _fetch_xml(url: str, timeout: int = 15) -> str:
    request = Request(url, headers={'User-Agent': USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode('utf-8', errors='replace')


def _clean_text(raw: str | None) -> str:
    value = raw or ''
    # Normalize smart/curly quotes to straight quotes for consistent filtering
    value = value.replace('"', '"').replace('"', '"')  # U+201C, U+201D -> "
    value = value.replace(''', "'").replace(''', "'")  # U+2018, U+2019 -> '
    value = value.replace('«', '"').replace('»', '"')  # U+00AB, U+00BB -> "
    # Remove html tags and collapse spaces to keep a compact RAG context.
    value = re.sub(r'<[^>]+>', ' ', value)
    value = re.sub(r'(?i)\blea\s+m[áa]s\s*:?\s*', ' ', value)
    value = re.sub(r'(?i)\bver\s+m[áa]s\s*:?\s*', ' ', value)
    value = re.sub(r'(?i)\bart[íi]culo\s+relacionado\b.*$', ' ', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def _normalize_for_match(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    normalized = ''.join(ch for ch in normalized if not unicodedata.combining(ch))
    return normalized.lower()


def _split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r'\s+', ' ', text).strip()
    if not cleaned:
        return []
    parts = re.split(r'(?<=[\.!?])\s+', cleaned)
    return [item.strip() for item in parts if len(item.strip()) >= 12]


def _infer_attack_channel(text_normalized: str) -> str:
    for channel, markers in CHANNEL_PATTERNS:
        if any(marker in text_normalized for marker in markers):
            return channel
    return 'indefinido'


def _extract_list_items_from_html(html: str, marker_text: str, max_items: int = 10) -> list[str]:
    """
    Extract list items (<li> elements) from a section in HTML that contains marker text.
    For example: extract all <li> items after "ejemplos son:" or "se recomienda"
    """
    try:
        # Find the section containing the marker
        marker_pattern = re.escape(marker_text)
        section_match = re.search(
            rf'{marker_pattern}.*?(?=<(?:h\d|p|div)[^>]*>|$)',
            html,
            re.IGNORECASE | re.DOTALL
        )
        if not section_match:
            return []
        
        section_html = section_match.group(0)
        
        # Extract all <li> items from this section
        lis = re.findall(r'<li[^>]*>(.*?)</li>', section_html, re.IGNORECASE | re.DOTALL)
        
        # Clean and return
        items = []
        for li in lis[:max_items]:
            cleaned = re.sub(r'<[^>]+>', '', li)
            cleaned = cleaned.replace('&ldquo;', '"').replace('&rdquo;', '"')
            cleaned = cleaned.replace('&lsquo;', "'").replace('&rsquo;', "'")
            cleaned = cleaned.replace('&amp;', '&')
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned:
                items.append(cleaned)
        
        return items
    except Exception:
        return []


def _extract_attack_context(*, title: str, content: str, html: str = '') -> dict[str, str]:
    sentences = _split_sentences(f'{title}. {content}')
    normalized_sentences = [_normalize_for_match(item) for item in sentences]

    process_lines: list[str] = []
    sequence_lines: list[str] = []
    recommendation_lines: list[str] = []
    example_lines: list[str] = []
    origin_line = ''
    target_line = ''
    recommendation_tail = 0

    for raw, normalized in zip(sentences, normalized_sentences):
        if any(keyword in normalized for keyword in ATTACK_ACTION_KEYWORDS) and len(process_lines) < 4:
            process_lines.append(raw)

        if any(marker in normalized for marker in SEQUENCE_SENTENCE_MARKERS) and len(sequence_lines) < 4:
            sequence_lines.append(raw)

        recommendation_triggered = any(keyword in normalized for keyword in RECOMMENDATION_KEYWORDS)
        if recommendation_triggered and len(recommendation_lines) < 4:
            recommendation_lines.append(raw)
            recommendation_tail = 3
            continue

        if any(keyword in normalized for keyword in ('evite', 'evitar', 'prevenir', 'proteja', 'proteccion', 'cambie', 'verifique')) and len(recommendation_lines) < 6:
            if raw not in recommendation_lines:
                recommendation_lines.append(raw)

        if recommendation_tail > 0 and len(recommendation_lines) < 8:
            if raw not in recommendation_lines:
                recommendation_lines.append(raw)
            recommendation_tail -= 1
            continue

        if recommendation_tail > 0:
            recommendation_tail -= 1

        if any(keyword in normalized for keyword in TECHNICAL_OBJECT_KEYWORDS) and len(example_lines) < 4:
            example_lines.append(raw)

        if not origin_line and any(marker in normalized for marker in ORIGIN_MARKERS):
            origin_line = raw

        if not target_line and any(marker in normalized for marker in TARGET_MARKERS):
            target_line = raw

    # Extract structured list items from HTML if available
    if html:
        list_examples = _extract_list_items_from_html(html, 'ejemplos son', max_items=10)
        list_recommendations = _extract_list_items_from_html(html, 'se recomienda', max_items=10)
        
        # Prioritize list items over sentence-based extraction
        if list_examples:
            example_lines.extend(list_examples)
        if list_recommendations:
            recommendation_lines.extend(list_recommendations)

    full_text_normalized = _normalize_for_match(f'{title} {content}')
    channel = _infer_attack_channel(full_text_normalized)

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
    cleaned_html = re.sub(
        r'<(script|style|noscript|svg)[^>]*>.*?</\1>',
        ' ',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    article_match = re.search(r'<article[^>]*>(.*?)</article>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    if article_match:
        cleaned_html = article_match.group(1)

    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    if not paragraphs:
        paragraphs = re.findall(r'<li[^>]*>(.*?)</li>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

    cleaned = [_clean_text(item) for item in paragraphs]
    compact = ' '.join(item for item in cleaned if item)
    return compact[:5000].strip()


def _enrich_article_content(url: str, fallback: str) -> str:
    try:
        html = _fetch_xml(url)
    except (URLError, TimeoutError, ValueError):
        return fallback

    detailed = _extract_paragraph_text(html)
    if not detailed:
        return fallback

    if fallback and fallback not in detailed:
        return f'{fallback} {detailed}'[:5000]
    return detailed[:5000]


def _enrich_article_content_with_html(url: str, fallback: str) -> tuple[str, str]:
    """
    Fetch article content and return both enriched content AND the raw HTML.
    Used to extract structured data like lists.
    Returns: (enriched_content, html)
    """
    try:
        html = _fetch_xml(url)
    except (URLError, TimeoutError, ValueError):
        return (fallback, '')

    detailed = _extract_paragraph_text(html)
    if not detailed:
        return (fallback, html)

    if fallback and fallback not in detailed:
        content = f'{fallback} {detailed}'[:5000]
    else:
        content = detailed[:5000]
    
    return (content, html)


def _is_paraguay_relevant(*, title: str, content: str, url: str) -> bool:
    combined = _normalize_for_match(f'{title} {content}')
    if any(term in combined for term in PARAGUAY_KEYWORDS):
        return True

    if re.search(r'https?://[^\s]+\.py\b', content, flags=re.IGNORECASE):
        return True

    parsed = urlparse(url)
    return parsed.netloc.endswith('.py') or '.com.py' in parsed.netloc


def _has_attack_flow_description(*, title: str, content: str) -> bool:
    text = _normalize_for_match(f'{title} {content}')

    action_hits = sum(1 for keyword in ATTACK_ACTION_KEYWORDS if keyword in text)
    flow_hit = any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in ATTACK_FLOW_PATTERNS)
    technical_hit = any(keyword in text for keyword in TECHNICAL_OBJECT_KEYWORDS)
    operation_hits = sum(1 for keyword in PHISHING_OPERATION_KEYWORDS if keyword in text)

    if flow_hit and action_hits >= 2:
        return True

    if action_hits >= 4:
        return True

    if technical_hit and action_hits >= 2:
        return True

    # CERT often describes campaign mechanics without explicit "primero/luego" wording.
    if operation_hits >= 2:
        return True

    # Educational articles about attack techniques (e.g., "que es smishing") count too
    if technical_hit and operation_hits >= 1:
        return True

    # Any technical hit alone for educational/informational articles
    if technical_hit:
        return True

    return False


def _passes_article_filters(article: dict[str, Any]) -> bool:
    title = str(article.get('titulo', ''))
    content = str(article.get('contenido', ''))
    url = str(article.get('url', ''))

    if not _is_paraguay_relevant(title=title, content=content, url=url):
        return False

    if not _has_attack_flow_description(title=title, content=content):
        return False

    return True


def _parse_date(raw_date: str | None) -> date:
    if not raw_date:
        return date.today()

    try:
        return parsedate_to_datetime(raw_date).date()
    except (TypeError, ValueError, OverflowError):
        return date.today()


def _parse_date_strict(raw_date: str | None) -> date | None:
    if not raw_date:
        return None

    candidate = raw_date.strip()
    if not candidate:
        return None

    # ISO-like datetimes are common in meta tags (e.g. 2025-09-10T08:30:00-03:00).
    iso_candidate = candidate.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(iso_candidate).date()
    except ValueError:
        pass

    try:
        return parsedate_to_datetime(candidate).date()
    except (TypeError, ValueError, OverflowError):
        pass

    for fmt in ('%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(candidate, fmt).date()
        except ValueError:
            continue

    return None


def _oldest_allowed_date() -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - LOOKBACK_YEARS)
    except ValueError:
        # Handles leap-year edge cases like Feb 29.
        return today.replace(month=2, day=28, year=today.year - LOOKBACK_YEARS)


def _is_recent_enough(published: date) -> bool:
    dynamic_floor = _oldest_allowed_date()
    floor = MIN_ALLOWED_DATE if MIN_ALLOWED_DATE < dynamic_floor else dynamic_floor
    return published >= floor


def _parse_rss_items(xml_text: str, fuente: str, max_items: int) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, Any]] = []

    for item in root.findall('.//item'):
        title = _clean_text(item.findtext('title'))
        link = _clean_text(item.findtext('link'))
        description = _clean_text(item.findtext('description'))
        pub_date = _parse_date(item.findtext('pubDate'))

        if not title or not link:
            continue

        if not _is_recent_enough(pub_date):
            continue

        parsed = urlparse(link)
        if not parsed.scheme or not parsed.netloc:
            continue

        items.append(
            {
                'titulo': title[:255],
                'contenido': description[:5000],
                'fuente': fuente,
                'url': link,
                'fecha': pub_date,
            }
        )

        if len(items) >= max_items:
            break

    return items


def _extract_meta_content(html: str, prop: str) -> str:
    pattern = rf'<meta[^>]+(?:property|name)="{re.escape(prop)}"[^>]+content="([^"]+)"'
    match = re.search(pattern, html, flags=re.IGNORECASE)
    return _clean_text(match.group(1)) if match else ''


def _extract_cert_search_entries(search_html: str) -> list[dict[str, str]]:
    article_blocks = re.findall(
        r'<article[^>]*class=["\']([^"\']*)["\'][^>]*>(.*?)</article>',
        search_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    entries: list[dict[str, str]] = []
    for class_value, block in article_blocks:
        # Keep only real posts from WordPress loop, skip pages.
        if 'type-post' not in class_value:
            continue

        link_match = re.search(
            r'<h[1-6][^>]*class=["\'][^"\']*entry-title[^"\']*["\'][^>]*>\s*'
            r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not link_match:
            continue

        date_match = re.search(
            r'<span[^>]*class=["\'][^"\']*mh-meta-date[^"\']*["\'][^>]*>(.*?)</span>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )
        excerpt_match = re.search(
            r'<div[^>]*class=["\'][^"\']*mh-excerpt[^"\']*["\'][^>]*>\s*<p>(.*?)</p>',
            block,
            flags=re.IGNORECASE | re.DOTALL,
        )

        entries.append(
            {
                'url': _clean_text(link_match.group(1)),
                'titulo': _clean_text(link_match.group(2)),
                'contenido': _clean_text(excerpt_match.group(1) if excerpt_match else ''),
                'fecha_raw': _clean_text(date_match.group(1) if date_match else ''),
            }
        )

    return entries


def _scrape_cert_from_search(max_items: int) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for term in CERT_SEARCH_TERMS:
        search_url = f'{CERT_BASE_URL}/?s={quote_plus(term)}'
        try:
            search_html = _fetch_xml(search_url)
        except URLError as exc:
            logger.warning('Failed CERT search request %s: %s', search_url, exc)
            continue

        for row in _extract_cert_search_entries(search_html):
            url = row['url']
            if url.startswith('/'):
                url = f'{CERT_BASE_URL}{url}'

            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                continue

            if '/wp-content/' in url or '/category/' in url or '/tag/' in url:
                continue

            if any(parsed.path.rstrip('/') == blocked.rstrip('/') for blocked in CERT_EXCLUDED_PATHS):
                continue

            if url in seen_urls:
                continue

            parsed_date = _parse_date_strict(row['fecha_raw'])
            if parsed_date is None:
                continue

            enriched_content, article_html = _enrich_article_content_with_html(url, row['contenido'] or DEFAULT_CONTENT)

            article = {
                'titulo': row['titulo'][:255],
                'contenido': enriched_content[:5000],
                **_extract_attack_context(title=row['titulo'], content=enriched_content, html=article_html),
                'fuente': SOURCE_CERT,
                'url': url,
                'fecha': parsed_date,
            }

            if not _is_recent_enough(article['fecha']):
                continue

            if not _passes_article_filters(article):
                continue

            seen_urls.add(url)
            collected.append(article)

            if len(collected) >= max_items:
                return collected

    return collected


def _scrape_abc_from_search(max_items: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    target_items = max(1, max_items // len(ABC_SEARCH_QUERIES))

    for query in ABC_SEARCH_QUERIES:
        if len(items) >= max_items:
            break

        end_index = 0
        batch_size = min(20, target_items)
        query_items = []

        while len(query_items) < target_items:
            search_url = (
                f'{ABC_QUERYLY_ENDPOINT}?queryly_key={ABC_QUERYLY_KEY}'
                f'&query={query}&endindex={end_index}&batchsize={batch_size}'
                '&showfaceted=true'
            )

            try:
                payload = _fetch_xml(search_url)
            except URLError as exc:
                logger.warning('Failed ABC search request %s: %s', search_url, exc)
                break

            try:
                data = json.loads(payload)
            except json.JSONDecodeError as exc:
                logger.warning('Invalid JSON returned from ABC search endpoint: %s', exc)
                break

            batch = data.get('items', [])
            if not batch:
                break

            for row in batch:
                normalized = _normalize_abc_search_item(row)
                if normalized is None:
                    continue

                query_items.append(normalized)
                if len(query_items) >= target_items:
                    break

            end_index += batch_size

        items.extend(query_items)

    return items[:max_items]


def _scrape_from_feeds(feed_urls: list[str], fuente: str, max_items: int) -> list[dict[str, Any]]:
    for feed_url in feed_urls:
        try:
            xml_text = _fetch_xml(feed_url)
            items = _parse_rss_items(xml_text, fuente=fuente, max_items=max_items)
            if items:
                logger.info('Loaded %s items from %s', len(items), feed_url)
                return items
        except (URLError, ET.ParseError, TimeoutError, ValueError) as exc:
            logger.warning('Failed feed %s: %s', feed_url, exc)
            continue

    return []


def scrape_abc_color(max_items: int = 20) -> list[dict[str, Any]]:
    # ABC must use phishing search only (no ciber/ciberseguridad fallback paths).
    return _scrape_abc_from_search(max_items=max_items)


def scrape_cert_py(max_items: int = 20) -> list[dict[str, Any]]:
    return _scrape_cert_from_search(max_items=max_items)


def save_articles(articles: list[dict[str, Any]]) -> dict[str, int]:
    created = 0
    skipped = 0

    for item in articles:
        articulo, was_created = Articulo.objects.get_or_create(
            url=item['url'],
            defaults={
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
            },
        )
        if was_created:
            created += 1
        else:
            articulo.titulo = item['titulo']
            articulo.contenido = item['contenido'] or DEFAULT_CONTENT
            articulo.proceso_ataque = item.get('proceso_ataque', '')
            articulo.secuencia_ataque = item.get('secuencia_ataque', '')
            articulo.recomendaciones = item.get('recomendaciones', '')
            articulo.ejemplos_ataque = item.get('ejemplos_ataque', '')
            articulo.origen_ataque = item.get('origen_ataque', '')
            articulo.objetivo_ataque = item.get('objetivo_ataque', '')
            articulo.canal_ataque = item.get('canal_ataque', 'indefinido')
            articulo.fuente = item['fuente']
            articulo.fecha = item['fecha']
            articulo.save()
            skipped += 1

    return {'created': created, 'skipped': skipped, 'total': len(articles)}


def run_weekly_ingestion(max_items_per_source: int = 20) -> dict[str, Any]:
    abc_items = scrape_abc_color(max_items=max_items_per_source)
    cert_items = scrape_cert_py(max_items=max_items_per_source)

    all_items = abc_items + cert_items
    save_result = save_articles(all_items)

    return {
        'abc_count': len(abc_items),
        'cert_count': len(cert_items),
        **save_result,
    }


def _normalize_abc_search_item(row: dict[str, Any]) -> dict[str, Any] | None:
    title = _clean_text(row.get('title', ''))
    description = _clean_text(row.get('description', ''))
    link = _clean_text(row.get('link', ''))
    pubdateunix = row.get('pubdateunix')

    if not title or not link:
        return None

    if link.startswith('/'):
        link = f'{ABC_BASE_URL}{link}'

    parsed = urlparse(link)
    if not parsed.scheme or not parsed.netloc:
        return None

    parsed_date = _parse_unix_or_text_date(pubdateunix=pubdateunix, fallback=row.get('pubdate'))
    if not _is_recent_enough(parsed_date):
        return None

    enriched_content, article_html = _enrich_article_content_with_html(link, description or DEFAULT_CONTENT)

    normalized = {
        'titulo': title[:255],
        'contenido': enriched_content[:5000],
        **_extract_attack_context(title=title, content=enriched_content, html=article_html),
        'fuente': SOURCE_ABC,
        'url': link,
        'fecha': parsed_date,
    }

    if not _passes_article_filters(normalized):
        return None

    return normalized


def _parse_unix_or_text_date(pubdateunix: Any, fallback: Any) -> date:
    if pubdateunix:
        try:
            return datetime.fromtimestamp(int(pubdateunix), tz=timezone.utc).date()
        except (TypeError, ValueError, OverflowError):
            return date.today()
    return _parse_date(str(fallback or ''))
