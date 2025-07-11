from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from alquiler.models import Alquiler, Pago, Cliente
from django.conf import settings

def enviar_alertas_vencimiento():
    fecha_aviso = timezone.now().date() + timedelta(days=2)
    proximos_a_vencer = Alquiler.objects.filter(
        fecha_fin=fecha_aviso,
        estado_alquiler='activo'
    )

    if proximos_a_vencer.exists():
        print(f"Enviando alertas para alquileres que vencen el: {fecha_aviso}")
    else:
        print(f"No hay alquileres próximos a vencer para {fecha_aviso}")
        return

    for alquiler in proximos_a_vencer:
        asunto = '⚠️ Aviso: Vencimiento Próximo del Alquiler'
        mensaje = (
            f'Estimado {alquiler.cliente.nombre},\n\n'
            f'El alquiler del equipo "{alquiler.equipo}" '
            f'vence el día {alquiler.fecha_fin}.\n'
            'Por favor, realice la devolución o renovación correspondiente.\n\n'
            'Gracias,\nEquipo de soporte'
        )

        try:
            send_mail(
                asunto,
                mensaje,
                'noreply@tusitio.com',
                [alquiler.cliente.email],
                fail_silently=False,
            )
            print(f"Alerta enviada a {alquiler.cliente.email}")
        except Exception as e:
            print(f"Error al enviar a {alquiler.cliente.email}: {e}")




def verificar_pagos_vencidos():
    """Marca pagos vencidos y clientes morosos"""
    fecha_actual = timezone.now().date()
    pagos_vencidos = Pago.objects.filter(
        fecha_vencimiento__lt=fecha_actual,
        estado_pago='pendiente'
    )
    
    for pago in pagos_vencidos:
        pago.estado_pago = 'vencido'
        pago.save()
        
        # Marcar cliente como moroso
        cliente = pago.alquiler.cliente
        cliente.moroso = True
        cliente.fecha_marcado_moroso = fecha_actual
        cliente.save()

def enviar_recordatorios_pago():
    """Envía recordatorios de pagos próximos a vencer"""
    fecha_limite = timezone.now().date() + timedelta(days=3)  # 3 días antes
    pagos_proximos = Pago.objects.filter(
        fecha_vencimiento=fecha_limite,
        estado_pago='pendiente'
    ).select_related('alquiler__cliente')
    
    for pago in pagos_proximos:
        cliente = pago.alquiler.cliente
        try:
            send_mail(
                'Recordatorio de pago próximo',
                f'Estimado {cliente.nombre}, le recordamos que tiene un pago pendiente por ${pago.monto} que vence el {pago.fecha_vencimiento}.',
                settings.DEFAULT_FROM_EMAIL,
                [cliente.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error enviando recordatorio a {cliente.email}: {str(e)}")