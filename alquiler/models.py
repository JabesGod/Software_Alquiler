from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.conf import settings
import os
from decimal import Decimal
from django.db.models import Q, Sum

def equipo_foto_upload_path(instance, filename):
    """Función para definir la ruta de subida de fotos"""
    return f'equipos/{instance.equipo.numero_serie}/{filename}'

class Equipo(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('alquilado', 'En alquiler'),
        ('reservado', 'Reservado'),
        ('mantenimiento', 'En mantenimiento'),
    ]
    
    # Campos básicos
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    numero_serie = models.CharField(max_length=100, unique=True)
    especificaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    fecha_registro = models.DateField(auto_now_add=True)
    ubicacion = models.CharField(max_length=100)
    
    # Campos de inventario
    cantidad_total = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad total",
        help_text="Número total de unidades idénticas de este equipo"
    )
    
    cantidad_disponible = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad disponible",
        help_text="Número de unidades disponibles para alquiler"
    )
    
    # Campos de precios de alquiler
    precio_dia = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    
    precio_semana = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por semana",
        help_text="Precio de alquiler por una semana (7 días)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    precio_mes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por mes",
        help_text="Precio de alquiler por un mes (30 días)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    precio_trimestre = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por trimestre",
        help_text="Precio de alquiler por tres meses (90 días)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    precio_semestre = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por semestre",
        help_text="Precio de alquiler por seis meses (180 días)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    precio_anio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por año",
        help_text="Precio de alquiler por un año (365 días)",
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    
    # Campos descriptivos
    descripcion_larga = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción detallada",
        help_text="Descripción completa con formato HTML permitido"
    )
    
    es_html = models.BooleanField(
        default=False,
        verbose_name="Usar HTML",
        help_text="Marcar si la descripción contiene formato HTML"
    )
    
    # Campos para valoración
    valoracion_promedio = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0)],
        verbose_name="Valoración promedio"
    )

    # Métodos relacionados con inventario y precios
    def actualizar_disponibilidad(self):
        """Actualiza la cantidad disponible basada en alquileres activos"""
        from django.db.models import Sum, Q
        alquileres_activos = self.alquileres.filter(
            Q(estado_alquiler='activo') | Q(estado_alquiler='reservado'),
            fecha_fin__gte=timezone.now().date()
        ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        self.cantidad_disponible = max(0, self.cantidad_total - alquileres_activos)
        
        # Actualizar estado general basado en disponibilidad
        if self.cantidad_disponible == 0:
            self.estado = 'alquilado'
        elif self.estado == 'alquilado' and self.cantidad_disponible > 0:
            self.estado = 'disponible'
        
        self.save()
    
    def obtener_precio_por_periodo(self, periodo):
        """Devuelve el precio para el período especificado"""
        periodos = {
            'dia': self.precio_dia,
            'semana': self.precio_semana or (self.precio_dia * 7 * Decimal('0.9')),  # 10% descuento
            'mes': self.precio_mes or (self.precio_dia * 30 * Decimal('0.8')),      # 20% descuento
            'trimestre': self.precio_trimestre or (self.precio_dia * 90 * Decimal('0.75')),
            'semestre': self.precio_semestre or (self.precio_dia * 180 * Decimal('0.7')),
            'anio': self.precio_anio or (self.precio_dia * 365 * Decimal('0.65'))
        }
        return periodos.get(periodo.lower(), Decimal('0'))
    
    def calcular_mejor_precio(self, dias):
        """Calcula el precio óptimo para un número dado de días"""
        from decimal import Decimal
        opciones = []
        
        if dias >= 1:
            opciones.append(('día', dias, self.precio_dia * dias))
        
        if dias >= 7:
            semanas = dias // 7
            resto = dias % 7
            opciones.append((
                'semana', 
                semanas,
                self.obtener_precio_por_periodo('semana') * semanas + 
                self.precio_dia * resto
            ))
        
        if dias >= 30:
            meses = dias // 30
            resto = dias % 30
            opciones.append((
                'mes',
                meses,
                self.obtener_precio_por_periodo('mes') * meses + 
                self.precio_dia * resto
            ))
        
        if dias >= 90:
            trimestres = dias // 90
            resto = dias % 90
            opciones.append((
                'trimestre',
                trimestres,
                self.obtener_precio_por_periodo('trimestre') * trimestres + 
                self.precio_dia * resto
            ))
        
        if dias >= 180:
            semestres = dias // 180
            resto = dias % 180
            opciones.append((
                'semestre',
                semestres,
                self.obtener_precio_por_periodo('semestre') * semestres + 
                self.precio_dia * resto
            ))
        
        if dias >= 365:
            años = dias // 365
            resto = dias % 365
            opciones.append((
                'año',
                años,
                self.obtener_precio_por_periodo('anio') * años + 
                self.precio_dia * resto
            ))
        
        if not opciones:
            return ('día', self.precio_dia * dias)
        
        # Seleccionar la opción más económica
        mejor_opcion = min(opciones, key=lambda x: x[2])
        return (mejor_opcion[0], mejor_opcion[2])
    
    def hay_disponibilidad(self, cantidad=1, fecha_inicio=None, fecha_fin=None):
        """
        Verifica si hay suficientes equipos disponibles para un período específico.
        Si no se especifican fechas, verifica disponibilidad actual.
        """
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin")
                
            # Verificar conflictos con alquileres existentes
            alquileres_conflicto = self.alquileres.filter(
                Q(estado_alquiler='activo') | Q(estado_alquiler='reservado'),
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio
            ).aggregate(total=Sum('cantidad'))['total'] or 0
            
            return self.cantidad_total - alquileres_conflicto >= cantidad
        return self.cantidad_disponible >= cantidad

    # Métodos relacionados con fotos
    def obtener_foto_principal(self):
        """Obtiene la foto principal o la predeterminada"""
        foto = self.fotos.filter(es_principal=True).first() or self.fotos.first()
        if foto:
            return foto.foto.url
        return os.path.join(settings.STATIC_URL, 'media/tecnonacho.png')
    
    def tiene_fotos(self):
        """Verifica si el equipo tiene fotos asociadas"""
        return self.fotos.exists()
    
    # Métodos para descripción
    def descripcion_corta(self, length=150):
        """Devuelve una versión corta de la descripción"""
        if not self.descripcion_larga:
            return ""
        
        if self.es_html:
            # Elimina etiquetas HTML para la versión corta
            text = strip_tags(self.descripcion_larga)
            return Truncator(text).chars(length)
        return Truncator(self.descripcion_larga).chars(length)
    
    def descripcion_como_html(self):
        """Devuelve la descripción como HTML seguro"""
        from django.utils.html import mark_safe
        if self.es_html and self.descripcion_larga:
            return mark_safe(self.descripcion_larga)
        return mark_safe(f"<p>{self.descripcion_larga}</p>" if self.descripcion_larga else "")
    
    # Métodos estándar
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.numero_serie} ({self.cantidad_disponible}/{self.cantidad_total})"
    
    def esta_disponible(self):
        return self.estado == 'disponible' and self.cantidad_disponible > 0
    
    def historial_alquileres(self):
        return self.alquileres.select_related('cliente').order_by('-fecha_inicio')
    
    def total_alquileres(self):
        return self.alquileres.count()
    
    def proxima_fecha_disponible(self):
        alquiler_activo = self.alquileres.filter(
            Q(estado_alquiler='activo') | Q(estado_alquiler='reservado'),
            fecha_fin__gte=timezone.now().date()
        ).order_by('fecha_fin').first()

        return alquiler_activo.fecha_fin if alquiler_activo else timezone.now().date()
    
    def actualizar_estado(self, nuevo_estado):
        if nuevo_estado in dict(self.ESTADOS):
            self.estado = nuevo_estado
            self.save()
            return True
        return False
    
    def equipos_similares(self, limit=5):
        return Equipo.objects.filter(
            Q(marca__iexact=self.marca) | Q(modelo__iexact=self.modelo)
        ).exclude(id=self.id)[:limit]
    
    def duracion_promedio_alquiler(self):
        from django.db.models import Avg, F, ExpressionWrapper, DurationField

        promedio = self.alquileres.filter(
            estado_alquiler='finalizado'
        ).annotate(
            duracion=ExpressionWrapper(
                F('fecha_fin') - F('fecha_inicio'), output_field=DurationField()
            )
        ).aggregate(promedio=Avg('duracion'))

        return promedio['promedio'].days if promedio['promedio'] else 0
    
    def exportar_informacion(self):
        return {
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'estado': self.get_estado_display(),
            'ubicacion': self.ubicacion,
            'cantidad_total': self.cantidad_total,
            'cantidad_disponible': self.cantidad_disponible,
            'precios': {
                'dia': float(self.precio_dia),
                'semana': float(self.precio_semana) if self.precio_semana else None,
                'mes': float(self.precio_mes) if self.precio_mes else None,
                'trimestre': float(self.precio_trimestre) if self.precio_trimestre else None,
                'semestre': float(self.precio_semestre) if self.precio_semestre else None,
                'anio': float(self.precio_anio) if self.precio_anio else None,
            },
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d'),
            'foto_principal': self.obtener_foto_principal(),
            'descripcion_corta': self.descripcion_corta(),
            'especificaciones': self.especificaciones,
        }

    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['marca', 'modelo']
        constraints = [
            models.CheckConstraint(
                check=models.Q(valoracion_promedio__gte=0.0) & models.Q(valoracion_promedio__lte=5.0),
                name="valoracion_promedio_rango"
            ),
            models.CheckConstraint(
                check=models.Q(cantidad_disponible__lte=models.F('cantidad_total')),
                name="cantidad_disponible_no_mayor_total"
            ),
            models.CheckConstraint(
                check=models.Q(precio_dia__gte=0),
                name="precio_dia_positivo"
            ),
            models.CheckConstraint(
                check=models.Q(cantidad_total__gte=0),
                name="cantidad_total_positiva"
            )
        ]



