from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import F
from alquiler.models import Alquiler, DetalleAlquiler, Equipo

class Command(BaseCommand):
    help = 'Finaliza todos los alquileres activos cuya fecha de fin ya ha pasado.'

    def handle(self, *args, **options):
        hoy = timezone.now().date()
        
        alquileres_a_finalizar = Alquiler.objects.filter(
            estado_alquiler='activo',
            fecha_fin__lt=hoy
        )

        if not alquileres_a_finalizar.exists():
            self.stdout.write(self.style.SUCCESS('✅ No se encontraron alquileres vencidos para finalizar.'))
            return

        self.stdout.write(f"\n⏳ Se encontraron {alquileres_a_finalizar.count()} alquiler(es) vencido(s). Procesando...")

        for alquiler in alquileres_a_finalizar:
            try:
                with transaction.atomic():
                    alquiler.estado_alquiler = 'finalizado'
                    alquiler.save()

                    detalles = DetalleAlquiler.objects.filter(alquiler=alquiler)
                    for detalle in detalles:
                        equipo = detalle.equipo
                        equipo.cantidad_disponible = F('cantidad_disponible') + detalle.cantidad
                        equipo.save(update_fields=['cantidad_disponible'])
                        equipo.refresh_from_db()

                    self.stdout.write(self.style.SUCCESS(f"✅ Alquiler ID {alquiler.id} ({alquiler.cliente.nombre}) finalizado."))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error al finalizar el alquiler ID {alquiler.id}: {e}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Proceso de finalización de alquileres vencidos completado."))