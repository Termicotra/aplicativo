# Treck — Descripción completa del proyecto

Resumen
-------
Treck es una plataforma de capacitación contra phishing diseñada para generar simulaciones de ataques realistas y proporcionar retroalimentación educativa contextualizada. Utiliza una base de conocimiento alimentada por ingesta automática de artículos (fuentes públicas y de confianza), aplica técnicas RAG (Retrieval-Augmented Generation) y llama a un servicio de lenguaje (OpenAI u otro) para crear contenidos y feedback adaptativo.

Objetivos
---------
- Entrenar usuarios para identificar correos y escenarios de phishing mediante simulaciones realistas.
- Mantener las simulaciones alineadas con casos y noticias reales (ingesta periódica de artículos).
- Ofrecer feedback educativo automático y seguimiento del progreso de los participantes.
- Proveer una API REST y panel administrativo para gestionar contenidos y resultados.

Principales funcionalidades
--------------------------
- Registro e inicio de sesión de usuarios (app `users`).
- Gestión de sesiones de capacitación y ejercicios (app `capacitaciones`).
- Ingesta automática y manual de artículos (app `articulos`) desde fuentes externas.
- Módulo RAG que utiliza artículos para proporcionar contexto a la IA.
- Generación de simulaciones de phishing mediante IA (app `simulaciones`).
- Evaluación automática de respuestas del usuario y generación de feedback educativo.
- Registro y seguimiento del progreso del usuario.
- Panel administrativo (`/admin/`) para gestionar artículos, simulaciones y usuarios.
- Scripts autónomos: `update_articles.py` y `generate_simulations.py`.

Arquitectura general
--------------------
- Frontend: React (desacoplado, consume la API REST del backend).
- Backend: Django + Django REST Framework (APIs, lógica de negocio).
- Base de datos: PostgreSQL (recomendado) o SQLite en desarrollo.
- Motor IA: API externa (OpenAI u otro) accesible desde `simulaciones/ai_service.py`.
- Ingesta: scripts y cron jobs que ejecutan `update_articles.py` regularmente.
- Tareas asíncronas: opción a integrar Celery + Redis para procesos pesados.

Estructura de carpetas (resumen relevante)
-----------------------------------------
- `articulos/` — modelos, vistas y lógica de ingestión.
- `simulaciones/` — generación y gestión de simulaciones; integración IA en `ai_service.py`.
- `capacitaciones/` — sesiones y ejercicios para usuarios.
- `users/` — modelos y endpoints relacionados a autenticación y perfiles.
- `docs/` — documentación y guías (aquí se encuentra este archivo).
- `update_articles.py`, `generate_simulations.py` — scripts principales fuera del ciclo request/response.

Modelos principales (conceptuales)
---------------------------------
- Articulo: fuente, título, fecha, canal, contenido, ejemplos_ataque, metadatos.
- Simulacion: referencia a `Articulo`, plantilla de correo, riesgo, resumen, justificación, estado, resultados.
- Capacitacion / Sesion: ejercicios asignados, participantes, fecha, resultados agregados.
- RespuestaEjercicio: respuesta del usuario, calificación, feedback generado.
- Usuario: roles (admin, instructor, participante), metadata y progreso.

Endpoints REST clave (ejemplos)
-------------------------------
- `POST /api/auth/login/` — iniciar sesión.
- `POST /api/auth/register/` — registrar usuario.
- `GET /api/articulos/` — listar artículos.
- `POST /api/articulos/ingest/` — disparar ingesta (protegido: admin/instructor).
- `GET /api/simulaciones/` — listar simulaciones.
- `POST /api/simulaciones/generate/` — generar simulaciones (requiere permisos).
- `POST /api/capacitaciones/{id}/submit/` — enviar respuestas y obtener evaluación.

Flujo de ingesta y generación de simulaciones
--------------------------------------------
1. Ingesta: `update_articles.py` recupera artículos desde fuentes configuradas y los almacena en la tabla `Articulo`.
2. Generación: `generate_simulations.py` procesa artículos recientes y crea `Simulacion` usando `simulaciones/ai_service.py`.
3. Pruebas/QA: administradores revisan simulaciones en el admin y, si es necesario, las editan antes de habilitarlas para participantes.

Seguridad y consideraciones
---------------------------
- Validación y sanitización: todas las entradas desde el frontend o API deben validarse y sanitizarse para prevenir XSS y SQLi.
- Autenticación: usar tokens JWT o sesiones seguras; endpoints sensibles requieren permisos basados en roles.
- Gestión de secretos: almacenar `OPENAI_API_KEY`, `DJANGO_SECRET_KEY` y credenciales fuera del repositorio (variables de entorno, vault).
- Rate limiting: proteger endpoints expuestos con límites de peticiones para evitar abuso.
- Protección CSRF: seguir las prácticas de Django para formularios y cabeceras en llamadas API.
- Prompt injection: limitar y sanitizar cualquier contenido de usuario que pueda concatenarse en prompts; aplicar plantillas fijas y validación estric­ta.

Integración IA (RAG)
--------------------
- La base de conocimiento está compuesta por artículos ingeridos.
- Para generar simulaciones o feedback, el módulo RAG recupera documentos relevantes (por relevancia/fechas) y los adjunta como contexto al prompt enviado al modelo.
- `simulaciones/ai_service.py` centraliza llamadas a la API de IA y aplica protecciones básicas sobre prompts.

Automatización y despliegue
---------------------------
- Ingesta programada:
  - Cron (Linux): añadir entrada que ejecute `python /ruta/update_articles.py` semanalmente.
  - Windows: Programador de tareas.
- Opcional: crear un comando de management de Django (`manage.py ingest_articles`) que envuelva el script para facilitar despliegue y logging.
- Contenedores: crear `Dockerfile` y `docker-compose.yml` (servicios: web, db, redis) para despliegues reproducibles.
- Producción: usar Gunicorn + Nginx, servir assets estáticos con WhiteNoise o CDN, activar HTTPS.

Pruebas y calidad
-----------------
- Tests: hay tests unitarios y de integración en cada app (`tests.py`). Ejecutar con `python manage.py test`.
- Formato: aplicar `black`/`isort` y linters si se desean (no incluidos por defecto).

Variables de entorno importantes
--------------------------------
- `DJANGO_SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `REDIS_URL`.
- Ejemplo en `.env.example` en la raíz del proyecto.

Operaciones de mantenimiento
---------------------------
- Backup de la base de datos periódicamente.
- Rotación de claves y revisión de permisos de acceso.
- Monitorización de fallos en las llamadas a la API de IA y reintentos controlados.


