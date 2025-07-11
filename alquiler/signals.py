# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alquiler, Cliente

@receiver(post_save, sender=Alquiler)
def actualizar_morosidad_cliente(sender, instance, **kwargs):
    instance.cliente.calcular_morosidad()