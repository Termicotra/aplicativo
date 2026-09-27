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
from django.core.management import call_command
from django.db import transaction

print("=" * 60)
print("[SEED CAPACITACIONES HEROKU]")
print("=" * 60)
print(f"Database: {database_url.split('@')[1] if '@' in database_url else 'desconocida'}")
print(f"Reset: {'Sí' if reset else 'No'}")
print("=" * 60 + "\n")

try:
    with transaction.atomic():
        if reset:
            print("Ejecutando con --reset (borrará datos previos)...\n")
            call_command('seed_capacitaciones', '--reset')
        else:
            print("Ejecutando sin reset (actualizará datos existentes)...\n")
            call_command('seed_capacitaciones')

    print("\n" + "=" * 60)
    print("[OK] Seed completado exitosamente")
    print("=" * 60)
except Exception as e:
    print("\n" + "=" * 60)
    print(f"[ERROR] {str(e)}")
    print("=" * 60)
    sys.exit(1)
