from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capacitaciones', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RespuestaEjercicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('es_correcta', models.BooleanField(default=False)),
                ('fecha_respuesta', models.DateTimeField(auto_now_add=True)),
                ('ejercicio', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='respuestas', to='capacitaciones.ejercicio')),
                ('opcion_seleccionada', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='respuestas', to='capacitaciones.opcionejercicio')),
                ('usuario', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='respuestas_capacitacion', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'respuesta_capacitacion',
                'ordering': ['-fecha_respuesta'],
            },
        ),
    ]
