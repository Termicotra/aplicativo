import os
import sys
import json

# Preparar entorno Django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')

import django
django.setup()

from simulaciones.ai_service import generar_simulacion_y_feedback
from simulaciones.models import AIInteraction

def run_real_test():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('ERROR: OPENAI_API_KEY no está configurada en el entorno. Exporta la variable y reintenta.')
        return

    prompt = 'Prueba real de generación de simulación anti-phishing para test' 
    articulo = {'id': 9999, 'titulo': 'Caso de prueba real', 'contenido': 'Contenido de prueba para generar simulación', 'fecha': '2026-07-15'}
    args = dict(
        openai_api_key=api_key,
        model_name=os.getenv('OPENAI_MODEL', ''),
        prompt_usuario=prompt,
        articulos_recientes=[],
        articulo_base=articulo,
    )

    print('Llamando a generar_simulacion_y_feedback...')
    try:
        result = generar_simulacion_y_feedback(**args)
    except Exception as exc:
        print('Error al generar simulación:', exc)
        return

    print('Resultado de la generación:')
    print(json.dumps(result, indent=2, ensure_ascii=False))

    qs = AIInteraction.objects.filter(model_name=args.get('model_name') or '').order_by('-created_at')[:10]
    print('\nÚltimas interacciones guardadas (limit 10):', qs.count())
    for obj in qs:
        print(obj.id, obj.id_iainteraction, obj.model_name, obj.created_at)

if __name__ == '__main__':
    run_real_test()
