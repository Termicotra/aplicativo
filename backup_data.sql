-- Script SQL para cargar datos de capacitaciones y evaluaciones en Heroku
-- Generado automáticamente desde base de datos local
-- Ejecutar en: heroku pg:psql -a treck-7759cedc445f < backup_data.sql

-- Lecciones
INSERT INTO leccion_capacitacion (id, titulo, duracion, orden, contenido_titulo, activa, bloqueada, fecha_creacion, fecha_actualizacion) VALUES (1, 'Que es el Phishing?', '5 min', 1, 'Introduccion al Phishing', true, false, '2026-08-14 14:36:27.802417+00:00', '2026-08-14 14:36:27.802417+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO leccion_capacitacion (id, titulo, duracion, orden, contenido_titulo, activa, bloqueada, fecha_creacion, fecha_actualizacion) VALUES (2, 'Identificar URLs sospechosas', '7 min', 2, 'Analisis de URLs', true, false, '2026-08-14 14:36:27.883626+00:00', '2026-08-14 14:36:27.883626+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO leccion_capacitacion (id, titulo, duracion, orden, contenido_titulo, activa, bloqueada, fecha_creacion, fecha_actualizacion) VALUES (3, 'Correos electronicos falsos', '8 min', 3, 'Detectando emails fraudulentos', true, false, '2026-08-14 14:36:27.944657+00:00', '2026-08-14 14:36:27.944657+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO leccion_capacitacion (id, titulo, duracion, orden, contenido_titulo, activa, bloqueada, fecha_creacion, fecha_actualizacion) VALUES (4, 'Mensajes SMS fraudulentos', '6 min', 4, 'Seguridad en SMS', true, false, '2026-08-14 14:36:27.983841+00:00', '2026-08-14 14:36:27.983841+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO leccion_capacitacion (id, titulo, duracion, orden, contenido_titulo, activa, bloqueada, fecha_creacion, fecha_actualizacion) VALUES (5, 'Redes sociales y phishing', '7 min', 5, 'Amenazas en Redes Sociales', true, false, '2026-08-14 14:36:28.026380+00:00', '2026-08-14 14:36:28.026380+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO leccion_capacitacion (id, titulo, duracion, orden, contenido_titulo, activa, bloqueada, fecha_creacion, fecha_actualizacion) VALUES (6, 'Proteccion y prevencion', '10 min', 6, 'Mejores Practicas de Seguridad', true, false, '2026-08-14 14:36:28.062067+00:00', '2026-08-14 14:36:28.062067+00:00') ON CONFLICT (id) DO NOTHING;

-- Secciones de lecciones
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (1, 1, 'Definicion', 'El phishing es una forma de engano donde un atacante se hace pasar por una fuente confiable para obtener informacion personal o financiera de la victima.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (2, 1, 'Por que es peligroso?', 'En Paraguay, se registraron mas de 551 millones de intentos de ciberataques en la primera mitad de 2025. El phishing es una de las tecnicas mas utilizadas por ciberdelincuentes.', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (3, 1, 'Tipos comunes', '', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (4, 2, 'Senales de alerta', '', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (5, 2, 'Como verificar', 'Siempre pasa el cursor sobre los enlaces antes de hacer clic. En moviles, manten presionado el enlace para ver la URL completa.', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (6, 3, 'Indicadores de phishing en emails', '', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (7, 3, 'Ejemplo en Paraguay', 'Es comun recibir correos falsos que simulan ser de Tigo, Personal, o bancos locales solicitando "verificar tu cuenta" o "actualizar datos".', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (8, 4, 'Que es Smishing?', 'El smishing es phishing a traves de mensajes SMS. Los atacantes envian mensajes que parecen ser de bancos o servicios legitimando para robar informacion.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (9, 4, 'Como identificar', '', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (10, 5, 'Riesgos en redes sociales', 'Las redes sociales son un objetivo comun para phishing. Los atacantes crean perfiles falsos o usan tecnicas de social engineering para obtener acceso a cuentas.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (11, 5, 'Proteccion basica', '', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (12, 6, 'Medidas preventivas', '', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO seccion_leccion (id, leccion_id, encabezado, texto, orden) VALUES (13, 6, 'Si crees que eres victima', '', 2) ON CONFLICT (id) DO NOTHING;

-- Items de lista
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (1, 3, 'Email phishing: Correos falsos que imitan bancos o servicios', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (2, 3, 'Smishing: Mensajes SMS fraudulentos', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (3, 3, 'Vishing: Llamadas telefonicas enganosas', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (4, 3, 'Spear phishing: Ataques personalizados', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (5, 4, 'Dominios mal escritos: "bancobcp.com" vs "banc0bcp.com"', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (6, 4, 'Subdominios enganosos: "login.banco.sitiofalso.com"', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (7, 4, 'HTTP en lugar de HTTPS', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (8, 4, 'URLs acortadas de fuentes desconocidas', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (9, 6, 'Remitentes con dominios sospechosos', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (10, 6, 'Errores ortograficos y gramaticales', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (11, 6, 'Urgencia extrema o amenazas', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (12, 6, 'Solicitudes de informacion personal', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (13, 6, 'Archivos adjuntos inesperados', 5) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (14, 9, 'Mensajes de remitentes desconocidos', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (15, 9, 'Urgencia para hacer clic en enlaces', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (16, 9, 'Solicitud de datos personales o financieros', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (17, 9, 'URLs acortadas sospechosas', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (18, 11, 'No hagas clic en enlaces sospechosos en mensajes directos', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (19, 11, 'Verifica la identidad de perfiles antes de interactuar', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (20, 11, 'Usa autenticacion de dos factores', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (21, 11, 'No compartas informacion personal sensible', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (22, 12, 'Mantén software y sistemas operativos actualizados', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (23, 12, 'Usa contrasenas fuertes y unicas', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (24, 12, 'Activa autenticacion de dos factores', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (25, 12, 'Ten cuidado al descargar archivos adjuntos', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (26, 12, 'Verifica direcciones de correo electronico cuidadosamente', 5) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (27, 13, 'Cambia tus contrasenas inmediatamente', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (28, 13, 'Contacta a tu institucion financiera', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (29, 13, 'Reporta el incidente a las autoridades', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (30, 13, 'Monitorea tu cuenta para actividad sospechosa', 4) ON CONFLICT (id) DO NOTHING;
INSERT INTO item_lista_seccion (id, seccion_id, texto, orden) VALUES (31, 13, 'Considera un servicio de monitoreo de credito', 5) ON CONFLICT (id) DO NOTHING;

-- Ejercicios
INSERT INTO ejercicio_evaluacion (id, tema, pregunta, concepto, ejemplo, retroalimentacion, activo, fecha_creacion, fecha_actualizacion) VALUES (1, 'Phishing', 'Que indicador sugiere que un correo podria ser phishing?', 'El phishing usa suplantacion y urgencia para robar datos sensibles.', 'Un correo pide verificar cuenta bancaria con un enlace acortado.', 'Antes de hacer clic, valida remitente, dominio y tono del mensaje.', true, '2026-05-04 17:26:06.285196+00:00', '2026-08-14 13:53:53.748615+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO ejercicio_evaluacion (id, tema, pregunta, concepto, ejemplo, retroalimentacion, activo, fecha_creacion, fecha_actualizacion) VALUES (2, 'Smishing', 'En un SMS, cual es una senal comun de fraude?', 'El smishing es phishing por mensajes de texto con enlaces maliciosos.', 'Mensaje afirma bloqueo de cuenta y pide confirmar datos en un link.', 'No abras enlaces de SMS no verificados y consulta canales oficiales.', true, '2026-05-04 17:26:06.306463+00:00', '2026-08-14 13:53:53.771309+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO ejercicio_evaluacion (id, tema, pregunta, concepto, ejemplo, retroalimentacion, activo, fecha_creacion, fecha_actualizacion) VALUES (3, 'Ingenieria social', 'Que accion reduce el riesgo ante una solicitud inesperada de datos?', 'La ingenieria social manipula emociones para obtener informacion sensible.', 'Un supuesto soporte tecnico pide codigo MFA por telefono.', 'Verifica identidad por un canal alterno antes de compartir datos.', true, '2026-05-04 17:26:06.321043+00:00', '2026-08-14 13:53:53.782591+00:00') ON CONFLICT (id) DO NOTHING;
INSERT INTO ejercicio_evaluacion (id, tema, pregunta, concepto, ejemplo, retroalimentacion, activo, fecha_creacion, fecha_actualizacion) VALUES (4, 'Seguridad en Codigos QR', 'Cual es el riesgo mas relevante al escanear codigos QR en espacios publicos?', 'Los codigos QR pueden contener URLs maliciosas, malware o llevar a sitios de phishing. Su facilidad de escaneo y el desconocimiento de destino hacen que sean vectores de ataque.', 'Un codigo QR pegado sobre un cartel publicitario original redirige a un sitio falso que captura credenciales.', 'Antes de escanear, verifica visualmente que el codigo se vea integro y considera usar un app que muestre la URL antes de abrir.', true, '2026-08-14 13:53:53.790587+00:00', '2026-08-14 13:53:53.790587+00:00') ON CONFLICT (id) DO NOTHING;

-- Opciones de ejercicios
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (1, 1, 'Solicita usuario y contrasena por enlace externo.', true, 'Correcto. Pedir credenciales por enlace es una senal de riesgo.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (2, 1, 'Llega desde dominio institucional validado internamente.', false, 'Incorrecto. Ese escenario no muestra alerta por si solo.', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (3, 1, 'Tiene saludo personalizado y no solicita acciones urgentes.', false, 'Incorrecto. Esas caracteristicas no son tipicas de phishing.', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (4, 2, 'El numero no identificado exige accion inmediata con un enlace.', true, 'Correcto. La urgencia con enlace sospechoso es un patron de smishing.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (5, 2, 'El mensaje informa horario de atencion sin incluir links.', false, 'Incorrecto. Ese contenido no implica fraude por si mismo.', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (6, 2, 'El remitente coincide con el contacto oficial guardado.', false, 'Incorrecto. No es un indicador de ataque en ese contexto.', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (7, 3, 'Compartir el dato para evitar bloqueo inmediato.', false, 'Incorrecto. Nunca compartas datos sensibles sin validar identidad.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (8, 3, 'Confirmar solicitud con el area oficial por un canal independiente.', true, 'Correcto. Validar por otro canal corta el intento de manipulacion.', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (9, 3, 'Reenviar la solicitud a todos los contactos para decidir.', false, 'Incorrecto. Eso puede ampliar el impacto del fraude.', 3) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (10, 4, 'Los codigos QR siempre son seguros porque estan cifrados en la camara del telefono.', false, 'Incorrecto. Los QR no estan cifrados. El riesgo es el contenido o destino del enlace.', 1) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (11, 4, 'Pueden dirigir a URLs maliciosas o sitios de phishing sin que el usuario vea el destino real.', true, 'Correcto. El riesgo principal es que la URL esta oculta hasta escanear, permitiendo engano.', 2) ON CONFLICT (id) DO NOTHING;
INSERT INTO opcion_evaluacion (id, ejercicio_id, texto, es_correcta, retroalimentacion_opcion, orden) VALUES (12, 4, 'El riesgo es minimo si se escanea desde una red WiFi publica confiable.', false, 'Incorrecto. La red no afecta si el codigo apunta a un sitio malicioso.', 3) ON CONFLICT (id) DO NOTHING;
