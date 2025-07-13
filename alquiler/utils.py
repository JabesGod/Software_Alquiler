# utils.py
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
import logging
from .models import Pago, Alquiler, Cliente
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
from functools import wraps

logger = logging.getLogger(__name__)

def enviar_notificacion_pago(pago, usuario):
    """
    Envía notificaciones por correo electrónico sobre el pago
    a cliente y administradores.
    """
    try:
        # Notificación al cliente
        if pago.alquiler.cliente.email:
            subject_cliente = f"Confirmación de pago #{pago.id}"
            message_cliente = render_to_string('emails/confirmacion_pago_cliente.html', {
                'pago': pago,
                'cliente': pago.alquiler.cliente,
                'alquiler': pago.alquiler
            })
            
            send_mail(
                subject=subject_cliente,
                message="",  # Versión texto plano se genera del HTML
                html_message=message_cliente,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[pago.alquiler.cliente.email],
                fail_silently=False
            )

        # Notificación a administradores
        subject_admin = f"Nuevo pago registrado - #{pago.id}"
        message_admin = render_to_string('emails/notificacion_pago_admin.html', {
            'pago': pago,
            'usuario': usuario,
            'alquiler': pago.alquiler
        })
        
        send_mail(
            subject=subject_admin,
            message="",
            html_message=message_admin,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ADMIN_EMAILS,
            fail_silently=False
        )

    except Exception as e:
        logger.error(f"Error enviando notificaciones de pago: {str(e)}", exc_info=True)


def verificar_estado_pago_alquiler(alquiler):
    """
    Verifica si un alquiler está completamente pagado y actualiza su estado.
    Retorna True si el estado fue actualizado.
    """
    try:
        total_pagado = alquiler.pagos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        if total_pagado >= alquiler.precio_total:
            alquiler.estado_alquiler = 'finalizado'
            alquiler.save()
            
            # Actualizar todos los pagos parciales a 'pagado'
            alquiler.pagos.filter(estado_pago='parcial').update(estado_pago='pagado')
            return True
        return False
    except Exception as e:
        logger.error(f"Error verificando estado de pago para alquiler {alquiler.id}: {str(e)}", exc_info=True)
        return False


def verificar_morosidad_cliente(cliente_id):
    """
    Verifica si un cliente tiene pagos vencidos y lo marca como moroso si es necesario.
    Retorna True si el cliente fue marcado como moroso.
    """
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        pagos_vencidos = Pago.objects.filter(
            alquiler__cliente=cliente,
            estado_pago__in=['pendiente', 'parcial'],
            fecha_vencimiento__lt=timezone.now().date()
        ).exists()
        
        if pagos_vencidos:
            cliente.estado_verificacion = 'rechazado'
            cliente.moroso = True
            cliente.fecha_marcado_moroso = timezone.now().date()
            cliente.save()
            return True
        return False
    except Exception as e:
        logger.error(f"Error verificando morosidad para cliente {cliente_id}: {str(e)}", exc_info=True)
        return False


def actualizar_pagos_vencidos():
    """
    Tarea programada para marcar pagos vencidos y clientes morosos.
    Retorna el número de pagos actualizados.
    """
    try:
        fecha_limite = timezone.now().date()
        pagos_vencidos = Pago.objects.filter(
            fecha_vencimiento__lt=fecha_limite,
            estado_pago__in=['pendiente', 'parcial']
        )
        
        count = 0
        for pago in pagos_vencidos:
            pago.estado_pago = 'vencido'
            pago.save()
            verificar_morosidad_cliente(pago.alquiler.cliente.id)
            count += 1
            
        return count
    except Exception as e:
        logger.error(f"Error actualizando pagos vencidos: {str(e)}", exc_info=True)
        return 0


def enviar_recordatorios_pago():
    """
    Envía recordatorios de pagos próximos a vencer (3 días antes).
    Retorna el número de notificaciones enviadas.
    """
    try:
        fecha_limite = timezone.now().date() + timedelta(days=3)
        pagos_proximos = Pago.objects.filter(
            fecha_vencimiento=fecha_limite,
            estado_pago__in=['pendiente', 'parcial']
        ).select_related('alquiler__cliente')
        
        count = 0
        for pago in pagos_proximos:
            cliente = pago.alquiler.cliente
            if not cliente.email:
                continue
                
            try:
                subject = f"Recordatorio de pago próximo - Alquiler #{pago.alquiler.id}"
                message = render_to_string('emails/recordatorio_pago.html', {
                    'pago': pago,
                    'cliente': cliente,
                    'dias_restantes': 3
                })
                
                send_mail(
                    subject=subject,
                    message="",
                    html_message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[cliente.email],
                    fail_silently=False
                )
                count += 1
            except Exception as e:
                logger.error(f"Error enviando recordatorio a {cliente.email}: {str(e)}", exc_info=True)
        
        return count
    except Exception as e:
        logger.error(f"Error en enviar_recordatorios_pago: {str(e)}", exc_info=True)
        return 0


