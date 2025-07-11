from django.contrib.auth import get_user_model
from alquiler.models import UserAuditLog



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


def get_target_user_from_request(request):
    """
    Extrae el usuario objetivo de la solicitud basado en parámetros comunes
    """
    User = get_user_model()
    
    # Buscar en diferentes lugares comunes
    user_id = (request.POST.get('user_id') or 
               request.GET.get('user_id') or
               request.POST.get('usuario_id') or
               request.GET.get('usuario_id') or
               request.resolver_match.kwargs.get('usuario_id', None))
    
    if user_id and user_id != str(request.user.id):
        try:
            return User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            pass
    
    return None

def log_custom_action(user, action, status='success', request=None, target_user=None, **details):
    """
    Registra una acción personalizada manualmente
    
    Args:
        user: Usuario que realiza la acción
        action: Tipo de acción (debe coincidir con ACTION_CHOICES)
        status: Estado de la acción ('success', 'failed', 'warning')
        request: Objeto request opcional para extraer IP y user-agent
        target_user: Usuario afectado por la acción (opcional)
        details: Diccionario con detalles adicionales
    """
    log_data = {
        'user': user,
        'action': action,
        'status': status,
        'details': details,
        'target_user': target_user
    }
    
    if request:
        log_data.update({
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar longitud
        })
    
    return UserAuditLog.objects.create(**log_data)