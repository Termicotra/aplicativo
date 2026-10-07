# Generated migration to remove usuario field from AIInteraction

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulaciones', '0012_remove_simulacion_usuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aiinteraction',
            name='usuario',
        ),
    ]
