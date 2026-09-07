from __future__ import annotations

import json  # Para parsear JSON de APIs
import logging  # Para registrar eventos
import re  # Expresiones regulares
import time  # Backoff entre reintentos HTTP
import unicodedata  # Normalizar caracteres acentuados
from html import unescape as html_unescape  # Decodificar entidades HTML (&#8211; &nbsp; &amp;)
from datetime import date, datetime, timezone  # Manejo de fechas
from email.utils import parsedate_to_datetime  # Parsear fechas en formato email
from typing import Any  # Type hints
from socket import timeout as socket_timeout  # Para compatibilidad con Python < 3.10
from urllib.error import URLError  # Excepciones de red
from urllib.parse import quote_plus, urlparse  # Codificar URLs y extraer componentes
from urllib.request import Request, urlopen  # Descargar contenido HTTP, esto se encarga de hacer requests HTTP y manejar redirecciones, etc.

try:
    from openai import OpenAI  # Cliente OpenAI para ChatGPT
except ImportError:
    OpenAI = None

from .models import Articulo  # Modelo Django para guardar artículos

logger = logging.getLogger(__name__)  # Logger para registrar eventos de este módulo



# [1. Petición HTTP] ──> [2. Extracción & Búsqueda] ──> [3. Enriquecimiento] ──> [4. Guardado en DB]


# 2. Solo extrae Un título, Un enlace (URL) y Un snippet (un fragmento corto de 1 o 2 oraciones).
# ============== CONFIGURACIÓN DE FUENTES ==============
# ABC Color - búsqueda por API Queryly
ABC_BASE_URL = 'https://www.abc.com.py'
ABC_SEARCH_QUERIES = (
    'phishing',
    'smishing',
    'vishing',
    'ciberestafa',
    'estafa bancaria',
    'suplantacion de identidad',
    'vaciamiento de cuenta',
    'correo falso',
    'robo de cuentas',
    'fraude electronico',
)
ABC_QUERYLY_KEY = '33530b56c6aa4c20'  # API key para búsqueda
ABC_QUERYLY_ENDPOINT = 'https://api.queryly.com/json.aspx'  # Endpoint de búsqueda
ABC_MAX_PAGES_PER_QUERY = 2  # Cota de páginas: evita loops infinitos si todo se rechaza

# CERT Paraguay - búsqueda por web scraping
CERT_BASE_URL = 'https://www.cert.gov.py'
CERT_SEARCH_TERMS = (
    'phishing',
    'smishing',
    'vishing',
    'suplantacion',
    'correo fraudulento',
    'robo de credenciales',
    'ingenieria social',
    'estafa',
)
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
    'paraguayos',
    'paraguayas',
    'asuncion',
    'asunción',
    'encarnacion',
    'encarnación',
    'ciudad del este',
    'ministerio publico',
    'ministerio público',
    'poder judicial',
    'corte suprema de justicia',
    'corte suprema',
    'policia nacional',
    'policía nacional',
    'cert py',
    'cert.gov.py',
    'cert paraguay',
    'banco del paraguay',
    'banco paraguayo',
    'banco central',
    'itaipú',
    'itaipu',
    'rio parana',
    'río paraná',
    'aeropuerto silvio pettirossi',
    'silvio pettirossi',
    'tenaris',
    'industrias paraguayas',
    'empresa paraguaya',
    'empresas paraguayas',
    'bancos paraguayos',
    'gobierno paraguayo',
    'senatur',
    'setec',
    'dinac',
    'aduana',
    'impuestos internos',
)

# Acciones específicas de phishing que hacen los atacantes
# (SOLO: envían, redirigen, suplantan, capturan credenciales - los atacantes siempre)
ATTACK_ACTION_KEYWORDS = (
    'los atacantes',
    'el atacante',
    'atacantes',
    'envian',
    'envia',
    'envía',
    'redirigen',
    'redirige',
    'suplantan',
    'suplanta',
    'hacen pasar',
    'hace pasar',
    'capturan credenciales',
    'captura de credenciales',
    'roban credenciales',
    'robo de credenciales',
    'solicita datos',
    'solicitan datos',
    'solicita credenciales',
    'solicitan credenciales',
    'pide datos',
    'piden datos',
)

