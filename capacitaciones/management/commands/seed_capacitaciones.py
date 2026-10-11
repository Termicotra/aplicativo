from django.core.management.base import BaseCommand
from django.db import transaction, connection

from capacitaciones.models import Leccion, SeccionLeccion, ItemListaSeccion


SEED_LECCIONES = [
    {
        'titulo': '¿Qué es el Phishing?',
        'duracion': '5 min',
        'orden': 1,
        'contenido_titulo': 'Introducción al Phishing',
        'bloqueada': False,
        'secciones': [
            {
                'encabezado': 'Definición',
                'texto': 'El phishing es una forma de engaño donde un atacante se hace pasar por una fuente confiable para obtener información personal o financiera de la víctima.',
                'orden': 1,
            },
            {
                'encabezado': '¿Por qué es peligroso?',
                'texto': 'En Paraguay, se registraron más de 551 millones de intentos de ciberataques en la primera mitad de 2025. El phishing es una de las técnicas más utilizadas por ciberdelincuentes.',
                'orden': 2,
            },
            {
                'encabezado': 'Tipos comunes',
                'texto': '',
                'orden': 3,
                'items': [
                    'Email phishing: Correos falsos que imitan bancos o servicios',
                    'Smishing: Mensajes SMS fraudulentos',
                    'Vishing: Llamadas telefónicas engañosas',
                    'Spear phishing: Ataques personalizados',
                ],
            },
        ],
    },
    {
        'titulo': 'Identificar URLs sospechosas',
        'duracion': '7 min',
        'orden': 2,
        'contenido_titulo': 'Análisis de URLs',
        'secciones': [
            {
                'encabezado': 'Señales de alerta',
                'texto': '',
                'orden': 1,
                'items': [
                    'Dominios mal escritos: "bancobcp.com" vs "banc0bcp.com"',
                    'Subdominios engañosos: "login.banco.sitiofalso.com"',
                    'HTTP en lugar de HTTPS',
                    'URLs acortadas de fuentes desconocidas',
                ],
            },
            {
                'encabezado': 'Cómo verificar',
                'texto': 'Siempre pasa el cursor sobre los enlaces antes de hacer clic. En móviles, mantén presionado el enlace para ver la URL completa.',
                'orden': 2,
            },
        ],
    },
    {
        'titulo': 'Correos electrónicos falsos',
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
                    'Errores ortográficos y gramaticales',
                    'Urgencia extrema o amenazas',
                    'Solicitudes de información personal',
                    'Archivos adjuntos inesperados',
                ],
            },
            {
                'encabezado': 'Ejemplo en Paraguay',
                'texto': 'Es común recibir correos falsos que simulan ser de Tigo, Personal, o bancos locales solicitando "verificar tu cuenta" o "actualizar datos".',
                'orden': 2,
            },
        ],
    },
    {
        'titulo': 'Mensajes SMS fraudulentos',
        'duracion': '6 min',
        'orden': 4,
        'contenido_titulo': 'Seguridad en SMS',
        'bloqueada': False,
        'secciones': [
            {
                'encabezado': '¿Qué es Smishing?',
                'texto': 'El smishing es phishing a través de mensajes SMS. Los atacantes envían mensajes que parecen ser de bancos o servicios legitimando para robar información.',
                'orden': 1,
            },
            {
                'encabezado': 'Cómo identificar',
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
        'bloqueada': False,
        'secciones': [
            {
                'encabezado': 'Riesgos en redes sociales',
                'texto': 'Las redes sociales son un objetivo común para phishing. Los atacantes crean perfiles falsos o usan técnicas de social engineering para obtener acceso a cuentas.',
                'orden': 1,
            },
            {
                'encabezado': 'Protección básica',
                'texto': '',
                'orden': 2,
                'items': [
                    'No hagas clic en enlaces sospechosos en mensajes directos',
                    'Verifica la identidad de perfiles antes de interactuar',
                    'Usa autenticación de dos factores',
                    'No compartas información personal sensible',
                ],
            },
        ],
    },
    {
        'titulo': 'Ingeniería social y manipulación',
        'duracion': '9 min',
        'orden': 6,
        'contenido_titulo': 'Técnicas de Manipulación Psicológica',
        'bloqueada': False,
        'secciones': [
            {
                'encabezado': '¿Qué es la ingeniería social?',
                'texto': 'La ingeniería social es el uso de manipulación psicológica para engañar a las personas y obtener información confidencial o acceso a sistemas. A diferencia del phishing, no siempre requiere tecnología.',
                'orden': 1,
            },
            {
                'encabezado': 'Técnicas comunes de manipulación',
                'texto': '',
                'orden': 2,
                'items': [
                    'Urgencia extrema: "Tu cuenta será bloqueada en 24 horas"',
                    'Autoridad falsa: Fingir ser personal de banco o gobierno',
                    'Confianza: Crear rapport antes de pedir información',
                    'Miedo: Amenazar con consecuencias negativas',
                    'Recompensa falsa: Prometer dinero o premios',
                ],
            },
            {
                'encabezado': 'Suplantación de seres cercanos',
                'texto': 'Una técnica especialmente efectiva es cuando un atacante se hace pasar por un familiar cercano (padres, hermanos, hijos) en peligro para solicitar dinero urgentemente. En Paraguay, estos ataques son comunes vía WhatsApp o llamadas telefónicas.',
                'orden': 3,
            },
            {
                'encabezado': 'Ejemplo: "Hola papá"',
                'texto': '',
                'orden': 4,
                'items': [
                    'El atacante obtiene el número de WhatsApp de un familiar',
                    'Cambia el nombre del perfil al del familiar real',
                    'Escribe: "Hola papá, soy tu hijo. Tengo un problema"',
                    'Crea una historia urgente: accidente, multa, secuestro',
                    'Solicita transferencia inmediata o datos bancarios',
                    'Desaparece antes de que se verifique la historia',
                ],
            },
            {
                'encabezado': 'Cómo protegerse',
                'texto': '',
                'orden': 5,
                'items': [
                    'Verifica directamente con la persona: llama o pregunta en persona',
                    'Desconfia de mensajes urgentes inesperados',
                    'Nunca comparte datos personales o bancarios por chat',
                    'Si es urgencia financiera, cuelga y llama de vuelta',
                    'Confirma cambios de cuenta bancaria por metodo oficial',
                    'Educa a familiares sobre estas tacticas',
                ],
            },
        ],
    },
    {
        'titulo': 'Protección y prevención',
        'duracion': '10 min',
        'orden': 7,
        'contenido_titulo': 'Mejores Prácticas de Seguridad',
        'bloqueada': False,
        'secciones': [
            {
                'encabezado': 'Medidas preventivas',
                'texto': '',
                'orden': 1,
                'items': [
                    'Mantén software y sistemas operativos actualizados',
                    'Usa contraseñas fuertes y únicas',
                    'Activa autenticación de dos factores',
                    'Ten cuidado al descargar archivos adjuntos',
                    'Verifica direcciones de correo electrónico cuidadosamente',
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

            with connection.cursor() as cursor:
                cursor.execute("ALTER SEQUENCE item_lista_seccion_id_seq RESTART WITH 1;")
                cursor.execute("ALTER SEQUENCE seccion_leccion_id_seq RESTART WITH 1;")
                cursor.execute("ALTER SEQUENCE leccion_capacitacion_id_seq RESTART WITH 1;")
            self.stdout.write(self.style.WARNING('Se reiniciaron las secuencias de IDs.'))

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
