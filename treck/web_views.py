import re

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect, render

from articulos.models import Articulo
from capacitaciones.models import Ejercicio, OpcionEjercicio, RespuestaEjercicio
from simulaciones.ai_service import AIServiceError, generar_simulacion_y_feedback
from simulaciones.models import Simulacion
from .forms import UserRegisterForm


def _parse_email_simulation_text(raw_text: str) -> dict[str, object]:
    sender = ''
    subject = ''
    attachments: list[str] = []
    body_lines: list[str] = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()

        if lowered.startswith('de:') and not sender:
            sender = stripped.split(':', 1)[1].strip()
            continue

        if lowered.startswith('asunto:') and not subject:
            subject = stripped.split(':', 1)[1].strip()
            continue

        if lowered.startswith('adjunto:') or lowered.startswith('adjuntos:'):
            raw_attachments = stripped.split(':', 1)[1].strip()
            if raw_attachments:
                for name in re.split(r'[,;]', raw_attachments):
                    clean_name = name.strip()
                    if clean_name:
                        attachments.append(clean_name)
            continue

        body_lines.append(line)

    body = '\n'.join(body_lines)
    body = re.sub(r'\n{3,}', '\n\n', body).strip()

    return {
        'sender': sender,
        'subject': subject,
        'attachments': attachments,
        'body': body,
    }


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    simulaciones = (
        Simulacion.objects.filter(usuario=request.user)
        .select_related('articulo')
        .order_by('-fecha_creacion')[:20]
    )
    respuestas_qs = (
        RespuestaEjercicio.objects.filter(usuario=request.user)
        .select_related('ejercicio', 'opcion_seleccionada')
        .order_by('-fecha_respuesta')
    )
    progreso = respuestas_qs.aggregate(
        total=Count('id'),
        aciertos=Count('id', filter=Q(es_correcta=True)),
        errores=Count('id', filter=Q(es_correcta=False)),
    )
    total_respuestas = progreso['total'] or 0
    aciertos = progreso['aciertos'] or 0
    precision = round((aciertos / total_respuestas) * 100, 2) if total_respuestas else 0

    context = {
        'simulaciones': simulaciones,
        'progreso_capacitaciones': {
            'total': total_respuestas,
            'aciertos': aciertos,
            'errores': progreso['errores'] or 0,
            'precision': precision,
        },
        'respuestas_capacitaciones_recientes': respuestas_qs[:10],
    }
    return render(request, 'dashboard.html', context)


@login_required
def articulo_list_view(request):
    articulos = Articulo.objects.order_by('-fecha')
    return render(request, 'articulos/list.html', {'articulos': articulos})


