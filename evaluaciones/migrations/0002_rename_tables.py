from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ejercicio_capacitacion') THEN
                    ALTER TABLE IF EXISTS ejercicio_capacitacion RENAME TO ejercicio_evaluacion;
                END IF;
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'opcion_ejercicio') THEN
                    ALTER TABLE IF EXISTS opcion_ejercicio RENAME TO opcion_evaluacion;
                END IF;
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'respuesta_capacitacion') THEN
                    ALTER TABLE IF EXISTS respuesta_capacitacion RENAME TO respuesta_evaluacion;
                END IF;
            END $$;
            """,
            reverse_sql="",
        ),
    ]
