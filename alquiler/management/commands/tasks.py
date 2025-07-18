from django.core.management.base import BaseCommand
from alquiler.utils import actualizar_morosidad_clientes

class Command(BaseCommand):
    help = 'Actualiza el estado de morosidad de los clientes'

    def handle(self, *args, **options):
        actualizar_morosidad_clientes()
        self.stdout.write(self.style.SUCCESS('Morosidad de clientes actualizada correctamente'))

# alquiler/tasks.py
from datetime import date
from decimal import Decimal
from django.db.models import Sum
from alquiler.models import Cliente, Pago

def actualizar_morosidad_clientes():
    print("🔄 Ejecutando tarea: actualizar_morosidad_clientes")

    clientes = Cliente.objects.all()

    for cliente in clientes:
        print(f"👤 Revisando cliente: {cliente.nombre}")

        pagos_vencidos = Pago.objects.filter(
            alquiler__cliente=cliente,
            estado_pago__in=['pendiente', 'parcial'],
            fecha_vencimiento__lt=date.today()
        )

        if pagos_vencidos.exists():
            deuda_total = pagos_vencidos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
            dias_mora = (date.today() - pagos_vencidos.earliest('fecha_vencimiento').fecha_vencimiento).days

            cliente.moroso = True
            cliente.dias_mora = dias_mora
            cliente.deuda_total = deuda_total
            cliente.fecha_marcado_moroso = date.today()
            cliente.save()

            print(f"⚠️ Cliente marcado como moroso: {cliente.nombre} - {dias_mora} días - ${deuda_total}")
        else:
            print(f"✅ Cliente al día: {cliente.nombre}")