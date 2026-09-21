#!/usr/bin/env python
import os
import sys
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from articulos.models import Articulo
from simulaciones.models import Simulacion
from simulaciones.ai_service import generar_simulacion_y_feedback

# Entidades reales de Paraguay validadas
ENTIDADES_REALES_PARAGUAY = {
    # Bancos locales
    'ITAU': 'Banco Itaú',
    'SUDAMERIS': 'Banco Sudameris',
    'GNB': 'Banco GNB',
    'BASA': 'Banco Basa',
    'CONTINENTAL': 'Banco Continental',
    'FAMILIAR': 'Banco Familiar',
    'ATLAS': 'Banco Atlas',
    'BANCOP': 'Bancop',
    'INTERFISA': 'Interfisa',
    'SOLAR': 'Banco Solar',
    'UENO': 'Banco Ueno',
    'ZETA': 'Banco Zeta',
    'BNF': 'Banco Nacional de Fomento',
    'BCP': 'Banco Central del Paraguay',
    # Bancos extranjeros
    'CITIBANK': 'Citibank',
    'BANCO DO BRASIL': 'Banco do Brasil',
    # Gobierno y servicios
    'IPS': 'Instituto de Previsión Social',
    'SET': 'Secretaría de Impuestos',
    'ANDE': 'Administración Nacional de Electricidad',
    'ESSAP': 'Empresa de Servicios Sanitarios',
    'PODER JUDICIAL': 'Poder Judicial',
    'COPACO': 'COPACO',
    'CERT': 'CERT.py',
    'MUNICIPALIDAD': 'Municipalidades',
    'MTESS': 'Ministerio de Trabajo, Empleo y Seguridad Social',
    'MOPC': 'Ministerio de Obras Públicas y Comunicaciones',
    'STP': 'Secretaría Técnica de Planificación',
    'SEAM': 'Secretaría del Ambiente',
    'DINAC': 'Dirección Nacional de Aeronáutica Civil',
}


def is_inherently_phishing(articulo):
    """
    Detect if attack described is inherently phishing (no legitimate version possible).

    Returns (is_inherent, reason)
    """
    content_lower = (articulo.contenido + articulo.titulo).lower()

    # Palabras clave que indican ataque inherentemente phishing (sin versión legítima posible)
    # Solo MÁS específicas: credenciales, datos tarjeta, adjuntos maliciosos, bloqueos
    # Removido "dinero" porque bancos PUEDEN tener mensajes legítimos sobre bonificaciones/reembolsos
    phishing_keywords = {
        'credenciales_en_email': ['enviar contraseña', 'confirmar contraseña', 'verificar usuario y contraseña'],
        'datos_tarjeta': ['número de tarjeta', 'cvv', 'pin de tarjeta'],
        'adjunto_malicioso': ['adjunto malicioso', 'archivo malicioso', 'adjunto con malware'],
        'bloqueo_via_email': ['bloqueo de cuenta', 'cuenta bloqueada', 'será bloqueada', 'cuenta será bloqueada',
                             'haz clic para desbloquear', 'verifica tu cuenta', 'compromet', 'amenaza de bloqueo'],
    }

    for category, keywords in phishing_keywords.items():
        for keyword in keywords:
            if keyword in content_lower:
                return True, f"Detectado: {category} ({keyword})"

    # Additional patterns: urgency + credential request = phishing
    if 'inmediato' in content_lower and ('confirme' in content_lower or 'verifique' in content_lower or 'identidad' in content_lower):
        return True, "Detectado: Urgencia + solicitud de identidad"

    if 'si no' in content_lower and 'será' in content_lower and ('bloqueada' in content_lower or 'cancelada' in content_lower):
        return True, "Detectado: Amenaza condicional (si no, será...)"

    return False, None


