# Generated manually on 2025-10-05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='legajo',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Legajo'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='area',
            field=models.CharField(blank=True, choices=[('PRODUCCION', 'Producción'), ('MANTENIMIENTO', 'Mantenimiento'), ('ALMACEN', 'Almacén'), ('CALIDAD', 'Calidad'), ('ADMINISTRACION', 'Administración')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='turno_habitual',
            field=models.CharField(blank=True, choices=[('M', 'Mañana'), ('T', 'Tarde'), ('N', 'Noche'), ('R', 'Rotativo')], max_length=1, null=True),
        ),
    ]
