from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from alquiler.models import Pago, Cliente
from django.db.models import Q, Sum

class Command(BaseCommand):
    help = 'Verifica pagos vencidos y actualiza morosidad de clientes'

    def handle(self, *args, **options):
        self.verificar_pagos_vencidos()
        self.actualizar_morosidad_clientes()
        self.stdout.write(self.style.SUCCESS('Tarea completada exitosamente'))

    def verificar_pagos_vencidos(self):
        Pago.objects.filter(
            Q(fecha_vencimiento__lt=timezone.now().date()) &
            Q(estado_pago__in=['pendiente', 'parcial'])
        ).update(estado_pago='vencido')

    def actualizar_morosidad_clientes(self):
        fecha_limite = timezone.now().date() - timedelta(days=2)
        clientes_morosos = Cliente.objects.filter(
            Q(alquileres__pagos__estado_pago__in=['pendiente', 'parcial', 'vencido']) &
            Q(alquileres__pagos__fecha_vencimiento__lte=fecha_limite)
        ).distinct()

        for cliente in clientes_morosos:
            pago_mas_atrasado = Pago.objects.filter(
                alquiler__cliente=cliente,
                estado_pago__in=['pendiente', 'parcial', 'vencido']
            ).order_by('fecha_vencimiento').first()

            if pago_mas_atrasado:
                cliente.moroso = True
                cliente.dias_mora = (timezone.now().date() - pago_mas_atrasado.fecha_vencimiento).days
                cliente.deuda_total = Pago.objects.filter(
                    alquiler__cliente=cliente,
                    estado_pago__in=['pendiente', 'parcial', 'vencido']
                ).aggregate(total=Sum('monto'))['total'] or 0
                cliente.save()

        Cliente.objects.filter(moroso=True).exclude(
            id__in=clientes_morosos.values('id')
        ).update(moroso=False, dias_mora=0, deuda_total=0)