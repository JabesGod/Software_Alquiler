# Generated by Django 5.1.7 on 2025-03-21 16:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alquiler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alquiler',
            name='equipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alquileres', to='alquiler.equipo'),
        ),
    ]
