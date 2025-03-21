from django.contrib import admin
from .models import Cliente, Equipo, Alquiler, Pago, Contrato

admin.site.register(Cliente)
admin.site.register(Equipo)
admin.site.register(Alquiler)
admin.site.register(Pago)
admin.site.register(Contrato)