# Patrones regex para detectar flujos de ataque (primero...luego, paso a paso)
ATTACK_FLOW_PATTERNS = (
    r'\bprimero\b.{0,120}\bluego\b',  # "primero X luego Y"
    r'\bprimero\b.{0,120}\bdespues\b|\bdespués\b',  # "primero X después Y"
    r'\bel proceso consiste en\b',  # "el proceso consiste en"
    r'\bel ataque funciona\b',  # "el ataque funciona"
    r'\bel ataque trabaja\b',  # "el ataque trabaja"
    r'\bcomo funciona\b',  # "cómo funciona"
    r'\bpaso a paso\b',  # "paso a paso"
    r'\bpaso 1\b|\bpaso 2\b|\bpaso 3\b',  # "paso 1, paso 2, etc"
    r'\bcadena de ataque\b',  # "cadena de ataque"
    r'\bsecuencia de\b',  # "secuencia de"
    r'\bflujo de\b',  # "flujo de"
    r'\be luego\b',  # "e luego"
    r'\baseguir\b|\ba continuacion\b|\ba continuación\b',  # "a continuación"
    r'\bllamadas consecutivas\b',  # "llamadas consecutivas"
    r'\ben este orden\b',  # "en este orden"
)

# Palabras específicas sobre operaciones phishing/smishing
PHISHING_OPERATION_KEYWORDS = (
    'campana de phishing',
    'campaña de phishing',
    'correo falso',
    'correo fraudulento',
    'mensaje fraudulento',
    'sitio falso',
    'pagina falsa',
    'página falsa',
    'sitio clonado',
    'pagina clonada',
    'página clonada',
    'captura de credenciales',
    'robo de credenciales',
    'suplantacion de identidad',
    'suplantación de identidad',
    'enlace malicioso',
    'url maliciosa',
    'URL maliciosa',
    'bancos paraguayos',
    'campana de smishing',
    'campaña de smishing',
    'sms falso',
    'sms fraudulento',
    'mensaje de texto falso',
    'suplantacion por sms',
    'suplantación por SMS',
    'fraude electronico',
    'fraude electrónico',
    'ciberataque',
    'ciberdelincuentes',
    'delincuentes ciberneticos',
    'delincuentes cibernéticos',
    'estafadores en linea',
    'estafadores en línea',
    'ofertas falsas',
    'promocion falsa',
    'promoción falsa',
    'descuento falso',
)

# TÁCTICAS DE PHISHING PURO - Solo lo relevante para generar simulaciones realistas
# (Eliminado: certificados, IPs, servidores, tokens, scripts, plugins - son detalles técnicos irrelevantes)
PHISHING_TACTICS_KEYWORDS = (
    'enlaces falsos',
    'enlace falso',
    'enlace malicioso',
    'pagina clonada',
    'página clonada',
    'paginas clonadas',
    'páginas clonadas',
    'qr malicioso',
    'codigo qr malicioso',
    'código QR malicioso',
    'quishing',
    'deepfake de voz',
    'deepfake',
    'sms spoofing',
    'sms clonado',
    'spoof de sms',
    'spoofing',
    'enlace en sms',
    'url acortada',
    'url acortada',
    'bit.ly',
    'tinyurl',
    'shorturl',
    'formulario falso',
    'formulario malicioso',
    'sitio malicioso',
    'pagina maliciosa',
    'página maliciosa',
    'dominio falso',
    'dominio clonado',
    'correo falso',
    'correo malicioso',
    'sms falso',
    'sms malicioso',
    'mensaje falso',
    'mensaje malicioso',
    'notificacion falsa',
    'notificación falsa',
    'alerta falsa',
    'codigo de verificacion falso',
    'código de verificación falso',
    'otp falso',
    'sesion falsa',
    'sesión falsa',
    'app falsa',
)

# Nuevas palabras clave: Ingeniería social y tácticas de manipulación
SOCIAL_ENGINEERING_KEYWORDS = (
    'presion psicologica',
    'presión psicológica',
    'presion temporal',
    'presión temporal',
    'urgencia',
    'urgente',
    'ahora mismo',
    'inmediatamente',
    'crear urgencia',
    'genera urgencia',
    'amenaza',
    'amenaza de',
    'amenaza implícita',
    'suplantacion de identidad',
    'suplantación de identidad',
    'se hace pasar',
    'hace pasar por',
    'falsa confianza',
    'genera confianza',
    'manipulacion psicologica',
    'manipulación psicológica',
    'explotacion de confianza',
    'explotación de confianza',
    'solicita datos personales',
    'solicita datos sensibles',
    'solicita credenciales de acceso',
    'redacta como',
    'redacta mensajes falsos',
    'cuerpo del mensaje',
    'contenido del mensaje',
    'tono de autoridad',
    'se presenta como autoridad',
    'crea miedo',
    'genera miedo',
    'promesa falsa',
    'promesas falsas',
    'oferta falsa',
    'oferta engañosa',
    'descuento falso',
    'oferta irresistible',
    'recompensa falsa',
    'premios falsos',
    'cuenta bloqueada',
    'acceso suspendido',
    'actualización obligatoria',
    'acción inmediata',
    'engaña',
    'engañan',
    'convence',
    'convencen',
    'presiona',
    'presionan',
    'falsifica',
    'imita',
    'copia',
)

