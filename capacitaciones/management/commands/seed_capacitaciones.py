from django.core.management.base import BaseCommand
from django.db import transaction

from capacitaciones.models import Leccion, SeccionLeccion, ItemListaSeccion


SEED_LECCIONES = [
    {
        'titulo': 'Que es el Phishing?',
        'duracion': '5 min',
        'orden': 1,
        'contenido_titulo': 'Introduccion al Phishing',
        'bloqueada': False,
        'secciones': [
            {
                'encabezado': 'Definicion',
                'texto': 'El phishing es una forma de engano donde un atacante se hace pasar por una fuente confiable para obtener informacion personal o financiera de la victima.',
                'orden': 1,
            },
            {
                'encabezado': 'Por que es peligroso?',
                'texto': 'En Paraguay, se registraron mas de 551 millones de intentos de ciberataques en la primera mitad de 2025. El phishing es una de las tecnicas mas utilizadas por ciberdelincuentes.',
                'orden': 2,
            },
            {
                'encabezado': 'Tipos comunes',
                'texto': '',
                'orden': 3,
                'items': [
                    'Email phishing: Correos falsos que imitan bancos o servicios',
                    'Smishing: Mensajes SMS fraudulentos',
                    'Vishing: Llamadas telefonicas enganosas',
                    'Spear phishing: Ataques personalizados',
                ],
            },
        ],
    },
    {
        'titulo': 'Identificar URLs sospechosas',
        'duracion': '7 min',
        'orden': 2,
        'contenido_titulo': 'Analisis de URLs',
        'secciones': [
            {
                'encabezado': 'Senales de alerta',
                'texto': '',
                'orden': 1,
                'items': [
                    'Dominios mal escritos: "bancobcp.com" vs "banc0bcp.com"',
                    'Subdominios enganosos: "login.banco.sitiofalso.com"',
                    'HTTP en lugar de HTTPS',
                    'URLs acortadas de fuentes desconocidas',
                ],
            },
            {
                'encabezado': 'Como verificar',
                'texto': 'Siempre pasa el cursor sobre los enlaces antes de hacer clic. En moviles, manten presionado el enlace para ver la URL completa.',
                'orden': 2,
            },
        ],
    },
    {
        'titulo': 'Correos electronicos falsos',
        'duracion': '8 min',
        'orden': 3,
        'contenido_titulo': 'Detectando emails fraudulentos',
        'secciones': [
            {
                'encabezado': 'Indicadores de phishing en emails',
                'texto': '',
                'orden': 1,
                'items': [
                    'Remitentes con dominios sospechosos',
                    'Errores ortograficos y gramaticales',
                    'Urgencia extrema o amenazas',
                    'Solicitudes de informacion personal',
                    'Archivos adjuntos inesperados',
                ],
            },
            {
                'encabezado': 'Ejemplo en Paraguay',
                'texto': 'Es comun recibir correos falsos que simulan ser de Tigo, Personal, o bancos locales solicitando "verificar tu cuenta" o "actualizar datos".',
                'orden': 2,
            },
        ],
    },
    {
        'titulo': 'Mensajes SMS fraudulentos',
        'duracion': '6 min',
        'orden': 4,
        'contenido_titulo': 'Seguridad en SMS',
        'bloqueada': True,
        'secciones': [
            {
                'encabezado': 'Que es Smishing?',
                'texto': 'El smishing es phishing a traves de mensajes SMS. Los atacantes envian mensajes que parecen ser de bancos o servicios legitimando para robar informacion.',
                'orden': 1,
            },
            {
                'encabezado': 'Como identificar',
                'texto': '',
                'orden': 2,
                'items': [
                    'Mensajes de remitentes desconocidos',
                    'Urgencia para hacer clic en enlaces',
                    'Solicitud de datos personales o financieros',
                    'URLs acortadas sospechosas',
                ],
            },
        ],
    },
    {
        'titulo': 'Redes sociales y phishing',
        'duracion': '7 min',
        'orden': 5,
        'contenido_titulo': 'Amenazas en Redes Sociales',
        'bloqueada': True,
        'secciones': [
            {
                'encabezado': 'Riesgos en redes sociales',
                'texto': 'Las redes sociales son un objetivo comun para phishing. Los atacantes crean perfiles falsos o usan tecnicas de social engineering para obtener acceso a cuentas.',
                'orden': 1,
            },
            {
                'encabezado': 'Proteccion basica',
                'texto': '',
                'orden': 2,
                'items': [
                    'No hagas clic en enlaces sospechosos en mensajes directos',
                    'Verifica la identidad de perfiles antes de interactuar',
                    'Usa autenticacion de dos factores',
                    'No compartas informacion personal sensible',
                ],
            },
        ],
    },
    {
        'titulo': 'Proteccion y prevencion',
        'duracion': '10 min',
        'orden': 6,
        'contenido_titulo': 'Mejores Practicas de Seguridad',
        'bloqueada': True,
        'secciones': [
            {
                'encabezado': 'Medidas preventivas',
                'texto': '',
                'orden': 1,
                'items': [
                    'Mantén software y sistemas operativos actualizados',
                    'Usa contrasenas fuertes y unicas',
                    'Activa autenticacion de dos factores',
                    'Ten cuidado al descargar archivos adjuntos',
                    'Verifica direcciones de correo electronico cuidadosamente',
                ],
            },
            {
                'encabezado': 'Si crees que eres victima',
                'texto': '',
                'orden': 2,
                'items': [
                    'Cambia tus contrasenas inmediatamente',
                    'Contacta a tu institucion financiera',
                    'Reporta el incidente a las autoridades',
                    'Monitorea tu cuenta para actividad sospechosa',
                    'Considera un servicio de monitoreo de credito',
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Carga lecciones base de capacitacion en ciberseguridad.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina lecciones existentes y carga solo las de semilla.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            ItemListaSeccion.objects.all().delete()
            SeccionLeccion.objects.all().delete()
            Leccion.objects.all().delete()
            self.stdout.write(self.style.WARNING('Se eliminaron lecciones previas.'))

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

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed completado. Lecciones creadas: {creadas}. Lecciones actualizadas: {actualizadas}.'
            )
        )
