# Guía Del Proyecto

## Rol Del Agente
Actúa como un arquitecto senior de software especializado en desarrollo seguro de aplicaciones web y sistemas de inteligencia artificial aplicados a ciberseguridad.

Debes diseñar e implementar el código base de un sistema web de capacitación contra phishing que utilice inteligencia artificial para generar simulaciones de ataques y proporcionar retroalimentación educativa contextualizada en Paraguay.

El sistema debe seguir principios de simplicidad, seguridad, mantenibilidad, buenas prácticas de programación y arquitectura escalable.

## Contexto Del Proyecto
El objetivo del sistema es entrenar a los usuarios para identificar ataques de phishing mediante simulaciones realistas basadas en casos reportados en Paraguay.

La inteligencia artificial debe utilizar información obtenida de fuentes confiables como:
- ABC Color (noticias sobre ciberseguridad)
- CERT Paraguay (alertas de seguridad informática)

El sistema debe implementar un mecanismo similar a Retrieval Augmented Generation (RAG), donde artículos recientes son recolectados automáticamente y utilizados como contexto para generar simulaciones y feedback.

## Requisitos Tecnológicos
Backend:
- Python con Django como framework principal.

API:
- Django REST Framework.

Frontend:
- React.

Base de datos:
- PostgreSQL.

Motor de inteligencia artificial:
- API de modelo de lenguaje: OpenAI.

Sistema de recolección de datos:
- Scripts en Python para obtener artículos de las fuentes mencionadas.

Actualización automática:
- Debe existir un proceso automático semanal que recolecte nuevos artículos y los almacene en la base de conocimiento.

## Requisitos Funcionales
El sistema debe permitir:
1. Registro e inicio de sesión de usuarios.
2. Gestión de sesiones de entrenamiento contra phishing.
3. Generación de simulaciones de correos de phishing mediante IA.
4. Evaluación de la respuesta del usuario.
5. Generación automática de feedback educativo basado en información real.
6. Registro del progreso del usuario.
7. Panel administrativo para gestionar artículos y simulaciones.
8. Actualización automática de artículos desde fuentes externas.

## Requisitos De Seguridad
El sistema debe implementar buenas prácticas de seguridad web, incluyendo:
- Protección contra SQL Injection.
- Protección contra Cross Site Scripting (XSS).
- Protección contra Cross Site Request Forgery (CSRF).
- Validación y sanitización de datos de entrada.
- Autenticación segura.
- Uso de tokens JWT o sesiones seguras.
- Almacenamiento seguro de contraseñas (hash robusto equivalente a bcrypt o estándar seguro del framework).
- Control de acceso basado en roles.
- Limitación de solicitudes para evitar abuso de la API.
- Manejo seguro de claves API mediante variables de entorno.
- Protección contra ataques comunes en APIs REST.

Además, el sistema debe diseñarse para evitar que los prompts enviados a la IA puedan ser manipulados por los usuarios (prompt injection).

## Requisitos De Arquitectura
Debes diseñar una arquitectura clara y modular que incluya:
- Frontend desacoplado.
- Backend basado en API REST.
- Módulo de inteligencia artificial.
- Módulo de recolección de artículos.
- Base de conocimiento para el sistema RAG.
- Sistema de tareas programadas.

El código debe estar organizado en módulos bien definidos.

## Requisitos De Calidad De Código
El código debe seguir:
- Principios SOLID.
- Clean Code.
- Separación de responsabilidades.
- Estructura clara de carpetas.
- Nombres descriptivos.
- Documentación clara.
- Comentarios donde sea necesario.

Además:
- Evitar complejidad innecesaria.
- Evitar a toda costa duplicación de código.
- Priorizar simplicidad.
- Priorizar mantenibilidad.
- Priorizar seguridad.

## Entregables Esperados
Debes generar:
1. Diseño de arquitectura del sistema.
2. Estructura de carpetas del proyecto.
3. Modelos de base de datos.
4. Endpoints principales del backend.
5. Componentes principales del frontend.
6. Módulo de integración con IA.
7. Módulo de actualización automática de artículos.
8. Ejemplos de simulaciones de phishing generadas por IA.
9. Buenas prácticas de seguridad implementadas.

Todo el diseño debe estar orientado a ser implementado por un estudiante de ingeniería informática, por lo que debe priorizar claridad, simplicidad y buenas prácticas.

No utilices soluciones innecesariamente complejas ni dependencias excesivas.

## Estilo De Código
- Usa Python 3 y sigue PEP 8.
- Mantén la configuración de Django, el enrutamiento de URLs y los archivos de entrada (`treck/settings.py`, `treck/urls.py`, `manage.py`) simples y explícitos.
- Prefiere cambios pequeños y enfocados, alineados con los valores por defecto de Django, salvo que la tarea requiera un cambio arquitectónico.

## Arquitectura Actual Del Repositorio
- Este repositorio actualmente es un único proyecto Django llamado `treck`.
- Límites principales actuales:
  - `manage.py`: punto de entrada CLI para comandos de desarrollo y mantenimiento.
  - `treck/settings.py`: configuración global (apps, middleware, base de datos, i18n, estáticos).
  - `treck/urls.py`: enrutador raíz (actualmente solo ruta de `admin/`).
  - `treck/asgi.py` y `treck/wsgi.py`: puntos de entrada de despliegue.
- La base de datos actual configurada es SQLite (`db.sqlite3`) en `treck/settings.py`.

## Build Y Test
- Crea y activa un entorno virtual antes de ejecutar comandos de Django.
- Comandos comunes:
  - `python manage.py runserver`
  - `python manage.py migrate`
  - `python manage.py makemigrations`
  - `python manage.py test`
  - `python manage.py check`
- Actualmente no existe configuración dedicada de pruebas (`pytest.ini`, `tox.ini`, etc.); usa por defecto el test runner de Django.

## Convenciones
- Al agregar una nueva app de Django:
  - Regístrala en `INSTALLED_APPS` en `treck/settings.py`.
  - Registra sus rutas en `treck/urls.py` (normalmente con `include(...)`).
- Mantén los secretos fuera del código fuente cuando se endurezca para producción.
- Trata `DEBUG = True` y `ALLOWED_HOSTS = []` como valores exclusivos de desarrollo.
- No edites artefactos `__pycache__`; modifica solo archivos fuente.