# Palabras de recomendación de seguridad
RECOMMENDATION_KEYWORDS = (
    'se recomienda',
    'recomendamos',
    'se aconseja',
    'aconsejamos',
    'no haga clic',
    'no hacer clic',
    'no compartir',
    'no comparta',
    'verifique',
    'verificar',
    'verificacion',
    'verificación',
    'activar',
    'activa',
    'activado',
    'doble factor',
    'autenticacion de dos factores',
    'autenticación de dos factores',
    '2fa',
    'reportar',
    'reporte',
    'denunciar',
    'denuncia',
    'como evitar',
    'cómo evitar',
    'evitar este ataque',
    'prevenir',
    'prevenga',
    'prevencion',
    'prevención',
    'proteja',
    'protege',
    'proteccion',
    'protección',
    'cambiar contraseña',
    'cambiar contrasena',
    'reseteando',
    'actualizar',
    'actualice',
    'configurar',
    'configure',
    'vigile',
    'vigil',
    'cuidado',
    'cuidese',
    'cuidadoso',
    'precaucion',
    'precaución',
    'no proporcione',
    'no proporcionar',
    'no ingrese',
    'no compartir',
    'desconfiar',
    'desconfiado',
    'sospechar',
    'sospecha',
    'validacion',
    'validación',
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
    'atacantes',
    'ciberdelincuentes',
    'los estafadores',
    'estafadores',
    'actores maliciosos',
    'actores ciberneticos',
    'actores cibernéticos',
    'grupos de',
    'grupo criminal',
    'delincuentes',
    'criminales',
    'maliciosos',
    'redes de fraude',
    'banda de',
    'organizacion criminal',
    'organización criminal',
)

# Palabras que identifican el objetivo del ataque
TARGET_MARKERS = (
    'clientes de',
    'usuarios de',
    'personas usuarias',
    'victimas',
    'víctimas',
    'usuarios de',
    'clientes de',
    'afectados',
    'afectadas',
    'personas afectadas',
    'residentes de',
    'habitantes de',
    'ciudadanos de',
    'empresas',
    'empresarios',
    'profesionales de',
    'trabajadores de',
    'personas mayores',
    'adultos mayores',
)

# Canales de ataque (tupla: nombre -> palabras clave)
CHANNEL_PATTERNS = (
    ('whatsapp', ('whatsapp',)),
    ('sms', ('sms', 'mensaje de texto')),
    ('correo', ('correo electronico', 'email', 'e-mail', 'mail')),
    ('telegram', ('telegram',)),
    ('sitio-web', ('sitio web', 'pagina web', 'enlace', 'url')),
)

# Patrones de boilerplate de portales (newsletters, promos, metadata)
BOILERPLATE_PATTERNS = (
    r'\bunite\s+al\s+canal\s+de\s+\w+\s+en\s+\w+\b',  # "Unite al canal de ABC en WhatsApp"
    r'\bdescargu?e?\s+la\s+app\b',  # "Descargue la app"
    r'\bsiguien?do?\s+(la\s+)?cuenta\b',  # "Siguiendo la cuenta", "Seguí la cuenta"
    r'\bsuscrib[íe]te?\s+a\s+\w+\b',  # "Suscríbete a", "Suscribite a"
    r'\b\d{1,2}/\d{1,2}/\d{4}\s+(noticias|avisos|alertas)\s+\d+\b',  # "01/06/2022 Noticias 0"
    r'\[\.{3}\]|\[\…\]',  # "[...]" "[…]" (teaser truncado)
    r'\bseguir(nos)?\s+en\b',  # "Seguir en", "Seguirnos en"
    r'\bleer\s+m[aá]s\b',  # "Leer más"
    r'\bver\s+m[aá]s\b',  # "Ver más"
    r'\bcontinuar\s+leyendo\b',  # "Continuar leyendo"
)

# Señales de que el artículo es sobre phishing (no solo menciona la palabra)
PHISHING_TOPIC_TERMS = (
    'phishing', 'smishing', 'vishing', 'quishing', 'ciberestafa', 'suplantacion de identidad',
    'correo falso', 'robo de credenciales', 'vaciamiento de cuenta', 'ingenieria social',
    'estafa bancaria', 'fraude electronico', 'campaña de phishing', 'ataque de phishing',
)

# Penalizaciones: vulnerabilidades técnicas de producto (CVEs, configuraciones, servidores)
TECHNICAL_VULN_TERMS = (
    'cve-', 'vulnerabilidad en productos', 'ejecucion remota de codigo', 'inyeccion sql',
    'sql injection', 'xss attack', 'cross-site scripting', 'buffer overflow',
    'path traversal', 'rce ', 'remote code', 'brute force attack', 'ddos',
    'zero-day', 'exploit publico', 'no autenticado', 'bypass de autenticacion',
    'usuario no autenticado',
)

