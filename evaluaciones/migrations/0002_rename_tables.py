from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluaciones', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='ejercicio',
            table='ejercicio_evaluacion',
        ),
        migrations.AlterModelTable(
            name='opcionejercicio',
            table='opcion_evaluacion',
        ),
        migrations.AlterModelTable(
            name='respuestaejercicio',
            table='respuesta_evaluacion',
        ),
    ]
