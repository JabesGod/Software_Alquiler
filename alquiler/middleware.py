import json
from django.utils import timezone
from django.db import transaction
from user_agents import parse
from .models import UserAuditLog
from .utils import get_client_ip
from utils.audit_log import get_target_user_from_request


class AuditMiddleware:
    """
    Middleware para registrar automáticamente la actividad de los usuarios
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = [
            '/admin/jsi18n/',
            '/static/',
            '/media/',
            '/favicon.ico'
        ]

    def __call__(self, request):
        response = self.get_response(request)
        self._log_user_activity(request, response)
        return response

    def _should_log_request(self, request):
        """Determina si la solicitud debe ser registrada"""
        if not request.user.is_authenticated:
            return False
            
        path = request.path
        return not any(path.startswith(exempt) for exempt in self.exempt_paths)

    def _log_user_activity(self, request, response):
        """Registra la actividad del usuario"""
        if not self._should_log_request(request):
            return

        try:
            with transaction.atomic():
                user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
                action = self._determine_action(request, response)
                
                if action:  # Solo registrar si se pudo determinar una acción
                    details = {
                        'browser': user_agent.browser.family,
                        'os': user_agent.os.family,
                        'is_mobile': user_agent.is_mobile,
                        'path': request.path,
                        'method': request.method,
                        'view_name': self._get_view_name(request),
                        'status_code': response.status_code
                    }

                    UserAuditLog.objects.create(
                        user=request.user,
                        action=action,
                        status='success' if response.status_code < 400 else 'failed',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],  # Limitar longitud
                        details=details,
                        target_user=get_target_user_from_request(request)
                    )
        except Exception as e:
            # Importante: No dejar que los errores en el logging afecten la respuesta
            pass

    def _determine_action(self, request, response):
        """Determina el tipo de acción basado en la solicitud"""
        path = request.path.lower()
        
        # Acciones de autenticación
        if path == '/login/':
            return 'login_failed' if response.status_code != 200 else 'login'
        if path == '/logout/':
            return 'logout'
            
        # Acciones relacionadas con contraseñas
        if 'password' in path:
            if 'change' in path:
                return 'password_change'
            if 'reset' in path:
                return 'password_reset'
        
        # Acciones de gestión de usuarios
        if 'usuario' in path:
            if 'editar' in path:
                return self._determine_edit_action(request)
            if 'crear' in path:
                return 'user_create'
            if 'eliminar' in path:
                return 'user_delete'
        
        # Otras acciones administrativas
        if request.user.is_staff and request.method == 'POST':
            return self._determine_admin_action(request)
            
        return None

    def _determine_edit_action(self, request):
        """Determina el tipo de edición de usuario"""
        if request.method == 'POST':
            if 'is_active' in request.POST:
                return 'status_change'
            if 'rol' in request.POST:
                return 'role_change'
            if 'permisos' in request.POST:
                return 'permission_change'
        return 'user_edit'

    def _determine_admin_action(self, request):
        """Determina acciones administrativas específicas"""
        path = request.path.lower()
        if 'config' in path:
            return 'config_change'
        if 'export' in path:
            return 'export_data'
        if any(x in path for x in ['clientes', 'equipos', 'alquileres']):
            return 'data_access'
        return 'admin_action'

    def _get_view_name(self, request):
        """Obtiene el nombre de la vista desde el resolver_match"""
        if hasattr(request, 'resolver_match') and request.resolver_match:
            return request.resolver_match.view_name
        return None
    

