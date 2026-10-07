#!/usr/bin/env python
"""
Script para ejecutar el seed de capacitaciones en Heroku sin CLI.
Uso: python seed_heroku.py <DATABASE_URL> [--reset]

Ejemplo:
  python seed_heroku.py "postgresql://user:pass@host:5432/db"
  python seed_heroku.py "postgresql://user:pass@host:5432/db" --reset
"""

import os
import sys
import django
from pathlib import Path

# Obtener el DATABASE_URL desde argumentos
if len(sys.argv) < 2:
    print("Error: Debes proporcionar el DATABASE_URL como argumento")
    print("Uso: python seed_heroku.py <DATABASE_URL> [--reset]")
    print("\nPara obtener el DATABASE_URL:")
    print("  1. Ve a https://dashboard.heroku.com/apps/treck-7759cedc445f/settings")
    print("  2. Click en 'Reveal Config Vars'")
    print("  3. Copia el valor de DATABASE_URL")
    sys.exit(1)

database_url = sys.argv[1]
reset = "--reset" in sys.argv

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
os.environ['DATABASE_URL'] = database_url

# Agregar el directorio del proyecto al path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Setup Django
django.setup()

# Importar después de setup
from django.db import transaction
from capacitaciones.models import Leccion, SeccionLeccion, ItemListaSeccion

# Importar el seed data
from capacitaciones.management.commands.seed_capacitaciones import SEED_LECCIONES

print("=" * 60)
print("[SEED CAPACITACIONES HEROKU]")
print("=" * 60)
print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'desconocida'}")
print(f"Reset: {'Sí' if reset else 'No'}")
print("=" * 60 + "\n")

try:
    with transaction.atomic():
        if reset:
            print("Borrando datos previos...\n")
            ItemListaSeccion.objects.all().delete()
            SeccionLeccion.objects.all().delete()
            Leccion.objects.all().delete()
            print("Datos previos eliminados.\n")

        creadas = 0
        actualizadas = 0

        for seed in SEED_LECCIONES:
            leccion, created = Leccion.objects.update_or_create(
                titulo=seed['titulo'],
                defaults={
                    'duracion': seed.get('duracion', '5 min'),
                    'orden': seed.get('orden', 0),
                    'contenido_titulo': seed.get('contenido_titulo', ''),
                    'bloqueada': seed.get('bloqueada', False),
                    'activa': True,
                },
            )

            if created:
                creadas += 1
            else:
                actualizadas += 1

            secciones_seed = seed.get('secciones', [])
            for seccion_seed in secciones_seed:
                seccion, _ = SeccionLeccion.objects.update_or_create(
                    leccion=leccion,
                    orden=seccion_seed.get('orden', 0),
                    defaults={
                        'encabezado': seccion_seed['encabezado'],
                        'texto': seccion_seed.get('texto', ''),
                    },
                )

                items_seed = seccion_seed.get('items', [])
                ItemListaSeccion.objects.filter(seccion=seccion, orden__gt=len(items_seed)).delete()

                for index, item_texto in enumerate(items_seed, start=1):
                    ItemListaSeccion.objects.update_or_create(
                        seccion=seccion,
                        orden=index,
                        defaults={
                            'texto': item_texto,
                        },
                    )

            SeccionLeccion.objects.filter(leccion=leccion, orden__gt=len(secciones_seed)).delete()

        print(f"Lecciones creadas: {creadas}")
        print(f"Lecciones actualizadas: {actualizadas}\n")

    print("=" * 60)
    print("[OK] Seed completado exitosamente")
    print("=" * 60)
except Exception as e:
    print("\n" + "=" * 60)
    print(f"[ERROR] {str(e)}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
