#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

os.environ.setdefault('OPENAI_MODEL', 'gpt-4o')

from articulos.models import Articulo
from simulaciones.ai_service import generar_simulacion_y_feedback

# Get first article (should not be CERT or ABC as entity)
articulo = Articulo.objects.filter(fuente__icontains='ABC').first()
if articulo:
    print(f"Artículo seleccionado: {articulo.titulo[:100]}")
    print(f"Fuente: {articulo.fuente}")
    print(f"Canal de ataque: {articulo.canal_ataque}")
    
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
            }
        )
        
        print("\n=== RESULTADO ===")
        print(f"Entidad objetivo: {resultado['entidad_objetivo']}")
        print(f"Dominio objetivo: {resultado['dominio_objetivo']}")
        print(f"Remitente generado: {resultado['sender_email']}")
        print(f"Asunto: {resultado['subject']}")
        print(f"Enlace senuelo: {resultado['enlace_senuelo']}")
        
        # Check that no provider domains appear
        sender = resultado['sender_email'].lower()
        subject = resultado['subject'].lower()
        if 'abc' in sender or 'cert' in sender:
            print(f"⚠️  ADVERTENCIA: Proveedor detectado en remitente: {sender}")
        else:
            print(f"✓ Remitente limpio (sin ABC/CERT)")
            
        if 'abc' in subject or 'cert' in subject:
            print(f"⚠️  ADVERTENCIA: Proveedor en asunto: {subject}")
        else:
            print(f"✓ Asunto limpio (sin ABC/CERT)")
        
    except Exception as e:
        print(f"Error generando simulación: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No se encontró artículo de ABC")