# Penalizaciones: malware / infraestructura técnica (no es phishing puro)
MALWARE_TECH_TERMS = (
    'malware', 'troyano', 'ransomware', 'cadena de infeccion', 'backdoor', 'botnet',
    'rootkit', 'spyware', 'gusano informatico', 'servidor linux', 'windows server', 'apache',
)

# Penalizaciones: operativos policiales (informan detenciones, no modus operandi)
LAW_ENFORCEMENT_TERMS = (
    'interpol', 'europol', 'extraditan', 'extradicion', 'detenidos', 'detenciones',
    'desarticulan', 'desarticulada', 'condenado a', 'condenados a', 'golpe mundial',
    'operacion internacional', 'imputado por',
)

# Penalizaciones: artículos enfocados en otros países (sin ángulo Paraguay)
FOREIGN_FOCUS_TERMS = (
    'en mexico', 'en brasil', 'en estados unidos', 'en argentina', 'en chile',
    'en españa', 'en europa', 'en asia', 'en china', 'en rusia', 'en africa',
)

# Umbrales de relevancia
MIN_RELEVANCE_SCORE = 5  # Puntaje mínimo para aceptar artículo
MIN_EXTRACTED_MATERIAL = 200  # Mínimo de caracteres en campos extraídos


def _fetch_xml(url: str, timeout: int = 5) -> str:
    """Descargar HTML/XML desde una URL. Retorna string decodificado UTF-8."""
    request = Request(url, headers={'User-Agent': USER_AGENT})  # Crear request con User-Agent
    with urlopen(request, timeout=timeout) as response:  # Abrir URL con timeout
        return response.read().decode('utf-8', errors='replace')  # Decodificar ignorando errores


def _clean_text(raw: str | None) -> str:
    """Limpiar texto: HTML entities, boilerplate, quotes. Retorna texto limpio."""
    value = raw or ''
    # Decodificar entidades HTML (&#8211; -> –, &nbsp; -> espacio, &amp; -> &, etc)
    value = html_unescape(value)
    # Normalizar espacios no-quebrantes
    value = value.replace('\xa0', ' ')
    # Normalizar guiones tipográficos a ASCII
    value = value.replace('–', '-').replace('—', '-')  # U+2013, U+2014 -> -
    value = value.replace('…', '...')  # U+2026 -> ...
    # Eliminar boilerplate de portales
    for pattern in BOILERPLATE_PATTERNS:
        value = re.sub(pattern, ' ', value, flags=re.IGNORECASE)
    # Normalizar comillas curvas/inteligentes a rectas
    value = value.replace('"', '"').replace('"', '"')  # U+201C, U+201D -> "
    value = value.replace(''', "'").replace(''', "'")  # U+2018, U+2019 -> '
    value = value.replace('«', '"').replace('»', '"')  # U+00AB, U+00BB -> "
    # Eliminar etiquetas HTML
    value = re.sub(r'<[^>]+>', ' ', value)
    # Eliminar frases de navegación y "Lea más"
    value = re.sub(r'(?i)\blea\s+m[áa]s\s*:?\s*', ' ', value)
    value = re.sub(r'(?i)\bver\s+m[áa]s\s*:?\s*', ' ', value)
    value = re.sub(r'(?i)\bart[íi]culo\s+relacionado\b.*$', ' ', value)
    value = re.sub(r'(?i)\bcompartir\b.*?(?=\s[a-z]|\s|$)', ' ', value)
    value = re.sub(r'(?i)\bsiguiente\b', ' ', value)
    value = re.sub(r'(?i)\banterior\b', ' ', value)
    value = re.sub(r'(?i)\bvolver\b.*?(?=\s[a-z]|\s|$)', ' ', value)
    # Eliminar fechas de publicación y metadata
    value = re.sub(r'(?i)\b(publicado|escrito|por|autor|autora|en)\s+(el\s+)?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', ' ', value)
    value = re.sub(r'(?i)\b(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo).*?\d{1,2}\s+(de\s+)?\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b', ' ', value)
    # Eliminar referencias a comentarios, likes, shares
    value = re.sub(r'(?i)\b(\d+\s+)?(comentarios?|likes?|compartidas?|comentado|liked)\b', ' ', value)
    # Colapsar espacios múltiples y recortar
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def _normalize_for_match(text: str) -> str:
    """Normalizar para búsquedas: quitar acentos y convertir a minúsculas."""
    normalized = unicodedata.normalize('NFKD', text)  # Descomponer acentos
    normalized = ''.join(ch for ch in normalized if not unicodedata.combining(ch))  # Quitar marcas diacríticas
    return normalized.lower()  # Convertir a minúsculas


