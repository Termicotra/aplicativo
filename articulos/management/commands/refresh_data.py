from django.core.management.base import BaseCommand
from django.db import connection
from articulos.models import Articulo
from simulaciones.models import Simulacion
from django.core.cache import cache
import sys
import os
from datetime import datetime, timedelta

# Importar los scripts de actualización
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


class Command(BaseCommand):
    help = 'Refresca artículos y simulaciones cada 15 días (ejecutable cada 24 horas)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución sin considerar la última vez que se ejecutó',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        cache_key = 'last_refresh_data_timestamp'
        last_refresh = cache.get(cache_key)

        now = datetime.now()

        # Verificar si han pasado 15 días desde la última ejecución
        if not force and last_refresh:
            last_refresh_dt = datetime.fromisoformat(last_refresh)
            days_elapsed = (now - last_refresh_dt).days

            if days_elapsed < 15:
                self.stdout.write(
                    self.style.WARNING(
                        f'⏭️  Saltando refresco: solo han pasado {days_elapsed} días de 15 requeridos.\n'
                        f'   Última ejecución: {last_refresh_dt.strftime("%Y-%m-%d %H:%M:%S")}\n'
                        f'   Próxima ejecución: {(last_refresh_dt + timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")}'
                    )
                )
                return

        self.stdout.write('=' * 60)
        self.stdout.write(f'[{now.strftime("%Y-%m-%d %H:%M:%S")}] Iniciando refresco de datos')
        self.stdout.write('=' * 60 + '\n')

        try:
            # Paso 1: Borrar datos de simulaciones
            self.stdout.write('1. Borrando simulaciones...')
            count = Simulacion.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'   ✓ {count} simulaciones borradas'))

            # Paso 2: Borrar datos de artículos
            self.stdout.write('2. Borrando artículos...')
            count = Articulo.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'   ✓ {count} artículos borrados'))

            # Paso 3: Ejecutar ingestion de artículos
            self.stdout.write('3. Ejecutando ingestion de artículos...')
            try:
                from articulos.ingestion import main as ingest_main
                ingest_main()
                self.stdout.write(self.style.SUCCESS('   ✓ Ingestion completada'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   ⚠ Ingestion falló: {e}'))

            # Paso 4: Ejecutar generación de simulaciones
            self.stdout.write('4. Generando simulaciones...')
            try:
                from generate_simulations import main as sim_main
                sim_main()
                self.stdout.write(self.style.SUCCESS('   ✓ Simulaciones generadas'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   ⚠ Generación de simulaciones falló: {e}'))

            # Guardar timestamp de la última ejecución exitosa
            cache.set(cache_key, now.isoformat(), timeout=None)  # timeout=None = indefinido

            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('✓ Proceso de refresco completado exitosamente'))
            self.stdout.write(f'Próxima ejecución: {(now + timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write('=' * 60)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error durante el proceso: {e}'))
            raise
