from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('capacitaciones', '0002_respuestaejercicio'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Ejercicio',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('tema', models.CharField(max_length=120)),
                        ('pregunta', models.TextField()),
                        ('concepto', models.TextField()),
                        ('ejemplo', models.TextField(default='')),
                        ('retroalimentacion', models.TextField()),
                        ('activo', models.BooleanField(default=True)),
                        ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                        ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'db_table': 'ejercicio_capacitacion',
                        'ordering': ['-fecha_creacion'],
                    },
                ),
                migrations.CreateModel(
                    name='OpcionEjercicio',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('texto', models.CharField(max_length=255)),
                        ('es_correcta', models.BooleanField(default=False)),
                        ('retroalimentacion_opcion', models.TextField(blank=True, default='')),
                        ('orden', models.PositiveSmallIntegerField(default=1)),
                        ('ejercicio', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='opciones', to='evaluaciones.ejercicio')),
                    ],
                    options={
                        'db_table': 'opcion_ejercicio',
                        'ordering': ['orden', 'id'],
                    },
                ),
                migrations.AddConstraint(
                    model_name='opcionejercicio',
                    constraint=models.UniqueConstraint(fields=('ejercicio', 'orden'), name='unique_orden_por_ejercicio'),
                ),
                migrations.AddConstraint(
                    model_name='opcionejercicio',
                    constraint=models.UniqueConstraint(condition=Q(es_correcta=True), fields=('ejercicio',), name='unique_respuesta_correcta_por_ejercicio'),
                ),
                migrations.CreateModel(
                    name='RespuestaEjercicio',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('es_correcta', models.BooleanField(default=False)),
                        ('fecha_respuesta', models.DateTimeField(auto_now_add=True)),
                        ('ejercicio', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='respuestas', to='evaluaciones.ejercicio')),
                        ('opcion_seleccionada', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='respuestas', to='evaluaciones.opcionejercicio')),
                        ('usuario', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='respuestas_capacitacion', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'respuesta_capacitacion',
                        'ordering': ['-fecha_respuesta'],
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
