from django.core.management.base import BaseCommand
from alquiler.models import Alquiler
from django.utils import timezone

class Command(BaseCommand):
    help = 'Asigna números de factura a alquileres existentes que no tengan uno'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--prefijo',
            type=str,
            default='FACT',
            help='Prefijo para los números de factura (por defecto: FACT)'
        )
    
    def handle(self, *args, **options):
        prefijo = options['prefijo']
        alquileres = Alquiler.objects.filter(numero_factura__isnull=True).order_by('id')
        
        total = alquileres.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✅ Todos los alquileres ya tienen número de factura'))
            return
        
        self.stdout.write(f'🔍 Encontrados {total} alquileres sin número de factura')
        
        for i, alquiler in enumerate(alquileres, start=1):
            # Formato: PREFIJO-AÑO-NÚMERO (ej: FACT-2025-0001)
            year = alquiler.fecha_inicio.year
            numero = f"{prefijo}-{year}-{i:04d}"
            
            alquiler.numero_factura = numero
            alquiler.save()
            
            if i % 100 == 0 or i == total:
                self.stdout.write(f'⚡ Procesados {i}/{total} alquileres')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Se asignaron números de factura a {total} alquileres')
        )