def _split_sentences(text: str) -> list[str]:
    """Dividir texto en oraciones. Solo retorna oraciones con ≥15 caracteres."""
    cleaned = re.sub(r'\s+', ' ', text).strip()  # Colapsar espacios
    if not cleaned:
        return []
    parts = re.split(r'(?<=[\.!?])\s+', cleaned)  # Dividir por . ! ?
    sentences = [item.strip() for item in parts if len(item.strip()) >= 15]  # Filtrar por longitud (15 chars)
    return sentences


def _is_generic_sentence(text: str) -> bool:
    """Detectar si una oración es demasiado genérica o no relevante. Retorna True si es genérica."""
    normalized = _normalize_for_match(text)
    # Frases genéricas que no aportan sobre el ataque
    generic_patterns = (
        r'\bes importante\b',
        r'\bse recomienda estar alerta\b',
        r'\bse debe tener cuidado\b',
        r'\btodos debemos\b',
        r'\brecuerde que\b',
        r'\bcomo siempre\b',
        r'\ben conclusi[óo]n\b',
        r'\bpara finalizar\b',
        r'\bademas\b|\bademás\b',
        r'\bsiguiente\b',
        r'\banterior\b',
        r'^[a-z\s]{1,20}$',  # Muy corta (menos de 20 caracteres, después de filtrar)
    )
    return any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in generic_patterns)


def _calculate_string_similarity(s1: str, s2: str) -> float:
    """Calcular similitud entre dos strings. Retorna valor entre 0 y 1."""
    s1_norm = _normalize_for_match(s1)
    s2_norm = _normalize_for_match(s2)

    # Si uno contiene al otro, son muy similares
    if s1_norm in s2_norm or s2_norm in s1_norm:
        return 0.9

    # Calcular similitud simple basada en palabras comunes
    words1 = set(s1_norm.split())
    words2 = set(s2_norm.split())

    if not words1 or not words2:
        return 0.0

    common = len(words1 & words2)
    total = len(words1 | words2)

    return common / total if total > 0 else 0.0


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
            cleaned = cleaned.replace('&lt;', '<').replace('&gt;', '>')
            cleaned = cleaned.replace('&quot;', '"').replace('&#039;', "'")
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Colapsar espacios
            # Filtrar items muy cortos (menos de 10 caracteres = ruido)
            if cleaned and len(cleaned) >= 10:
                items.append(cleaned)

        return items
    except (IndexError, AttributeError, ValueError, re.error) as exc:
        logger.warning('Failed to extract list items from HTML: %s', exc)
        return []  # En caso de error, retorna lista vacía


