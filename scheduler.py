#!/usr/bin/env python
"""
Scheduler para ejecutar tareas periódicas en Heroku
Ejecuta: python scheduler.py
O en Heroku: procfile con "scheduler: python scheduler.py"
"""
import os
import sys
import django
import logging
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'treck.settings')
django.setup()

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def refresh_data_job():
    """Ejecuta el comando de refresco de datos"""
    try:
        logger.info('═' * 50)
        logger.info(f'[{datetime.now()}] Iniciando tarea: refresh_data')
        logger.info('═' * 50)
        call_command('refresh_data')
        logger.info('═' * 50)
        logger.info('✓ Tarea completada exitosamente')
        logger.info('═' * 50)
    except Exception as e:
        logger.error(f'✗ Error en tarea: {e}', exc_info=True)


def start_scheduler():
    """Inicia el scheduler"""
    scheduler = BackgroundScheduler()

    # Ejecutar cada 15 días a las 3 AM
    # Cron: hour=3, minute=0, day='*/15'
    trigger = CronTrigger(hour=3, minute=0, day='*/15')

    scheduler.add_job(
        refresh_data_job,
        trigger=trigger,
        id='refresh_data_job',
        name='Refresh Articulos y Simulaciones',
        replace_existing=True
    )

    scheduler.start()
    logger.info('📅 Scheduler iniciado')
    logger.info('⏰ Próxima ejecución: cada 15 días a las 3 AM')

    try:
        # Mantener el scheduler corriendo
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('⛔ Scheduler detenido')
        scheduler.shutdown()


if __name__ == '__main__':
    if os.getenv('DYNO'):  # Running on Heroku
        logger.info('Running on Heroku')
    start_scheduler()
