# Generated by Django 5.1.7 on 2025-05-26 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alquiler', '0012_alter_cliente_tipo_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='alquiler',
            name='fecha_creacion',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='alquiler',
            name='numero_factura',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
