import time
from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase

from articulos.ingestion import (
    MIN_EXTRACTED_MATERIAL,
    MIN_RELEVANCE_SCORE,
    _calculate_relevance_score,
    _has_attack_flow_description,
    _is_paraguay_relevant,
    _is_recent_enough,
    _normalize_abc_search_item,
    _parse_date_strict,
    _passes_article_filters,
)

URL_PY = 'https://www.abc.com.py/nacionales/alerta-phishing'
MATERIAL_SUFICIENTE = {
    'proceso_ataque': 'El atacante envía un correo falso que imita al banco. ' * 2,
    'secuencia_ataque': 'La víctima ingresa sus credenciales en una página clonada. ' * 2,
    'ejemplos_ataque': 'Se reportaron casos de clientes paraguayos afectados por el mensaje. ' * 2,
}


def _articulo_phishing_paraguay(**overrides):
    """Artículo que debería superar todos los filtros de ingesta."""
    articulo = {
        'titulo': 'Alerta: falso correo del banco suplanta identidad a clientes paraguayos',
        'contenido': (
            'Los atacantes envían un correo electrónico falso que simula ser del banco. '
            'El mensaje solicita con urgencia que la víctima ingrese sus datos en un enlace falso. '
            'Al hacer clic, una página clonada captura las credenciales. '
            'Es una campaña de phishing dirigida a usuarios en Paraguay.'
        ),
        'url': URL_PY,
        **MATERIAL_SUFICIENTE,
    }
    articulo.update(overrides)
    return articulo


class FiltroRelevanciaParaguayTests(SimpleTestCase):
    def test_acepta_titulo_que_menciona_paraguay(self):
        self.assertTrue(_is_paraguay_relevant(
            title='Phishing en Paraguay',
            content='Texto sin más contexto.',
            url='https://www.ejemplo.com/nota',
        ))

    def test_acepta_dominio_py_aunque_el_texto_no_lo_mencione(self):
        self.assertTrue(_is_paraguay_relevant(
            title='Nueva campaña de correos falsos',
            content='Texto sin referencias geográficas.',
            url='https://www.cert.gov.py/alerta-1',
        ))

    def test_acepta_url_py_citada_en_el_contenido(self):
        self.assertTrue(_is_paraguay_relevant(
            title='Nueva campaña de correos falsos',
            content='Más información en https://www.bancoejemplo.gov.py/aviso del sitio oficial.',
            url='https://www.ejemplo.com/nota',
        ))

    def test_rechaza_articulo_sin_senal_paraguaya(self):
        self.assertFalse(_is_paraguay_relevant(
            title='Phishing masivo en Mexico',
            content='Los atacantes enviaron correos falsos a clientes bancarios.',
            url='https://www.ejemplo.com/nota',
        ))


class FiltroFlujoDeAtaqueTests(SimpleTestCase):
    def test_acepta_descripcion_de_flujo_de_phishing(self):
        self.assertTrue(_has_attack_flow_description(
            title='Alerta de phishing',
            content='Los atacantes envían un enlace falso y luego piden la contraseña.',
        ))

    def test_rechaza_noticia_tecnica_sin_acciones_de_atacante(self):
        self.assertFalse(_has_attack_flow_description(
            title='Actualización de seguridad para el servidor',
            content='Se publicó una nueva versión del software con mejoras de rendimiento.',
        ))


class PuntajeRelevanciaTests(SimpleTestCase):
    def test_phishing_paraguayo_supera_el_umbral(self):
        articulo = _articulo_phishing_paraguay()

        score = _calculate_relevance_score(
            title=articulo['titulo'], content=articulo['contenido'], url=articulo['url'],
        )

        self.assertGreaterEqual(score, MIN_RELEVANCE_SCORE)

    def test_operativo_policial_resta_puntaje(self):
        contenido = 'Los atacantes enviaron un correo falso con un enlace falso en Paraguay.'

        alerta = _calculate_relevance_score(
            title='Alerta de phishing en Paraguay', content=contenido, url=URL_PY,
        )
        detencion = _calculate_relevance_score(
            title='Detenidos por phishing en Paraguay', content=contenido, url=URL_PY,
        )

        self.assertGreaterEqual(alerta - detencion, 5)

    def test_vulnerabilidad_tecnica_resta_puntaje(self):
        contenido = 'Los atacantes envían un correo falso con un enlace falso en Paraguay.'

        alerta = _calculate_relevance_score(
            title='Alerta de phishing en Paraguay', content=contenido, url=URL_PY,
        )
        tecnica = _calculate_relevance_score(
            title='Alerta de phishing en Paraguay', content=contenido + ' Afecta al CVE-2024-1234.', url=URL_PY,
        )

        self.assertGreaterEqual(alerta - tecnica, 4)

    def test_foco_extranjero_sin_paraguay_resta_puntaje(self):
        base = 'Los atacantes envían un correo falso con un enlace falso.'

        sin_foco = _calculate_relevance_score(
            title='Alerta de phishing', content=base, url='https://www.ejemplo.com/nota',
        )
        con_foco = _calculate_relevance_score(
            title='Alerta de phishing', content=base + ' Ocurrió en Mexico.', url='https://www.ejemplo.com/nota',
        )

        self.assertEqual(sin_foco - con_foco, 4)

    def test_sin_senales_de_phishing_queda_bajo_el_umbral(self):
        score = _calculate_relevance_score(
            title='El clima de hoy en Paraguay',
            content='Se espera una jornada soleada con temperaturas agradables.',
            url='https://www.abc.com.py/clima',
        )

        self.assertLess(score, MIN_RELEVANCE_SCORE)


