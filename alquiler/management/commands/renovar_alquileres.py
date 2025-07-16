# management/commands/renovar_alquileres.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from alquiler.models import Alquiler
from datetime import timedelta

class Command(BaseCommand):
    help = 'Renueva automáticamente los alquileres con renovación automática activada'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        alquileres_a_renovar = Alquiler.objects.filter(
            renovacion_automatica=True,
            fecha_fin__lte=hoy,
            estado_alquiler='activo'
        )

        for alquiler in alquileres_a_renovar:
            try:
                duracion = alquiler.fecha_fin - alquiler.fecha_inicio
                nuevo_fin = hoy + duracion
                
                nuevo_alquiler = Alquiler.objects.create(
                    cliente=alquiler.cliente,
                    fecha_inicio=hoy,
                    fecha_fin=nuevo_fin,
                    fecha_vencimiento=nuevo_fin,
                    con_iva=alquiler.con_iva,
                    observaciones=f"Renovación automática del alquiler #{alquiler.id}",
                    renovacion_automatica=True,
                    estado_alquiler='activo',
                    aprobado_por=alquiler.aprobado_por,
                    creado_por=alquiler.creado_por
                )
                
                # Copiar los detalles del alquiler
                for detalle in alquiler.detalles.all():
                    nuevo_alquiler.detalles.create(
                        equipo=detalle.equipo,
                        numeros_serie=detalle.numeros_serie,
                        periodo_alquiler=detalle.periodo_alquiler,
                        cantidad=detalle.cantidad,
                        precio_unitario=detalle.precio_unitario
                    )
                
                # Calcular el precio total del nuevo alquiler
                nuevo_alquiler.calcular_precio_total()
                
                self.stdout.write(self.style.SUCCESS(f'Renovado alquiler #{alquiler.id} como #{nuevo_alquiler.id}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error renovando alquiler #{alquiler.id}: {str(e)}'))