@login_required
def articulo_contexto_view(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    contexto = {
        'proceso_ataque': articulo.proceso_ataque,
        'secuencia_ataque': articulo.secuencia_ataque,
        'recomendaciones': articulo.recomendaciones,
        'ejemplos_ataque': articulo.ejemplos_ataque,
        'origen_ataque': articulo.origen_ataque,
        'objetivo_ataque': articulo.objetivo_ataque,
        'canal_ataque': articulo.canal_ataque,
    }
    return render(
        request,
        'articulos/contexto.html',
        {
            'articulo': articulo,
            'contexto': contexto,
        },
    )


@login_required
def simulaciones_section_view(request):
    current_state = request.session.get('simulacion_actual', {})
    current_simulacion = None

    sim_id = current_state.get('simulacion_id')
    if sim_id:
        current_simulacion = (
            Simulacion.objects.filter(id=sim_id, usuario=request.user)
            .select_related('articulo')
            .first()
        )

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'generar':
            articulo = (
                Articulo.objects.annotate(
                    has_simulacion=Exists(
                        Simulacion.objects.filter(articulo_id=OuterRef('pk'))
                    )
                )
                .filter(has_simulacion=False)
                .order_by('-fecha')
                .first()
            )
            if not articulo:
                messages.info(request, 'No hay articulos pendientes: ya existe 1 simulacion por cada articulo.')
                return redirect('simulaciones_section')

            articulos_recientes = [
                {
                    'titulo': item.titulo,
                    'contenido': item.contenido[:600],
                    'canal_ataque': item.canal_ataque,
                    'fuente': item.fuente,
                    'fecha': item.fecha.isoformat(),
                }
                for item in Articulo.objects.order_by('-fecha')[:5]
            ]
            articulo_base = {
                'titulo': articulo.titulo,
                'contenido': articulo.contenido[:600],
                'proceso_ataque': articulo.proceso_ataque,
                'secuencia_ataque': articulo.secuencia_ataque,
                'recomendaciones': articulo.recomendaciones,
                'ejemplos_ataque': articulo.ejemplos_ataque,
                'origen_ataque': articulo.origen_ataque,
                'objetivo_ataque': articulo.objetivo_ataque,
                'canal_ataque': articulo.canal_ataque,
                'fuente': articulo.fuente,
                'fecha': articulo.fecha.isoformat(),
                'url': articulo.url,
            }

            try:
                ia_output = generar_simulacion_y_feedback(
                    prompt_usuario='Generar simulacion de fraude alineada al articulo base.',
                    articulo_base=articulo_base,
                    articulos_recientes=articulos_recientes,
                )
            except AIServiceError as exc:
                messages.error(request, f'No se pudo generar la simulacion: {exc}')
                return redirect('simulaciones_section')
            except Exception:
                messages.error(request, 'Error inesperado al generar la simulacion con IA.')
                return redirect('simulaciones_section')

            simulacion = Simulacion.objects.create(
                usuario=request.user,
                articulo=articulo,
                simulacion_texto=ia_output['simulacion'],
                resumen_justificacion=ia_output['resumen_justificacion'],
                resultado='incorrecto',
                feedback=ia_output['feedback'],
            )

            request.session['simulacion_actual'] = {
                'simulacion_id': simulacion.id,
                'esperado': 'phishing' if ia_output.get('es_phishing', 'true') == 'true' else 'no-phishing',
                'tipo_mensaje': ia_output.get('tipo_mensaje', 'correo'),
                'sender_email': ia_output.get('sender_email', ''),
                'subject': ia_output.get('subject', ''),
                'attachments': ia_output.get('attachments', []),
                'entidad_objetivo': ia_output.get('entidad_objetivo', 'Entidad objetivo'),
                'dominio_objetivo': ia_output.get('dominio_objetivo', ''),
                'enlace_senuelo': ia_output.get('enlace_senuelo', ''),
                'respondida': False,
                'acierto': None,
            }
            messages.success(request, 'Simulacion generada. Analiza el contenido y responde.')
            return redirect('simulaciones_section')

        if action == 'evaluar':
            if not current_simulacion:
                messages.error(request, 'Primero debes generar una simulacion.')
                return redirect('simulaciones_section')

            respuesta = request.POST.get('respuesta', '')
            esperado = current_state.get('esperado', 'phishing')
            acierto = respuesta == esperado
            current_simulacion.resultado = 'correcto' if acierto else 'incorrecto'
            current_simulacion.save(update_fields=['resultado'])

            current_state['respondida'] = True
            current_state['acierto'] = acierto
            current_state['respuesta_usuario'] = respuesta
            request.session['simulacion_actual'] = current_state

            if acierto:
                messages.success(request, 'Acertaste. Buena deteccion.')
            else:
                messages.error(request, 'No acertaste. Revisa las senales de fraude indicadas.')
            return redirect('simulaciones_section')

    simulaciones_historial = (
        Simulacion.objects.all()
        .select_related('articulo')
        .order_by('-fecha_creacion')[:10]
    )

    mensaje_render = {
        'sender': '',
        'subject': 'Notificacion de seguridad y verificacion',
        'attachments': [],
        'body': current_simulacion.simulacion_texto if current_simulacion else '',
    }

    if current_simulacion:
        parsed = _parse_email_simulation_text(current_simulacion.simulacion_texto)
        entidad = str(current_state.get('entidad_objetivo', 'entidad')).lower().strip() or 'entidad'
        domain_hint = str(current_state.get('dominio_objetivo', '')).lower().strip()
        safe_entidad = re.sub(r'[^a-z0-9-]+', '', entidad) or 'entidad'
        if not domain_hint:
            domain_hint = f'{safe_entidad}.com.py'
        message_domain = re.sub(r'[^a-z0-9.-]+', '', domain_hint) or f'{safe_entidad}.com.py'
        session_sender = str(current_state.get('sender_email', '')).strip()
        session_subject = str(current_state.get('subject', '')).strip()
        session_attachments = current_state.get('attachments', [])

        mensaje_render['sender'] = session_sender or parsed['sender'] or f'soporte.seguridad@{message_domain}'
        mensaje_render['subject'] = session_subject or parsed['subject'] or 'Notificacion de seguridad y verificacion'
        if isinstance(session_attachments, list) and session_attachments:
            mensaje_render['attachments'] = [str(item).strip() for item in session_attachments if str(item).strip()]
        else:
            mensaje_render['attachments'] = parsed['attachments']
        mensaje_render['body'] = parsed['body'] or current_simulacion.simulacion_texto

    context = {
        'simulacion_actual': current_simulacion,
        'simulacion_estado': current_state,
        'mensaje_render': mensaje_render,
        'simulaciones_historial': simulaciones_historial,
    }
    return render(request, 'simulaciones/section.html', context)


@login_required
def capacitaciones_section_view(request):
    ejercicios_qs = Ejercicio.objects.filter(activo=True).prefetch_related('opciones').order_by('id')
    ejercicios = list(ejercicios_qs)

    if not ejercicios:
        return render(
            request,
            'capacitaciones/section.html',
            {
                'ejercicio': None,
                'resultado': None,
                'ejercicios_total': 0,
                'indice_actual': 0,
                'prev_ejercicio_id': None,
                'next_ejercicio_id': None,
            },
        )

    ejercicio_id_query = request.GET.get('ejercicio')
    ejercicio_actual = ejercicios[0]

    if ejercicio_id_query and ejercicio_id_query.isdigit():
        for ejercicio in ejercicios:
            if ejercicio.id == int(ejercicio_id_query):
                ejercicio_actual = ejercicio
                break

    resultado = None
    if request.method == 'POST':
        ejercicio_id = request.POST.get('ejercicio_id', '')
        opcion_id = request.POST.get('opcion_id', '')

        if not ejercicio_id.isdigit() or not opcion_id.isdigit():
            messages.error(request, 'Debes seleccionar una opcion valida.')
            return redirect('capacitaciones_section')

        ejercicio_actual = get_object_or_404(Ejercicio, id=int(ejercicio_id), activo=True)
        opcion = get_object_or_404(OpcionEjercicio, id=int(opcion_id), ejercicio=ejercicio_actual)
        opcion_correcta = get_object_or_404(OpcionEjercicio, ejercicio=ejercicio_actual, es_correcta=True)
        es_correcta = opcion.es_correcta

        if es_correcta:
            feedback = (
                opcion.retroalimentacion_opcion
                or 'Respuesta correcta. Buen trabajo identificando la situacion.'
            )
            messages.success(request, 'Respuesta correcta.')
        else:
            feedback = (
                opcion.retroalimentacion_opcion
                or ejercicio_actual.retroalimentacion
                or 'Respuesta incorrecta. Revisa el concepto y vuelve a intentar.'
            )
            messages.error(request, 'Respuesta incorrecta.')

        resultado = {
            'es_correcta': es_correcta,
            'feedback': feedback,
            'opcion_correcta': opcion_correcta,
        }
        RespuestaEjercicio.objects.create(
            usuario=request.user,
            ejercicio=ejercicio_actual,
            opcion_seleccionada=opcion,
            es_correcta=es_correcta,
        )

    ids = [item.id for item in ejercicios]
    indice_actual = ids.index(ejercicio_actual.id)
    prev_ejercicio_id = ids[indice_actual - 1] if indice_actual > 0 else None
    next_ejercicio_id = ids[indice_actual + 1] if indice_actual < len(ids) - 1 else None

    context = {
        'ejercicio': ejercicio_actual,
        'resultado': resultado,
        'ejercicios_total': len(ejercicios),
        'indice_actual': indice_actual + 1,
        'prev_ejercicio_id': prev_ejercicio_id,
        'next_ejercicio_id': next_ejercicio_id,
    }
    return render(request, 'capacitaciones/section.html', context)
