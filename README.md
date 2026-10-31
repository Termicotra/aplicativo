# TRECK

**TRECK** - Plataforma integral de educación y conciencia en ciberseguridad.

**T**ecnología · **R**iesgo · **E**ducación · **C**onciencia · **K**now-how

Una plataforma educativa integral para detección y prevención de phishing e ingeniería social, desarrollada en Django REST Framework.

## Descripción General

TRECK combina tecnología, evaluación de riesgos y educación pedagógica para desarrollar conciencia sobre ciberseguridad y proporcionar conocimiento práctico aplicable.

El sistema proporciona tres módulos educativos interconectados:

- **Capacitaciones**: Lecciones secuenciales sobre phishing e ingeniería social
- **Simulaciones**: Escenarios realistas de ataque generados por IA basados en amenazas reales
- **Evaluaciones**: Ejercicios interactivos para medir competencias específicas

El sistema ingesta automáticamente noticias de ciberseguridad desde fuentes paraguayas (ABC Color, CERT Paraguay), extrae contexto de ataque usando IA, y genera simulaciones educativas dinámicas.

## Características Principales

- 🤖 **Generación de Simulaciones con IA**: Crea escenarios realistas de phishing usando GPT-4o-mini
- 📊 **Seguimiento de Progreso Dinámico**: Calcula progreso en tiempo real desde datos de BD (33,33% cada módulo)
- 🌍 **Ingesta Automatizada**: Scrapea y procesa artículos de seguridad y regenera simulaciones cada 15 días mediante `python manage.py refresh_data`. En Heroku, un job programado (Heroku Scheduler) ejecuta ese comando cada 24 horas; el comando solo refresca si han pasado 15 días desde la última ejecución
- 🔍 **Filtrado Inteligente**: 4 niveles de validación para garantizar relevancia y calidad
- 📱 **Multi-canal**: Soporta correo, SMS, WhatsApp y simulaciones web
- 🔐 **Seguridad**: Validaciones contra inyección de prompts y coherencia de dominios

## Requisitos Previos

- Python 3.12+
- PostgreSQL 14+
- OpenAI API key
- Git

## Instalación

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd aplicativo

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# o .venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env con:
# DATABASE_URL=postgresql://user:password@localhost:5432/treck_db
# OPENAI_API_KEY=sk-...
# SECRET_KEY=tu-clave-secreta

# 5. Crear BD
createdb treck_db
python manage.py migrate
python manage.py seed_capacitaciones
python manage.py seed_evaluaciones
```

## Ejecución

```bash
# Servidor de desarrollo
python manage.py runserver

# Documentación: http://localhost:8000/api/docs/

# Refresco de artículos y simulaciones (ingesta + generación)
python manage.py refresh_data
python manage.py refresh_data --force  # Ignora el plazo de 15 días

# Generación de simulaciones
python generate_simulations.py
python generate_simulations.py --all  # Regenerar todas
```

## Endpoints Principales

```
POST   /api/users/auth/login/
POST   /api/users/auth/register/
GET    /api/users/mi-progreso/                          # Progreso dinámico
GET    /api/capacitaciones/lecciones/
POST   /api/capacitaciones/lecciones/{id}/marcar_completada/
GET    /api/simulaciones/
POST   /api/simulaciones/registrar-respuesta/
GET    /api/evaluaciones/
POST   /api/evaluaciones/responder/
GET    /api/evaluaciones/estadisticas/
```

## Estructura

```
aplicativo/
├── articulos/           # Ingesta (ABC Color, CERT Paraguay)
├── capacitaciones/      # Lecciones
├── evaluaciones/        # Ejercicios
├── simulaciones/        # Motor de IA
├── users/              # Autenticación
└── treck/              # Configuración
```

## Notas de Desarrollo

- El progreso se calcula dinámicamente: cada módulo contribuye 1/3
- Las simulaciones se validan contra 3 criterios: coherencia, especificidad, realismo
- La ingesta filtra artículos en 4 niveles: Paraguay, relevancia, flujo de ataque, material útil

## Licencia

Proyecto Final de Grado - Universidad Católica Nuestra Señora de la Asunción - Campus Guairá

## Contacto

- Autor: Federico Traversi
- Email: federico.traversi@uc.edu.py
