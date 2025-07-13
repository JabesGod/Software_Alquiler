# permission_tags.py
from django import template
from django.utils.translation import gettext as _

register = template.Library()

@register.filter
def translate_app_label(app_label):
    translations = {
        'auth': 'Autenticación',
        'contenttypes': 'Tipos de contenido',
        'sessions': 'Sesiones',
        'admin': 'Administración',
        # Añade más traducciones según tus apps
    }
    return translations.get(app_label, app_label)

@register.filter
def translate_model_name(model_name):
    translations = {
        'user': 'Usuario',
        'group': 'Grupo',
        'permission': 'Permiso',
        'contenttype': 'Tipo de contenido',
        'session': 'Sesión',
        # Añade más traducciones según tus modelos
    }
    return translations.get(model_name, model_name)

@register.filter
def translate_permission(codename):
    action_translations = {
        'add': 'Agregar',
        'change': 'Editar',
        'delete': 'Eliminar',
        'view': 'Ver',
    }
    
    parts = codename.split('_')
    if len(parts) > 1:
        action = parts[0]
        return f"{action_translations.get(action, action.title())} {parts[1]}"
    return codename