def generar_comprobante_pago(pago):
    """
    Genera un comprobante de pago en formato PDF.
    Retorna el contenido del PDF o None si hay error.
    """
    try:
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Configuración del documento
        pdf.setTitle(f"Comprobante de Pago #{pago.id}")
        
        # Encabezado
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(1 * inch, 10 * inch, "Comprobante de Pago")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(1 * inch, 9.5 * inch, f"Número: {pago.id}")
        pdf.drawString(1 * inch, 9 * inch, f"Fecha: {pago.fecha_pago.strftime('%d/%m/%Y')}")
        
        # Información del pago
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(1 * inch, 8 * inch, "Detalles del Pago:")
        pdf.setFont("Helvetica", 12)
        
        info_pago = [
            f"Alquiler: #{pago.alquiler.id}",
            f"Cliente: {pago.alquiler.cliente.nombre}",
            f"Monto: ${pago.monto}",
            f"Método de pago: {pago.get_metodo_pago_display()}",
            f"Referencia: {pago.referencia_transaccion or 'N/A'}",
            f"Estado: {pago.get_estado_pago_display()}"
        ]
        
        y_position = 7.5 * inch
        for linea in info_pago:
            pdf.drawString(1 * inch, y_position, linea)
            y_position -= 0.4 * inch
        
        # Pie de página
        pdf.setFont("Helvetica", 10)
        pdf.drawString(1 * inch, 0.5 * inch, "Gracias por su pago")
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error generando comprobante para pago {pago.id}: {str(e)}", exc_info=True)
        return None


def calcular_interes_morosidad(pago):
    """
    Calcula intereses moratorios para pagos vencidos.
    Retorna el monto de intereses.
    """
    if pago.estado_pago != 'vencido':
        return Decimal('0.00')
    
    dias_vencido = (timezone.now().date() - pago.fecha_vencimiento).days
    if dias_vencido <= 0:
        return Decimal('0.00')
    
    # Tasa de interés moratorio (ejemplo: 1% mensual)
    tasa_mensual = Decimal('0.01')
    tasa_diaria = tasa_mensual / Decimal('30')
    intereses = pago.monto * tasa_diaria * Decimal(dias_vencido)
    
    # Redondear a 2 decimales
    return intereses.quantize(Decimal('0.01'))


def verificar_pagos_parciales_completos(alquiler):
    """
    Verifica si los pagos parciales suman el total y actualiza estados.
    """
    try:
        total_pagado = alquiler.pagos.filter(estado_pago__in=['pagado', 'parcial']).aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')
        
        if total_pagado >= alquiler.precio_total:
            # Actualizar alquiler
            alquiler.estado_alquiler = 'finalizado'
            alquiler.save()
            
            # Actualizar todos los pagos parciales
            alquiler.pagos.filter(estado_pago='parcial').update(estado_pago='pagado')
            return True
        return False
    except Exception as e:
        logger.error(f"Error verificando pagos parciales para alquiler {alquiler.id}: {str(e)}", exc_info=True)
        return False
    

def crear_pago_inicial(alquiler, aprobado_por=None):
    """Crea automáticamente el primer pago vinculado al alquiler"""
    if alquiler and not alquiler.es_reserva and alquiler.precio_total > 0:
        Pago.objects.create(
            alquiler=alquiler,
            monto=alquiler.precio_total,
            metodo_pago='pendiente',
            estado_pago='pendiente',
            fecha_vencimiento=alquiler.fecha_fin + timedelta(days=15),
            aprobado_por=aprobado_por
        )

def get_client_ip(request):
    """
    Obtiene la dirección IP real del cliente, incluso detrás de un proxy.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from django.core.exceptions import PermissionDenied
from functools import wraps

def rol_requerido(*roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated or not hasattr(request.user, 'rol'):
                raise PermissionDenied
            if request.user.rol.nombre_rol.lower() not in [r.lower() for r in roles_permitidos]:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
