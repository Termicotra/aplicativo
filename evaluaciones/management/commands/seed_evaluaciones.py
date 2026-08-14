from django.core.management.base import BaseCommand
from django.db import transaction

from evaluaciones.models import Ejercicio, OpcionEjercicio


SEED_EJERCICIOS = [
    {
        'tema': 'Phishing',
        'pregunta': 'Que indicador sugiere que un correo podria ser phishing?',
        'concepto': 'El phishing usa suplantacion y urgencia para robar datos sensibles.',
        'ejemplo': 'Un correo pide verificar cuenta bancaria con un enlace acortado.',
        'retroalimentacion': 'Antes de hacer clic, valida remitente, dominio y tono del mensaje.',
        'opciones': [
            {
                'texto': 'Solicita usuario y contrasena por enlace externo.',
                'es_correcta': True,
                'retroalimentacion_opcion': 'Correcto. Pedir credenciales por enlace es una senal de riesgo.',
            },
            {
                'texto': 'Llega desde dominio institucional validado internamente.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. Ese escenario no muestra alerta por si solo.',
            },
            {
                'texto': 'Tiene saludo personalizado y no solicita acciones urgentes.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. Esas caracteristicas no son tipicas de phishing.',
            },
        ],
    },
    {
        'tema': 'Smishing',
        'pregunta': 'En un SMS, cual es una senal comun de fraude?',
        'concepto': 'El smishing es phishing por mensajes de texto con enlaces maliciosos.',
        'ejemplo': 'Mensaje afirma bloqueo de cuenta y pide confirmar datos en un link.',
        'retroalimentacion': 'No abras enlaces de SMS no verificados y consulta canales oficiales.',
        'opciones': [
            {
                'texto': 'El numero no identificado exige accion inmediata con un enlace.',
                'es_correcta': True,
                'retroalimentacion_opcion': 'Correcto. La urgencia con enlace sospechoso es un patron de smishing.',
            },
            {
                'texto': 'El mensaje informa horario de atencion sin incluir links.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. Ese contenido no implica fraude por si mismo.',
            },
            {
                'texto': 'El remitente coincide con el contacto oficial guardado.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. No es un indicador de ataque en ese contexto.',
            },
        ],
    },
    {
        'tema': 'Ingenieria social',
        'pregunta': 'Que accion reduce el riesgo ante una solicitud inesperada de datos?',
        'concepto': 'La ingenieria social manipula emociones para obtener informacion sensible.',
        'ejemplo': 'Un supuesto soporte tecnico pide codigo MFA por telefono.',
        'retroalimentacion': 'Verifica identidad por un canal alterno antes de compartir datos.',
        'opciones': [
            {
                'texto': 'Compartir el dato para evitar bloqueo inmediato.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. Nunca compartas datos sensibles sin validar identidad.',
            },
            {
                'texto': 'Confirmar solicitud con el area oficial por un canal independiente.',
                'es_correcta': True,
                'retroalimentacion_opcion': 'Correcto. Validar por otro canal corta el intento de manipulacion.',
            },
            {
                'texto': 'Reenviar la solicitud a todos los contactos para decidir.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. Eso puede ampliar el impacto del fraude.',
            },
        ],
    },
    {
        'tema': 'Seguridad en Codigos QR',
        'pregunta': 'Cual es el riesgo mas relevante al escanear codigos QR en espacios publicos?',
        'concepto': 'Los codigos QR pueden contener URLs maliciosas, malware o llevar a sitios de phishing. Su facilidad de escaneo y el desconocimiento de destino hacen que sean vectores de ataque.',
        'ejemplo': 'Un codigo QR pegado sobre un cartel publicitario original redirige a un sitio falso que captura credenciales.',
        'retroalimentacion': 'Antes de escanear, verifica visualmente que el codigo se vea integro y considera usar un app que muestre la URL antes de abrir.',
        'opciones': [
            {
                'texto': 'Los codigos QR siempre son seguros porque estan cifrados en la camara del telefono.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. Los QR no estan cifrados; el riesgo es el contenido o destino del enlace.',
            },
            {
                'texto': 'Pueden dirigir a URLs maliciosas o sitios de phishing sin que el usuario vea el destino real.',
                'es_correcta': True,
                'retroalimentacion_opcion': 'Correcto. El riesgo principal es que la URL esta oculta hasta escanear, permitiendo engano.',
            },
            {
                'texto': 'El riesgo es minimo si se escanea desde una red WiFi publica confiable.',
                'es_correcta': False,
                'retroalimentacion_opcion': 'Incorrecto. La red no afecta si el codigo apunta a un sitio malicioso.',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Carga ejercicios base de evaluaciones anti-phishing.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina ejercicios existentes y carga solo los de semilla.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            OpcionEjercicio.objects.all().delete()
            Ejercicio.objects.all().delete()
            self.stdout.write(self.style.WARNING('Se eliminaron ejercicios previos.'))

        creados = 0
        actualizados = 0

        for seed in SEED_EJERCICIOS:
            ejercicio, created = Ejercicio.objects.update_or_create(
                tema=seed['tema'],
                pregunta=seed['pregunta'],
                defaults={
                    'concepto': seed['concepto'],
                    'ejemplo': seed['ejemplo'],
                    'retroalimentacion': seed['retroalimentacion'],
                    'activo': True,
                },
            )

            if created:
                creados += 1
            else:
                actualizados += 1

            opciones_seed = seed['opciones']
            for index, opcion_seed in enumerate(opciones_seed, start=1):
                OpcionEjercicio.objects.update_or_create(
                    ejercicio=ejercicio,
                    orden=index,
                    defaults={
                        'texto': opcion_seed['texto'],
                        'es_correcta': opcion_seed['es_correcta'],
                        'retroalimentacion_opcion': opcion_seed['retroalimentacion_opcion'],
                    },
                )

            OpcionEjercicio.objects.filter(ejercicio=ejercicio, orden__gt=len(opciones_seed)).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed completado. Ejercicios creados: {creados}. Ejercicios actualizados: {actualizados}.'
            )
        )