def generate_simulations_for_articles(only_missing=True):
    """
    Generate 2 simulations per article: one phishing, one legitimate.
    
    Args:
        only_missing (bool): If True, only generate for articles without simulations.
    """
    if only_missing:
        articulos = Articulo.objects.exclude(simulaciones_generadas__isnull=False).distinct()
    else:
        articulos = Articulo.objects.all()
    
    total_generated = 0
    total_errors = 0
    total_skipped = 0

    print(f"\nTotales artículos a procesar: {articulos.count()}\n")

    for idx, articulo in enumerate(articulos, 1):
        print(f"[{idx}/{articulos.count()}] Artículo: {articulo.titulo[:50]}...")
        
        # Skip if already has simulations
        if not only_missing and Simulacion.objects.filter(articulo=articulo).exists():
            print(f"  [SKIP] Saltado (ya tiene simulaciones)")
            total_skipped += 1
            continue
        
        # Check if attack is inherently phishing
        is_inherent, reason = is_inherently_phishing(articulo)
        if is_inherent:
            print(f"  [{reason}] - Solo phishing")
            tipos_a_generar = [True]  # Only phishing
        else:
            tipos_a_generar = [True, False]  # Both phishing and legitimate

        # For each phishing type
        for es_phishing in tipos_a_generar:
            phishing_type = "PHISHING" if es_phishing else "LEGÍTIMO"
            print(f"    {phishing_type}...", end=" ", flush=True)
            
            try:
                resultado = generar_simulacion_y_feedback(
                    prompt_usuario="Identifica señales de phishing en este mensaje",
                    articulos_recientes=[
                        {
                            'titulo': articulo.titulo,
                            'fuente': articulo.fuente,
                            'fecha': str(articulo.fecha),
                            'canal_ataque': articulo.canal_ataque,
                            'contenido': articulo.contenido[:500]
                        }
                    ],
                    articulo_base={
                        'titulo': articulo.titulo,
                        'contenido': articulo.contenido,
                        'url': articulo.url,
                        'proceso_ataque': articulo.proceso_ataque,
                        'secuencia_ataque': articulo.secuencia_ataque,
                        'recomendaciones': articulo.recomendaciones,
                        'ejemplos_ataque': articulo.ejemplos_ataque,
                        'origen_ataque': articulo.origen_ataque,
                        'objetivo_ataque': articulo.objetivo_ataque,
                        'canal_ataque': articulo.canal_ataque,
                    },
                    force_es_phishing=es_phishing,
                    recipient_email=None,
                )
                
                # Validate simulation content
                simulacion_text = resultado.get('simulacion', '')
                if 'ERROR:' in simulacion_text or 'error' in simulacion_text.lower()[:50]:
                    print(f"[FAIL] Simulación contiene ERROR, rechazada")
                    total_errors += 1
                    continue

                # Validate minimum content length (email must have body)
                if len(simulacion_text.strip()) < 100:
                    print(f"[FAIL] Contenido demasiado corto ({len(simulacion_text)} chars), rechazada")
                    total_errors += 1
                    continue

                # Validate: legitimate emails should NOT mention attachments/files
                if not es_phishing:
                    text_lower = simulacion_text.lower()
                    attachment_keywords = ['adjunto', 'archivo', '.pdf', '.doc', '.zip', 'descargar', 'descargue', 'documento que']
                    if any(kw in text_lower for kw in attachment_keywords):
                        print(f"[FAIL] Simulacion legitima menciona adjuntos, rechazada")
                        total_errors += 1
                        continue

                # Validate: legitimate emails should NOT contain threat/urgency language
                if not es_phishing:
                    text_lower = simulacion_text.lower()
                    threat_keywords = ['será bloqueado', 'será bloqueada', 'bloqueo de cuenta', 'cuenta bloqueada',
                                      'amenaza de', 'amenaza', 'si no', 'inmediato', 'ahora', 'urgente', '24 horas']
                    found_threats = [kw for kw in threat_keywords if kw in text_lower]
                    if found_threats:
                        print(f"[FAIL] Simulacion legitima contiene amenazas/urgencia: {found_threats[0]}, rechazada")
                        total_errors += 1
                        continue

                # Validate: simulación debe ser temáticamente coherente con artículo
                articulo_text = (articulo.titulo + ' ' + articulo.contenido).lower()
                sim_text_lower = simulacion_text.lower()

                # Rechazar desajustes temáticos claros
                # Si artículo habla de "ofertas laborales" pero simulación es bancaria, rechazar
                if ('oferta' in articulo_text or 'laboral' in articulo_text or 'trabajo' in articulo_text):
                    if any(banco in sim_text_lower for banco in ['itau', 'bcp', 'bnf', 'gnb', 'sudameris', 'basa', 'banco']):
                        print(f"[FAIL] Desajuste temático: oferta laboral pero simulación es bancaria")
                        total_errors += 1
                        continue

                # Palabras clave comunes del artículo (excepto muy genéricas)
                articulo_words = [w for w in articulo_text.split()
                                if len(w) > 4 and w not in ['que', 'para', 'con', 'como', 'esta', 'sido', 'usuario', 'email', 'correo']]

                # Si el artículo tiene palabras clave únicas, buscar al menos una en la simulación
                if articulo_words:
                    common_words = [w for w in articulo_words if w in sim_text_lower]
                    if not common_words:
                        print(f"[FAIL] Simulacion NO relacionada al articulo, rechazada")
                        total_errors += 1
                        continue

                # Validate: NO presionar teclas específicas (pero SÍ permitir clicks)
                text_lower = simulacion_text.lower()
                # Rechazar SOLO si pide presionar teclas específicas
                keyboard_keywords = ['presione', 'presiona', 'pulsa', 'pulsando', 'presionar tecla',
                                    'tecla a', 'tecla b', 'tecla c', 'tecla d', 'tecla e',
                                    'presione la tecla', 'pulsa la tecla']
                found_keyboard = [kw for kw in keyboard_keywords if kw in text_lower]
                if found_keyboard:
                    print(f"[FAIL] Simulacion solicita presionar teclas, rechazada: {found_keyboard[0]}")
                    total_errors += 1
                    continue

                # Validate entity is real Paraguayan organization
                entidad = str(resultado.get('entidad_objetivo', '')).upper()

                # Rechazar "BANCO NACIONAL" genérico - debe ser BCP o BNF explícitamente
                if 'BANCO NACIONAL' in entidad and 'BNF' not in entidad and 'BCP' not in entidad:
                    print(f"[FAIL] Entidad ambigua 'BANCO NACIONAL' - debe ser BCP o BNF específicamente")
                    total_errors += 1
                    continue

                validated_keywords = list(ENTIDADES_REALES_PARAGUAY.keys())
                if not any(kw in entidad for kw in validated_keywords):
                    print(f"[FAIL] Entidad no validada: {entidad}")
                    total_errors += 1
                    continue

                # Create simulation record
                # Use the es_phishing value from AI result (may have been corrected for incoherence)
                resultado_es_phishing = resultado.get('es_phishing', 'true') == 'true'
                Simulacion.objects.create(
                    articulo=articulo,
                    es_phishing=resultado_es_phishing,
                    simulacion_texto=resultado['simulacion'],
                    tipo_mensaje=resultado.get('tipo_mensaje', 'correo'),
                    sender_email=resultado.get('sender_email', ''),
                    subject=resultado.get('subject', ''),
                    nombre_contacto=resultado.get('nombre_contacto', ''),
                    attachments=resultado.get('attachments', []),
                    enlace_senuelo=resultado.get('enlace_senuelo', ''),
                    entidad_objetivo=resultado.get('entidad_objetivo', ''),
                    dominio_objetivo=resultado.get('dominio_objetivo', ''),
                    resumen_justificacion=resultado.get('resumen_justificacion', ''),
                    feedback=resultado.get('feedback', ''),
                    tipo_generacion='inicial',
                )
                
                print("[OK]", end=" ")
                total_generated += 1
                
            except Exception as e:
                error_msg = str(e)[:80]
                print(f"[FAIL] ({error_msg})")
                total_errors += 1
                # Continue to next type instead of failing completely
    
    print(f"\n\n=== Resumen ===")
    print(f"Simulaciones generadas: {total_generated}")
    print(f"Errores: {total_errors}")
    print(f"Artículos saltados: {total_skipped}")


def main():
    """Función principal para generar simulaciones"""
    import sys

    # Check if user wants to regenerate all (--all flag)
    regenerate_all = '--all' in sys.argv

    print(f"Modo: {'Regenerar TODO' if regenerate_all else 'Solo faltantes'}")
    generate_simulations_for_articles(only_missing=not regenerate_all)


if __name__ == '__main__':
    main()