def _extract_attack_context_with_ai(*, content: str) -> dict[str, Any] | None:
    """Usar ChatGPT para extraer campos de ataque phishing desde el contenido limpio.

    Retorna dict con los 7 campos o None si falla.
    """
    if not OpenAI:
        logger.warning('OpenAI no está disponible, usando extracción por regex')
        return None

    if not content or len(content) < 100:
        return None

    try:
        client = OpenAI()  # Usa OPENAI_API_KEY de entorno

        prompt = f"""Analiza el siguiente artículo sobre phishing y extrae la información en JSON estructurado.

CONTENIDO DEL ARTÍCULO:
{content[:3000]}

Extrae estos campos en JSON (usa strings vacíos si no encontras información):
- proceso_ataque: Descripción del proceso/flujo del ataque phishing
- secuencia_ataque: Pasos secuenciales (primero..., luego..., después...)
- ejemplos_ataque: Ejemplos concretos de tácticas o mensajes
- origen_ataque: Dónde/qué entidad se origina el ataque (país, organización, región afectada, etc)
- objetivo_ataque: A quién va dirigido el ataque (víctimas, usuarios, empresas, etc)
- canal_ataque: Por qué canal se ejecuta (correo, SMS, WhatsApp, etc)
- recomendaciones: Recomendaciones para prevenirlo o evitarlo

Responde SOLO con JSON válido, sin markdown ni explicaciones adicionales."""

        response = client.chat.completions.create(
            model='gpt-4o-mini',  # Rápido y económico
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=1000,
        )

        # Parsear respuesta
        response_text = response.choices[0].message.content.strip()

        # Si tiene markdown code blocks, extraer JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        result = json.loads(response_text)
        return result

    except Exception as e:
        logger.error('Error en extracción con IA: %s', e)
        return None


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

    def _is_too_similar(text: str, existing_list: list[str], threshold: float = 0.75) -> bool:
        """Verificar si el texto es demasiado similar a algo en la lista existente."""
        for item in existing_list:
            if _calculate_string_similarity(text, item) >= threshold:
                return True
        return False

    # Iterar sobre cada oración y clasificarla
    for raw, normalized in zip(sentences, normalized_sentences):
        # Saltar si es demasiado genérica
        if _is_generic_sentence(raw):
            continue

        # PHISHING PURO: Capturar TÁCTICAS de ingeniería social + acciones de atacante
        has_phishing_tactic = any(tactic in normalized for tactic in PHISHING_TACTICS_KEYWORDS)
        has_social_eng = any(tactic in normalized for tactic in SOCIAL_ENGINEERING_KEYWORDS)
        has_action = any(keyword in normalized for keyword in ATTACK_ACTION_KEYWORDS)

        # Captura: acciones de atacante OR tácticas phishing OR ingeniería social
        if (has_action or has_phishing_tactic or has_social_eng) and len(process_lines) < 8:
            if not _is_too_similar(raw, process_lines, 0.8):
                process_lines.append(raw)

        # MEJORA ENFOCADA: Capturar SECUENCIA DE PHISHING (cómo ocurre el ataque)
        # Palabras clave para describir "cómo" ocurre el phishing paso a paso
        sequence_keywords = [
            'primero', 'luego', 'después', 'entonces', 'a continuacion',
            'siguiendo', 'paso', 'pasos', '1.', '2.', '3.',
            'recibe', 'hace clic', 'ingresa', 'completa', 'accede',
            'es redirigido', 'lleva a', 'abre', 'descarga', 'instala',
            'captura', 'obtiene', 'roba', 'extrae'
        ]

        has_sequence = any(kw in normalized for kw in sequence_keywords)

        if has_sequence and len(sequence_lines) < 8:
            if not _is_too_similar(raw, sequence_lines, 0.8):
                sequence_lines.append(raw)

        # Si detecta recomendación, añade y prepara para capturar oraciones siguientes
        recommendation_triggered = any(keyword in normalized for keyword in RECOMMENDATION_KEYWORDS)
        if recommendation_triggered and len(recommendation_lines) < 5:
            if not _is_too_similar(raw, recommendation_lines, 0.8):
                recommendation_lines.append(raw)
            recommendation_tail = 2  # Capturar las próximas 2 oraciones (reducido de 3)
            continue

        # Capturar variantes de "evite", "prevenir", etc.
        prevention_keywords = ('evite', 'evitar', 'prevenir', 'proteja', 'proteccion', 'cambie', 'verifique', 'configure', 'actualice', 'vigile')
        if any(keyword in normalized for keyword in prevention_keywords) and len(recommendation_lines) < 8:
            if not _is_too_similar(raw, recommendation_lines, 0.8):
                recommendation_lines.append(raw)

        # Si estamos en la "cola" de recomendaciones (2 oraciones después), añadir
        if recommendation_tail > 0 and len(recommendation_lines) < 10:
            if not _is_generic_sentence(raw) and not _is_too_similar(raw, recommendation_lines, 0.8):
                recommendation_lines.append(raw)
            recommendation_tail -= 1
            continue

        # Decrementar el contador de cola
        if recommendation_tail > 0:
            recommendation_tail -= 1

        # Capturar tácticas de phishing mencionadas (ejemplos concretos de phishing)
        if any(keyword in normalized for keyword in PHISHING_TACTICS_KEYWORDS) and len(example_lines) < 6:
            if not _is_too_similar(raw, example_lines, 0.8):
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


def _is_boilerplate_paragraph(text: str) -> bool:
    """Detectar párrafos que son solo promoción/navegación del portal, no contenido."""
    normalized = _normalize_for_match(text)

    # Párrafos cortos que mencionan redes sociales o suscripción = promo
    promo_terms = (
        'whatsapp', 'telegram', 'facebook', 'instagram', 'twitter', 'suscri',
        'newsletter', 'boletin', 'descarga la app', 'seguinos', 'siguenos',
    )
    if len(text) < 120 and any(term in normalized for term in promo_terms):
        return True

    # Solo metadata: fecha + categoría + contador
    if re.fullmatch(r'[\d/\-\s]+(noticias|alertas|avisos)?\s*\d*', normalized.strip()):
        return True

    # Teaser de nota relacionada: termina en "[...]" o "[…]"
    if normalized.rstrip().endswith('[...]') or normalized.rstrip().endswith('[…]'):
        return True

    return False


