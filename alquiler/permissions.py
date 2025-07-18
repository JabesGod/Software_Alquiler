from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(Alquiler)

Permission.objects.get_or_create(
    codename='override_moroso',
    name='Puede alquilar a clientes morosos/bloqueados',
    content_type=content_type
)