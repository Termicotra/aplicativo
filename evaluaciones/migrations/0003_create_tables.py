from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0002_rename_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS ejercicio_evaluacion (
                id BIGSERIAL PRIMARY KEY,
                tema VARCHAR(120) NOT NULL,
                pregunta TEXT NOT NULL,
                concepto TEXT NOT NULL,
                ejemplo TEXT NOT NULL DEFAULT '',
                retroalimentacion TEXT NOT NULL,
                activo BOOLEAN NOT NULL DEFAULT true,
                fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL,
                fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS opcion_evaluacion (
                id BIGSERIAL PRIMARY KEY,
                texto VARCHAR(255) NOT NULL,
                es_correcta BOOLEAN NOT NULL DEFAULT false,
                retroalimentacion_opcion TEXT NOT NULL DEFAULT '',
                orden SMALLINT NOT NULL DEFAULT 1,
                ejercicio_id BIGINT NOT NULL REFERENCES ejercicio_evaluacion(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS respuesta_evaluacion (
                id BIGSERIAL PRIMARY KEY,
                es_correcta BOOLEAN NOT NULL DEFAULT false,
                fecha_respuesta TIMESTAMP WITH TIME ZONE NOT NULL,
                ejercicio_id BIGINT NOT NULL REFERENCES ejercicio_evaluacion(id) ON DELETE CASCADE,
                opcion_seleccionada_id BIGINT NOT NULL REFERENCES opcion_evaluacion(id) ON DELETE CASCADE,
                usuario_id BIGINT NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS ejercicio_evaluacion_tema ON ejercicio_evaluacion(tema);
            CREATE INDEX IF NOT EXISTS opcion_evaluacion_ejercicio_id ON opcion_evaluacion(ejercicio_id);
            CREATE INDEX IF NOT EXISTS respuesta_evaluacion_usuario_id ON respuesta_evaluacion(usuario_id);
            CREATE INDEX IF NOT EXISTS respuesta_evaluacion_ejercicio_id ON respuesta_evaluacion(ejercicio_id);
            """,
            reverse_sql="",
        ),
    ]
