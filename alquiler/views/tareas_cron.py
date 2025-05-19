from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from alquiler.models import Alquiler

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
