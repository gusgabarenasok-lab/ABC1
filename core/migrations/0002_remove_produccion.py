# Generated manually on 2025-10-05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Eliminar el modelo Produccion que ya no existe
        migrations.DeleteModel(
            name='Produccion',
        ),
    ]