def _extract_paragraph_text(html: str) -> str:
    """Extraer texto limpio de párrafos HTML. Retorna hasta 5000 caracteres."""
    # Eliminar scripts, styles, SVGs, comentarios
    cleaned_html = re.sub(
        r'<(script|style|noscript|svg)[^>]*>.*?</\1>',
        ' ',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    # Eliminar comentarios HTML
    cleaned_html = re.sub(r'<!--.*?-->', ' ', cleaned_html, flags=re.DOTALL)
    # Eliminar navegación, footers, sidebars, widgets
    cleaned_html = re.sub(
        r'<(nav|footer|aside|[^>]*class=["\'].*?(sidebar|widget|nav|menu|footer|advertisement|ads?)["\'][^>]*)[^>]*>.*?</\1>',
        ' ',
        cleaned_html,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Si hay <article>, usar solo eso (descarta navegación, headers, etc.)
    article_match = re.search(r'<article[^>]*>(.*?)</article>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    if article_match:
        cleaned_html = article_match.group(1)
    # Si no hay article, buscar main
    else:
        main_match = re.search(r'<main[^>]*>(.*?)</main>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
        if main_match:
            cleaned_html = main_match.group(1)

    # Extraer párrafos <p> (máximo 50 para evitar basura)
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
    # Si no hay párrafos suficientes, intentar con <li> (pero máximo 20)
    if len(paragraphs) < 5:
        list_items = re.findall(r'<li[^>]*>(.*?)</li>', cleaned_html, flags=re.IGNORECASE | re.DOTALL)
        paragraphs.extend(list_items[:20])

    # Limpiar cada párrafo
    cleaned = [_clean_text(item) for item in paragraphs[:50]]
    # Filtrar párrafos muy cortos (menos de 15 caracteres = ruido)
    cleaned = [item for item in cleaned if item and len(item) > 14]
    # Filtrar párrafos que son puramente boilerplate/promocionales
    cleaned = [item for item in cleaned if not _is_boilerplate_paragraph(item)]
    # Concatenar, eliminar vacíos, truncar a 15000 caracteres
    compact = ' '.join(item for item in cleaned if item)
    return compact[:15000].strip()


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
    """Validar si describe un FLUJO DE PHISHING PURO. Requiere: tácticas de ingeniería social O flujo explícito."""
    text = _normalize_for_match(f'{title} {content}')

    # Contar evidencia de phishing puro
    action_hits = sum(1 for keyword in ATTACK_ACTION_KEYWORDS if keyword in text)  # Qué hacen los atacantes
    flow_hit = any(re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL) for pattern in ATTACK_FLOW_PATTERNS)  # Pasos
    tactics_hit = sum(1 for keyword in PHISHING_TACTICS_KEYWORDS if keyword in text)  # Tácticas phishing
    social_eng_hits = sum(1 for keyword in SOCIAL_ENGINEERING_KEYWORDS if keyword in text)  # Ingeniería social
    operation_hits = sum(1 for keyword in PHISHING_OPERATION_KEYWORDS if keyword in text)  # Operaciones phishing

    # ✅ CRITERIO 1: Flujo explícito + ≥2 acciones de atacante
    if flow_hit and action_hits >= 2:
        return True

    # ✅ CRITERIO 2: ≥3 acciones de atacante (describe qué hace el atacante)
    if action_hits >= 3:
        return True

    # ✅ CRITERIO 3: Tácticas de phishing + ≥2 acciones
    if tactics_hit >= 1 and action_hits >= 2:
        return True

    # ✅ CRITERIO 4: ≥2 palabras de ingeniería social (presión, urgencia, miedo)
    if social_eng_hits >= 2:
        return True

    # ✅ CRITERIO 5: Operación phishing bien documentada + tácticas
    if operation_hits >= 1 and (tactics_hit >= 1 or social_eng_hits >= 1):
        return True

    # ✅ CRITERIO 6: Flujo explícito + táctica phishing (incluso sin acciones explícitas)
    if flow_hit and tactics_hit >= 1:
        return True

    return False  # No es phishing puro


def _calculate_relevance_score(*, title: str, content: str, url: str) -> int:
    """Puntaje estricto de relevancia phishing. Suma señales, resta ruido.

    Retorna int: positivo = relevante, negativo/bajo = rechazar.
    """
    combined = _normalize_for_match(f'{title} {content} {url}')
    title_normalized = _normalize_for_match(title)
    score = 0

    # (+) Señales de phishing en TÍTULO: +3 c/u (máx 6, ponderado fuerte)
    title_topic_hits = sum(1 for term in PHISHING_TOPIC_TERMS if term in title_normalized)
    score += min(title_topic_hits * 3, 6)

    # (+) Señales de phishing en CONTENIDO: +1 c/u (máx 4)
    content_topic_hits = sum(1 for term in PHISHING_TOPIC_TERMS if term in combined)
    score += min(content_topic_hits, 4)

    # (+) Tácticas de ingeniería social: +1 c/u (máx 2)
    tactic_hits = sum(1 for term in PHISHING_TACTICS_KEYWORDS if term in combined)
    score += min(tactic_hits, 2)

    # (+) Acciones de atacante: +1 c/u (máx 2)
    action_hits = sum(1 for term in ATTACK_ACTION_KEYWORDS if term in combined)
    score += min(action_hits, 2)

    # (+) Paraguay mencionado en TEXTO: +3 (crucial para ABC que dice "phishing" de todo el mundo)
    if any(term in combined for term in PARAGUAY_KEYWORDS):
        score += 3

    # (-) Vulnerabilidad técnica: −4 c/u
    vuln_hits = sum(1 for term in TECHNICAL_VULN_TERMS if term in combined)
    score -= vuln_hits * 4

    # (-) Malware sin ángulo phishing: −4 c/u
    if title_topic_hits == 0:  # Si el título no dice "phishing", penalizar malware
        malware_hits = sum(1 for term in MALWARE_TECH_TERMS if term in combined)
        score -= malware_hits * 4

    # (-) Operativo policial: −5 c/u (siempre, describe detenciones no modus operandi)
    enforcement_hits = sum(1 for term in LAW_ENFORCEMENT_TERMS if term in title_normalized)
    score -= enforcement_hits * 5

    # (-) Foco extranjero SIN mención de Paraguay: −4 c/u
    has_paraguay = any(term in combined for term in PARAGUAY_KEYWORDS)
    if not has_paraguay:
        foreign_hits = sum(1 for term in FOREIGN_FOCUS_TERMS if term in combined)
        score -= foreign_hits * 4

    # (-) Sin ninguna señal phishing: −10 (automático rechazo)
    if title_topic_hits == 0 and content_topic_hits == 0:
        score -= 10

    return score


def _passes_article_filters(article: dict[str, Any]) -> bool:
    """Validar 4 filtros: Paraguay + puntaje + flujo + sustancia. CALIDAD antes que cantidad."""
    title = str(article.get('titulo', ''))
    content = str(article.get('contenido', ''))
    url = str(article.get('url', ''))

    # Filtro 1: Relevancia Paraguay
    if not _is_paraguay_relevant(title=title, content=content, url=url):
        return False

    # Filtro 2: Puntaje de relevancia estricto
    score = _calculate_relevance_score(title=title, content=content, url=url)
    if score < MIN_RELEVANCE_SCORE:
        return False

    # Filtro 3: Describe flujo de ataque
    if not _has_attack_flow_description(title=title, content=content):
        return False

    # Filtro 4: Material utilizable (proceso + secuencia + ejemplos ≥ 200 chars)
    material = (
        len(str(article.get('proceso_ataque', '')))
        + len(str(article.get('secuencia_ataque', '')))
        + len(str(article.get('ejemplos_ataque', '')))
    )
    if material < MIN_EXTRACTED_MATERIAL:
        return False

    return True  # Pasó los 4 filtros


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

            # Intentar extracción con IA (ChatGPT)
            respuesta_ia = _extract_attack_context_with_ai(content=enriched_content)

            # Si IA funciona, usar esos campos; si no, usar extracción por regex
            if respuesta_ia:
                campos_extraidos = respuesta_ia
            else:
                campos_extraidos = _extract_attack_context(title=row['titulo'], content=enriched_content, html=article_html)

            # Construir artículo con todos los campos
            article = {
                'titulo': row['titulo'][:255],
                'contenido': enriched_content[:5000],
                **campos_extraidos,
                'respuesta_ia': respuesta_ia or {},  # Guardar JSON de IA
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
        pages_fetched = 0  # Contador de páginas (cota de seguridad)

        # Loop de paginación: buscar hasta tener target_items O agotar páginas
        while len(query_items) < target_items and pages_fetched < ABC_MAX_PAGES_PER_QUERY:
            pages_fetched += 1
            # Construir URL de búsqueda (API Queryly)
            search_url = (
                f'{ABC_QUERYLY_ENDPOINT}?queryly_key={ABC_QUERYLY_KEY}'
                f'&query={quote_plus(query)}&endindex={end_index}&batchsize={batch_size}'
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
        'respuesta_ia': item.get('respuesta_ia', {}),  # JSON de ChatGPT (si fue extraído con IA)
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

    # Intentar extracción con IA (ChatGPT)
    respuesta_ia = _extract_attack_context_with_ai(content=enriched_content)

    # Si IA funciona, usar esos campos; si no, usar extracción por regex
    if respuesta_ia:
        campos_extraidos = respuesta_ia
    else:
        campos_extraidos = _extract_attack_context(title=title, content=enriched_content, html=article_html)

    # Construir artículo con todos los campos
    normalized = {
        'titulo': title[:255],
        'contenido': enriched_content[:5000],
        **campos_extraidos,
        'respuesta_ia': respuesta_ia or {},  # Guardar JSON de IA
        'fuente': SOURCE_ABC,
        'url': link,
        'fecha': parsed_date,
    }

    # Filtro final: Validar que sea relevante para Paraguay Y describa un ataque
    if not _passes_article_filters(normalized):
        return None

    return normalized  # Si pasó todos los filtros, retorna


