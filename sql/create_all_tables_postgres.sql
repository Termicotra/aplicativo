-- Script SQL (Postgres) generado automáticamente — Tablas del proyecto
-- NO ejecutar sin revisar. Refleja los modelos Django encontrados en el repo.
-- Ajustar referencias a usuarios si el proyecto usa un `AUTH_USER_MODEL` personalizado.

-- Tabla: articulo
CREATE TABLE IF NOT EXISTS articulo (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    proceso_ataque TEXT NOT NULL DEFAULT '',
    secuencia_ataque TEXT NOT NULL DEFAULT '',
    recomendaciones TEXT NOT NULL DEFAULT '',
    ejemplos_ataque TEXT NOT NULL DEFAULT '',
    origen_ataque TEXT NOT NULL DEFAULT '',
    objetivo_ataque TEXT NOT NULL DEFAULT '',
    canal_ataque VARCHAR(30) NOT NULL DEFAULT 'indefinido',
    fuente VARCHAR(100) NOT NULL,
    url VARCHAR(200) NOT NULL UNIQUE,
    fecha DATE NOT NULL
);

-- Índice sugerido
-- CREATE INDEX idx_articulo_fecha ON articulo(fecha);


-- Tabla: simulacion
CREATE TABLE IF NOT EXISTS simulacion (
    id SERIAL PRIMARY KEY,
    usuario INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    articulo INTEGER NOT NULL REFERENCES articulo(id) ON DELETE CASCADE,
    es_phishing BOOLEAN NOT NULL DEFAULT TRUE,
    simulacion_texto TEXT NOT NULL DEFAULT '',
    tipo_mensaje VARCHAR(20) NOT NULL DEFAULT 'correo',
    sender_email VARCHAR(255) NOT NULL DEFAULT '',
    subject VARCHAR(255) NOT NULL DEFAULT '',
    attachments JSONB NOT NULL DEFAULT '[]'::jsonb,
    enlace_senuelo TEXT NOT NULL DEFAULT '',
    entidad_objetivo VARCHAR(255) NOT NULL DEFAULT '',
    dominio_objetivo VARCHAR(255) NOT NULL DEFAULT '',
    resumen_justificacion TEXT NOT NULL DEFAULT '',
    resultado VARCHAR(20) NOT NULL DEFAULT 'sin-responder',
    feedback TEXT NOT NULL DEFAULT '',
    tipo_generacion VARCHAR(20) NOT NULL DEFAULT 'inicial',
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    fecha_respuesta TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    es_mostrada BOOLEAN NOT NULL DEFAULT FALSE
);

-- Constraints/Checks sugeridos (opcional):
-- ALTER TABLE simulacion
--     ADD CONSTRAINT simulacion_resultado_check CHECK (resultado IN ('correcto','incorrecto','sin-responder')),
--     ADD CONSTRAINT simulacion_tipo_generacion_check CHECK (tipo_generacion IN ('inicial','regenerado'));

-- Índices sugeridos
-- CREATE INDEX idx_simulacion_usuario ON simulacion(usuario);
-- CREATE INDEX idx_simulacion_articulo ON simulacion(articulo);


-- Tabla: ejercicio_capacitacion
CREATE TABLE IF NOT EXISTS ejercicio_capacitacion (
    id SERIAL PRIMARY KEY,
    tema VARCHAR(120) NOT NULL,
    pregunta TEXT NOT NULL,
    concepto TEXT NOT NULL,
    ejemplo TEXT NOT NULL DEFAULT '',
    retroalimentacion TEXT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Tabla: opcion_ejercicio
CREATE TABLE IF NOT EXISTS opcion_ejercicio (
    id SERIAL PRIMARY KEY,
    ejercicio INTEGER NOT NULL REFERENCES ejercicio_capacitacion(id) ON DELETE CASCADE,
    texto VARCHAR(255) NOT NULL,
    es_correcta BOOLEAN NOT NULL DEFAULT FALSE,
    retroalimentacion_opcion TEXT NOT NULL DEFAULT '',
    orden SMALLINT NOT NULL DEFAULT 1
);

-- Constraints / índices equivalentes a las UniqueConstraint en Django
CREATE UNIQUE INDEX IF NOT EXISTS unique_orden_por_ejercicio ON opcion_ejercicio (ejercicio, orden);
-- Índice parcial para garantizar una única respuesta correcta por ejercicio
CREATE UNIQUE INDEX IF NOT EXISTS unique_respuesta_correcta_por_ejercicio ON opcion_ejercicio (ejercicio) WHERE es_correcta;

-- Tabla: respuesta_capacitacion
CREATE TABLE IF NOT EXISTS respuesta_capacitacion (
    id SERIAL PRIMARY KEY,
    usuario INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    ejercicio INTEGER NOT NULL REFERENCES ejercicio_capacitacion(id) ON DELETE CASCADE,
    opcion_seleccionada INTEGER NOT NULL REFERENCES opcion_ejercicio(id) ON DELETE CASCADE,
    es_correcta BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_respuesta TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Índices sugeridos
-- CREATE INDEX idx_respuesta_usuario ON respuesta_capacitacion(usuario);
-- CREATE INDEX idx_respuesta_ejercicio ON respuesta_capacitacion(ejercicio);

-- Notas:
-- 1) Este script asume la tabla `auth_user` (el User por defecto de Django). Si usas un modelo de usuario personalizado, reemplaza las referencias a `auth_user(id)` por la tabla correcta.
-- 2) Revisar longitudes (`VARCHAR`) y `NOT NULL`/`DEFAULT` según necesidades reales y las migraciones existentes.
-- 3) Las columnas con `auto_now_add`/`auto_now` se mapearon a `TIMESTAMP WITH TIME ZONE` con `DEFAULT now()`.
-- 4) Ajustar tipos y constraints adicionales (FK, CHECKs) según la lógica de negocio.

-- Sección opcional: tablas del sistema de autenticación de Django (por defecto)
-- Si tu proyecto usa un `AUTH_USER_MODEL` personalizado, reemplaza o elimina esta sección.

-- Tabla: auth_user (esquema simplificado del User por defecto de Django)
CREATE TABLE IF NOT EXISTS auth_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Tabla: auth_group
CREATE TABLE IF NOT EXISTS auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Tabla: auth_permission (simplified)
CREATE TABLE IF NOT EXISTS auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL
);

-- Tablas intermedias para relaciones many-to-many
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE (user_id, group_id)
);

CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE (user_id, permission_id)
);

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE (group_id, permission_id)
);

-- Tablas auxiliares de Django comúnmente presentes
CREATE TABLE IF NOT EXISTS django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE (app_label, model)
);

CREATE TABLE IF NOT EXISTS django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Fin del script
