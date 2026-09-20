# Configuración de Tareas Programadas

Esta aplicación incluye una tarea que se ejecuta cada **15 días a las 3 AM** para:
1. Borrar tablas de artículos y simulaciones
2. Ejecutar ingestion de artículos
3. Generar nuevas simulaciones

## Opción 1: Heroku Scheduler (RECOMENDADO - Gratuito)

Heroku proporciona un addon gratuito para tareas programadas.

### Pasos:

1. **Instalar Heroku Scheduler:**
   ```bash
   heroku addons:create scheduler:standard -a treck-7759cedc445f
   ```

2. **Agregar la tarea al dashboard:**
   - Ve a: https://dashboard.heroku.com/apps/treck-7759cedc445f/resources
   - Busca "Heroku Scheduler"
   - Haz clic en ella
   - Clic en "Create Job"
   
3. **Configurar el job:**
   - **Dyno size:** Free
   - **Frequency:** Every 15 days
   - **Next run:** Configura la hora a las 3 AM (03:00)
   - **Command:** 
     ```
     python manage.py refresh_data
     ```
   
4. **Guardar y listo**

**Nota:** Heroku Scheduler tiene un límite de 10 minutos de ejecución. Si tu tarea toma más, necesitarás la Opción 3.

---

## Opción 2: APScheduler (Dedicado - Necesita dyno pagado)

Para ejecutar el scheduler como un proceso background separado.

### Pasos:

1. **Instalar dependencia:**
   ```bash
   pip install apscheduler
   ```

2. **Actualizar Procfile:**
   ```
   release: python manage.py migrate
   web: gunicorn treck.wsgi
   scheduler: python scheduler.py
   ```

3. **Push a Heroku:**
   ```bash
   git add Procfile requirements.txt scheduler.py
   git commit -m "Add scheduler process"
   git push heroku dev:main
   ```

4. **En Heroku Dashboard:**
   - Ve a Resources
   - Agrega un dyno "scheduler"
   - Selecciona Free o Hobby Plan

**Ventaja:** No tiene límite de tiempo de ejecución
**Desventaja:** Requiere un dyno adicional (costo)

---

## Opción 3: Servicio Externo (Gratuito)

Usa un servicio como EasyCron o cron-job.org

### Pasos:

1. Ve a https://www.easycron.com/
2. Crea una cuenta gratuita
3. Crea un nuevo "Cron Job"
4. **URL:** `https://treck-7759cedc445f.herokuapp.com/api/tasks/refresh-data/`
5. **Frequency:** Every 15 days at 03:00 AM
6. Guardar

**Nota:** Primero necesitamos crear un endpoint en tu API para esto

---

## Opción 4: GitHub Actions (Gratuito)

Ejecutar desde GitHub Actions sin usar recursos de Heroku.

### Pasos:

1. Crea `.github/workflows/scheduled-task.yml`:
   ```yaml
   name: Refresh Data
   
   on:
     schedule:
       - cron: '0 3 */15 * *'  # 3 AM cada 15 días
   
   jobs:
     refresh:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
           with:
             python-version: '3.12'
         - run: pip install -r requirements.txt
         - run: |
             export DJANGO_SETTINGS_MODULE=treck.settings
             python manage.py refresh_data --heroku-db=${{ secrets.HEROKU_DATABASE_URL }}
   ```

2. Agrega `HEROKU_DATABASE_URL` a GitHub Secrets

---

## Comandos Locales

Para probar la tarea localmente:

```bash
# Ejecutar inmediatamente
python manage.py refresh_data

# Ver logs
heroku logs --tail -a treck-7759cedc445f
```

---

## Monitoreo

Ver ejecuciones en Heroku:

```bash
# Logs de las últimas ejecuciones
heroku logs --tail -a treck-7759cedc445f | grep refresh_data

# Con más contexto
heroku logs --tail -a treck-7759cedc445f
```

---

## Recomendación

**Para el proyecto actual:** Usa **Opción 1 (Heroku Scheduler)** por ser:
- ✓ Gratuito
- ✓ Simple de configurar
- ✓ Integrado en Heroku
- ✓ Suficiente para tu caso (tarea de < 10 min)
