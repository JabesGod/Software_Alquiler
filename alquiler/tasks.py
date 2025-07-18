from django.core.management.base import BaseCommand
from alquiler.utils import actualizar_morosidad_clientes

class Command(BaseCommand):
    help = 'Actualiza el estado de morosidad de los clientes'

    def handle(self, *args, **options):
        actualizar_morosidad_clientes()
        self.stdout.write(self.style.SUCCESS('Morosidad de clientes actualizada correctamente'))

