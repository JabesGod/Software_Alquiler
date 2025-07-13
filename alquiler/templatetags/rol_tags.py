# usuarios/templatetags/rol_tags.py
from django import template

register = template.Library()

@register.filter
def has_rol(user, rol_name):
    return hasattr(user, 'rol') and user.rol.nombre_rol.lower() == rol_name.lower()

@register.filter
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.simple_tag
def tiene_permiso(user, codename):
    return user.has_perm(codename)
