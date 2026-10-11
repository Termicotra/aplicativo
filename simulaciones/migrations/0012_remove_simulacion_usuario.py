# Generated migration to remove usuario field from Simulacion

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulaciones', '0011_remove_simulacion_nombre_contacto'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulacion',
            name='usuario',
        ),
    ]