class FiltroFinalDeArticulosTests(SimpleTestCase):
    def test_acepta_articulo_que_cumple_los_cuatro_filtros(self):
        self.assertTrue(_passes_article_filters(_articulo_phishing_paraguay()))

    def test_rechaza_articulo_sin_material_utilizable(self):
        articulo = _articulo_phishing_paraguay(proceso_ataque='', secuencia_ataque='', ejemplos_ataque='')

        self.assertFalse(_passes_article_filters(articulo))

    def test_material_en_el_limite_del_minimo(self):
        articulo = _articulo_phishing_paraguay(
            proceso_ataque='x' * (MIN_EXTRACTED_MATERIAL - 1),
            secuencia_ataque='',
            ejemplos_ataque='',
        )
        self.assertFalse(_passes_article_filters(articulo))

        articulo['proceso_ataque'] = 'x' * MIN_EXTRACTED_MATERIAL
        self.assertTrue(_passes_article_filters(articulo))

    def test_rechaza_articulo_que_no_es_de_paraguay(self):
        articulo = _articulo_phishing_paraguay(url='https://www.ejemplo.com/nota')
        articulo['titulo'] = 'Alerta: falso correo del banco suplanta identidad a clientes'
        articulo['contenido'] = articulo['contenido'].replace('en Paraguay', 'en general')

        self.assertFalse(_passes_article_filters(articulo))


class FiltroFechasTests(SimpleTestCase):
    def test_parsea_formatos_iso_email_y_locales(self):
        self.assertEqual(_parse_date_strict('2025-09-10T08:30:00-03:00'), date(2025, 9, 10))
        self.assertEqual(_parse_date_strict('Wed, 10 Sep 2025 08:30:00 GMT'), date(2025, 9, 10))
        self.assertEqual(_parse_date_strict('10/09/2025'), date(2025, 9, 10))
        self.assertEqual(_parse_date_strict('10-09-2025'), date(2025, 9, 10))

    def test_fecha_invalida_o_vacia_devuelve_none(self):
        self.assertIsNone(_parse_date_strict(None))
        self.assertIsNone(_parse_date_strict('   '))
        self.assertIsNone(_parse_date_strict('no es una fecha'))

    def test_limite_minimo_de_antiguedad(self):
        self.assertTrue(_is_recent_enough(date.today()))
        self.assertTrue(_is_recent_enough(date(2022, 1, 1)))
        self.assertFalse(_is_recent_enough(date(2021, 12, 31)))


class NormalizacionItemABCTests(SimpleTestCase):
    """Verifica que un item de búsqueda de ABC pasa o no los filtros de fecha y contenido."""

    def _row(self, **overrides):
        row = {
            'title': 'Alerta: falso correo del banco suplanta identidad a clientes paraguayos',
            'description': 'Los atacantes envían un enlace falso en Paraguay.',
            'link': '/nacionales/alerta-phishing',
            'pubdateunix': int(time.time()),
        }
        row.update(overrides)
        return row

    def _patches(self, contenido):
        """Evita red y llamadas a la IA: el contenido enriquecido y la extracción se simulan."""
        return (
            patch('articulos.ingestion._enrich_article_content_with_html', return_value=(contenido, '')),
            patch('articulos.ingestion._extract_attack_context_with_ai', return_value=None),
            patch('articulos.ingestion._extract_attack_context', return_value=MATERIAL_SUFICIENTE),
        )

    def _normalize(self, row, contenido=None):
        contenido = contenido or _articulo_phishing_paraguay()['contenido']
        enrich, ai, regex = self._patches(contenido)
        with enrich, ai, regex:
            return _normalize_abc_search_item(row)

    def test_acepta_item_reciente_y_completa_la_url_relativa(self):
        resultado = self._normalize(self._row())

        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['url'], 'https://www.abc.com.py/nacionales/alerta-phishing')
        self.assertEqual(resultado['fuente'], 'ABC Color')

    def test_rechaza_item_sin_fecha_valida(self):
        self.assertIsNone(self._normalize(self._row(pubdateunix=None, pubdate='fecha rota')))

    def test_rechaza_item_demasiado_antiguo(self):
        viejo = int(time.mktime(date(2019, 6, 1).timetuple()))

        self.assertIsNone(self._normalize(self._row(pubdateunix=viejo)))

    def test_rechaza_item_que_no_es_phishing_paraguayo(self):
        resultado = self._normalize(
            self._row(title='Actualización de software', description='Nueva versión disponible.'),
            contenido='Nueva versión del software disponible para todos los usuarios.',
        )

        self.assertIsNone(resultado)