class FotoEquipo(models.Model):
    equipo = models.ForeignKey(
        Equipo,
        related_name='fotos',
        on_delete=models.CASCADE,
        verbose_name="Equipo asociado"
    )
    foto = models.ImageField(
        upload_to=equipo_foto_upload_path,
        verbose_name="Archivo de imagen",
        help_text="Suba una foto del equipo"
    )
    es_principal = models.BooleanField(
        default=False,
        verbose_name="Foto principal",
        help_text="Marcar si esta es la foto principal del equipo"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    
    def clean(self):
        """Valida que solo haya una foto principal por equipo"""
        if self.es_principal:
            if FotoEquipo.objects.filter(equipo=self.equipo, es_principal=True).exclude(id=self.id).exists():
                raise ValidationError("Ya existe una foto principal para este equipo.")
    
    def save(self, *args, **kwargs):
        """Garantiza que solo haya una foto principal"""
        if self.es_principal:
            FotoEquipo.objects.filter(equipo=self.equipo, es_principal=True).update(es_principal=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Foto de {self.equipo.marca} {self.equipo.modelo} - {self.descripcion or 'Sin descripción'}"
    
    class Meta:
        verbose_name = "Foto de equipo"
        verbose_name_plural = "Fotos de equipos"
        ordering = ['-es_principal', 'fecha_subida']

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
        ('reservado', 'Reservado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='alquileres')
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
    firma_cliente = models.ImageField(upload_to='firmas/', blank=True, null=True)
    documento_contrato = models.FileField(upload_to='contratos/')

    def __str__(self):
        return f"Contrato #{self.id} - Alquiler {self.alquiler.id}"
    


class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre_rol



class UsuarioManager(BaseUserManager):
    def _create_user(self, nombre_usuario, password, **extra_fields):
        """Método base para creación de usuarios"""
        if not nombre_usuario:
            raise ValueError("El nombre de usuario es obligatorio.")
        
        # Asignación automática de rol cliente si no se especifica
        if 'rol' not in extra_fields:
            extra_fields['rol'] = Rol.objects.get_or_create(
                nombre_rol="cliente",
                defaults={'descripcion': 'Rol por defecto para clientes'}
            )[0]
        
        user = self.model(nombre_usuario=nombre_usuario, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, nombre_usuario, password=None, **extra_fields):
        """Crea un usuario regular con rol cliente por defecto"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(nombre_usuario, password, **extra_fields)

    def create_superuser(self, nombre_usuario, password, **extra_fields):
        """Crea un superusuario con rol administrador"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Asignar rol de administrador
        extra_fields['rol'], _ = Rol.objects.get_or_create(
            nombre_rol="administrador",
            defaults={'descripcion': 'Administrador del sistema'}
        )
        
        return self._create_user(nombre_usuario, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre_usuario = models.CharField(max_length=100, unique=True)
    estado_usuario = models.CharField(max_length=20, default='activo')
    ultimo_acceso = models.DateTimeField(auto_now=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)  # Cambiado a PROTECT para mayor seguridad
    cliente = models.OneToOneField('Cliente', on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'

    def save(self, *args, **kwargs):
        """Asigna automáticamente el rol de cliente si no tiene rol asignado"""
        if not self.rol_id:
            self.rol = Rol.objects.get_or_create(
                nombre_rol="cliente",
                defaults={'descripcion': 'Rol por defecto para clientes'}
            )[0]
        super().save(*args, **kwargs)