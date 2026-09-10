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


def is_inherently_phishing(articulo):
    """
    Detect if attack described is inherently phishing (no legitimate version possible).

    Returns (is_inherent, reason)
    """
    content_lower = (articulo.contenido + articulo.titulo).lower()

    # Palabras clave que indican ataque inherentemente phishing (sin versión legítima posible)
    phishing_keywords = {
        'dinero': ['dinero', 'premio', 'regalo', 'ganaste', 'heredaste', 'bono', 'reembolso', 'comisión', 'adelanto'],
        'credenciales_en_email': ['enviar contraseña', 'confirmar contraseña', 'verificar usuario y contraseña'],
        'datos_tarjeta': ['número de tarjeta', 'cvv', 'pin de tarjeta'],
    }

    for category, keywords in phishing_keywords.items():
        for keyword in keywords:
            if keyword in content_lower:
                return True, f"Detectado: {category} ({keyword})"

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


if __name__ == '__main__':
    import sys
    
    # Check if user wants to regenerate all (--all flag)
    regenerate_all = '--all' in sys.argv
    
    print(f"Modo: {'Regenerar TODO' if regenerate_all else 'Solo faltantes'}")
    generate_simulations_for_articles(only_missing=not regenerate_all)
