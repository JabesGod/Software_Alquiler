# Generated by Django 5.1.7 on 2025-07-16 21:15

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alquiler', '0009_alter_alquiler_iva_alter_alquiler_precio_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallealquiler',
            name='precio_unitario',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
    ]
