from django.db import models

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
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
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
