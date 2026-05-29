# Treck — Simulador de capacitaciones anti-phishing

Breve: proyecto Django para generar simulaciones de phishing y capacitaciones basadas en artículos y IA.

## Requisitos
- Python 3.10+
- Git
- PostgreSQL (opcional, por defecto usa SQLite)

## Instalación rápida (desarrollo)
1. Clona el repositorio y sitúate en la carpeta del proyecto.

2. Crea y activa un entorno virtual:

   - Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   - macOS / Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Configura variables de entorno (ejemplo mínimo):

Create a `.env` file or export these env vars in tu entorno:

- `DJANGO_SECRET_KEY` — clave secreta de Django
- `DEBUG` — `True` (desarrollo) o `False` (producción)
- `DATABASE_URL` — URL de conexión si usas PostgreSQL (opcional)
- `OPENAI_API_KEY` — clave para la integración con el servicio de IA
- `OPENAI_MODEL` — modelo por defecto (ej: `gpt-4o`)

5. Aplica migraciones:

```bash
python manage.py migrate
```

6. (Opcional) Crea un superusuario para acceder al admin:

```bash
python manage.py createsuperuser
```

7. Carga datos iniciales (semillas):

```bash
python manage.py seed_capacitaciones
```

8. Ejecuta el servidor de desarrollo:

```bash
python manage.py runserver
```

## Base de datos
- Por defecto el proyecto está configurado para SQLite (desarrollo).
- Para producción: usar PostgreSQL y ajustar `DATABASE_URL`. Se incluye un script SQL de creación en `sql/create_all_tables_postgres.sql`.

## Actualización de artículos
- Hay un script para actualizar/recopilar artículos: `update_articles.py`.
- Para tareas programadas revisa `docs/cron_job.md`.

## Ingesta de artículos y generación de simulaciones
Este proyecto incluye scripts para: (1) ingestar artículos desde fuentes configuradas y (2) generar simulaciones de phishing basadas en esos artículos.

- Ingesta de artículos (ejecución manual):

```bash
# Ejecuta la ingesta y guarda artículos en la base de datos
python update_articles.py
```

El script `update_articles.py` recolecta los artículos configurados en la app `articulos` y los almacena en la base de conocimiento usada por el sistema RAG. Para automatizarlo semanalmente revisa `docs/cron_job.md`.

- Generación de simulaciones (ejecución manual):

```bash
# Genera simulaciones a partir de artículos y reglas/plantillas
python generate_simulations.py
```

El script `generate_simulations.py` crea simulaciones en la app `simulaciones` usando el contexto de los artículos almacenados y el servicio de IA configurado (requiere `OPENAI_API_KEY`). Puedes ejecutar ambos scripts en secuencia: primero la ingesta, luego la generación de simulaciones.

Ejemplo de flujo recomendado:

```bash
python update_articles.py
python generate_simulations.py
```

Si prefieres una integración con tareas programadas, configura un cron o un job del sistema que ejecute `update_articles.py` semanalmente y, si lo deseas, `generate_simulations.py` después de la ingesta.


## Ejecutar tests

```bash
python manage.py test
```

## Notas de seguridad
- Mantén las claves y secretos fuera del repositorio; usa variables de entorno.
- En producción setear `DEBUG=False` y `ALLOWED_HOSTS` adecuadamente.
- Revisa `treck/settings.py` para opciones de seguridad adicionales.

## Integración con IA
- Se espera una variable `OPENAI_API_KEY` para los servicios que usan IA (archivo(s) en `simulaciones/ai_service.py`).
- Protege y valida cualquier entrada de usuario que pueda influir en prompts para evitar prompt injection.

## Recursos adicionales
- Rutas y vistas principales en `treck/urls.py` y las apps `articulos`, `simulaciones`, `capacitaciones`, `users`.
- Ver `docs/cron_job.md` para ejemplo de job semanal de ingestión de artículos.