from django.db import models
from django.utils import timezone

class Equipo(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('alquilado', 'En alquiler'),
        ('reservado', 'Reservado'),
    ]

    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    numero_serie = models.CharField(max_length=100, unique=True)
    especificaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    fecha_registro = models.DateField(auto_now_add=True)
    ubicacion = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.numero_serie}"

    # Método para verificar rápidamente disponibilidad
    def esta_disponible(self):
        return self.estado == 'disponible'

    # Método para historial de alquileres relacionados al equipo
    def historial_alquileres(self):
        return self.alquileres.select_related('cliente').order_by('-fecha_inicio')

    # Cantidad total de alquileres realizados al equipo
    def total_alquileres(self):
        return self.alquileres.count()

    # Próxima fecha en que estará disponible basado en alquileres activos
    def proxima_fecha_disponible(self):
        alquiler_activo = self.alquileres.filter(
            estado_alquiler='activo', fecha_fin__gte=timezone.now().date()
        ).order_by('fecha_fin').first()

        if alquiler_activo:
            return alquiler_activo.fecha_fin
        return timezone.now().date()

    # Método para cambiar fácilmente el estado del equipo
    def actualizar_estado(self, nuevo_estado):
        if nuevo_estado in dict(self.ESTADOS):
            self.estado = nuevo_estado
            self.save()
            return True
        return False

    # Equipos similares según marca o modelo
    def equipos_similares(self):
        return Equipo.objects.filter(
            models.Q(marca__iexact=self.marca) | models.Q(modelo__iexact=self.modelo)
        ).exclude(id=self.id)

    # Duración promedio de alquiler del equipo (en días)
    def duracion_promedio_alquiler(self):
        from django.db.models import Avg, F, ExpressionWrapper, DurationField

        promedio = self.alquileres.filter(
            estado_alquiler='finalizado'
        ).annotate(
            duracion=ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'), output_field=DurationField()
            )
        ).aggregate(promedio=Avg('duracion'))

        if promedio['promedio']:
            return promedio['promedio'].days
        return 0

    # Método para exportar información básica del equipo
    def exportar_informacion(self):
        return {
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'estado': self.estado,
            'ubicacion': self.ubicacion,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d'),
        }



class Cliente(models.Model):
    ESTADO_VERIFICACION = [
        ('pendiente', 'Pendiente'),
        ('verificado', 'Verificado'),
        ('rechazado', 'Rechazado'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    informacion_facturacion = models.TextField(blank=True, null=True)
    estado_verificacion = models.CharField(max_length=20, choices=ESTADO_VERIFICACION, default='pendiente')
    
    # Para documentos subidos (puedes usar muchos campos o un JSON)
    documento_rut = models.FileField(upload_to='documentos/', blank=True, null=True)
    documento_cedula = models.FileField(upload_to='documentos/', blank=True, null=True)
    contrato_firmado = models.FileField(upload_to='contratos/', blank=True, null=True)

    def __str__(self):
        return self.nombre


class Alquiler(models.Model):
    ESTADO_ALQUILER = [
        ('activo', 'Activo'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="alquileres")    
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_alquiler = models.CharField(max_length=20, choices=ESTADO_ALQUILER, default='activo')
    renovacion = models.BooleanField(default=False)
    aprobado_por = models.CharField(max_length=100, blank=True, null=True)
    contrato_firmado = models.BooleanField(default=False)

    def __str__(self):
        return f"Alquiler de {self.equipo} a {self.cliente}"



class Pago(models.Model):
    ESTADO_PAGO = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('parcial', 'Parcial'),
    ]

    METODOS = [
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('efectivo', 'Efectivo'),
    ]

    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODOS)
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO)
    factura_generada = models.BooleanField(default=False)
    referencia_transaccion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pago de {self.monto} para alquiler {self.alquiler.id}"


class Contrato(models.Model):
    alquiler = models.OneToOneField(Alquiler, on_delete=models.CASCADE)
    fecha_contratacion = models.DateField(auto_now_add=True)
    terminos_contrato = models.TextField()
    fecha_firma = models.DateField(blank=True, null=True)
    documento_contrato = models.FileField(upload_to='contratos/')

    def __str__(self):
        return f"Contrato #{self.id} - Alquiler {self.alquiler.id}"
