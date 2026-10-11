# Generated migration to remove unused nombre_contacto field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulaciones', '0010_simulacion_nombre_contacto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulacion',
            name='nombre_contacto',
        ),
    ]
