def empresa_context(request):
    from django.conf import settings
    return {
        'empresa': {
            'nombre': getattr(settings, 'EMPRESA_NOMBRE', 'Mi Empresa'),
            'direccion': getattr(settings, 'EMPRESA_DIRECCION', 'Dirección no configurada'),
            'telefono': getattr(settings, 'EMPRESA_TELEFONO', ''),
            'email': getattr(settings, 'EMPRESA_EMAIL', ''),
            'ruc': getattr(settings, 'EMPRESA_RUC', ''),
        }
    }