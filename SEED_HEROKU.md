# Ejecutar Seed de Capacitaciones en Heroku sin CLI

## Paso 1: Obtener DATABASE_URL de Heroku

1. Ve a: https://dashboard.heroku.com/apps/treck-7759cedc445f/settings
2. Haz clic en "Reveal Config Vars"
3. Encuentra la variable `DATABASE_URL` y copia su valor completo
   - Debería verse algo como: `postgresql://user:password@host:5432/dbname`

## Paso 2: Ejecutar el Script

### Opción A: Ejecutar sin reset (actualiza datos existentes)
```bash
python seed_heroku.py "postgresql://user:password@host:5432/dbname"
```

### Opción B: Ejecutar con reset (borra y recrea todo)
```bash
python seed_heroku.py "postgresql://user:password@host:5432/dbname" --reset
```

## Ejemplo Completo

```bash
python seed_heroku.py "postgresql://u1234567890abcd:pabcdef1234567890@ec2-1-2-3-4.compute-1.amazonaws.com:5432/d1234567890abcd"
```

## Qué hace el script

- ✅ Se conecta a la base de datos remota de Heroku
- ✅ Ejecuta el seed de capacitaciones
- ✅ Crea/actualiza las 7 lecciones:
  1. Qué es el Phishing?
  2. Identificar URLs sospechosas
  3. Correos electrónicos falsos
  4. Mensajes SMS fraudulentos
  5. Redes sociales y phishing
  6. Ingeniería social y manipulación
  7. Protección y prevención

- Con `--reset`: Borra todas las lecciones previas y comienza desde cero
- Sin `--reset`: Mantiene lecciones existentes y actualiza/agrega nuevas

## Salida Esperada

```
============================================================
[SEED CAPACITACIONES HEROKU]
============================================================
Database: ec2-1-2-3-4.compute-1.amazonaws.com
Reset: No
============================================================

Ejecutando sin reset (actualizará datos existentes)...

Seed completado. Lecciones creadas: 1. Lecciones actualizadas: 6.

============================================================
[OK] Seed completado exitosamente
============================================================
```

## Requisitos

- Python 3.8+ instalado
- Django instalado (se usa desde el proyecto)
- Acceso de lectura a Heroku dashboard

## Solucionar Problemas

### "Error: Debes proporcionar el DATABASE_URL"
- Asegúrate de pasar el DATABASE_URL como primer argumento

### "Error de conexión a la base de datos"
- Verifica que copiastes correctamente el DATABASE_URL
- Asegúrate de que Heroku está activo y accesible

### "ModuleNotFoundError"
- Asegúrate de estar en el directorio correcto del proyecto
- Verifica que `treck` es el nombre correcto del settings module
