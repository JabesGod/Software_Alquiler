from django import forms
from alquiler.models import Alquiler, Usuario, Contrato, Cliente, Equipo, DetalleAlquiler
from django.utils import timezone
from datetime import timedelta
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
import json
import pytz
from decimal import Decimal, InvalidOperation


def validate_fecha_fin(value):
    bogota_tz = pytz.timezone('America/Bogota')
    hoy_colombia = timezone.now().astimezone(bogota_tz).date()
    if value < hoy_colombia:
        raise ValidationError(f"La fecha de fin ({value}) no puede ser anterior a hoy ({hoy_colombia})")


class AlquilerForm(forms.ModelForm):
    iva = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.HiddenInput(),
        required=False,
        initial=Decimal('0.00')
    )
    precio_total = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.HiddenInput(),
        required=False,
        initial=Decimal('0.00')
    )
    forzar_alquiler = forms.BooleanField(
        required=False,
        label="Forzar alquiler (cliente moroso)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Marque solo si tiene autorización para alquilar a cliente moroso"
    )
    
    class Meta:
        model = Alquiler
        fields = [
            'cliente', 'fecha_inicio', 'fecha_fin', 'fecha_vencimiento',
            'numero_factura', 'con_iva', 'observaciones',
            'renovacion_automatica', 'contrato_firmado',
            'iva', 'precio_total', 'forzar_alquiler'
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'con_iva': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_con_iva'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'renovacion_automatica': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contrato_firmado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
        if self.instance and self.instance.pk:
            self.fields['aprobado_por'] = forms.CharField(
                initial=self.instance.aprobado_por or (
                    getattr(self.request.user, 'nombre_usuario', '') if self.request else ''
                ),
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
                required=False
            )
        
        if not self.instance.pk and self.request and self.request.user.has_perm('alquiler.approve_alquiler'):
            self.fields['aprobado_por'] = forms.CharField(
                initial=getattr(self.request.user, 'nombre_usuario', ''),
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
                required=False
            )

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        forzar = cleaned_data.get('forzar_alquiler')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise forms.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

        if not self.instance.pk and cliente:
            if cliente.moroso and not forzar:
                self.add_error('cliente', f"El cliente {cliente.nombre} está marcado como moroso.")
            if cliente.estado_verificacion != 'verificado':
                self.add_error('cliente', f"El cliente {cliente.nombre} no está verificado. Solo se permiten alquileres para clientes verificados.")

        if forzar and not (self.request and self.request.user.has_perm('alquiler.override_moroso')):
            raise forms.ValidationError("No tiene permisos para forzar alquileres a clientes morosos.")

        return cleaned_data



    def clean_iva(self):
        iva = self.cleaned_data.get('iva', '0') or '0'
        return Decimal(iva).quantize(Decimal('0.00'))

    def clean_precio_total(self):
        precio_total = self.cleaned_data.get('precio_total', '0') or '0'
        return Decimal(precio_total).quantize(Decimal('0.00'))


class DetalleAlquilerForm(forms.ModelForm):
    numeros_serie = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Números de serie en formato JSON",
        initial='[]'
    )

    class Meta:
        model = DetalleAlquiler
        fields = ['equipo', 'numeros_serie', 'periodo_alquiler', 'cantidad', 'precio_unitario', 'con_iva']
        widgets = {
            'equipo': forms.HiddenInput(),
            'periodo_alquiler': forms.HiddenInput(),
            'cantidad': forms.HiddenInput(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        try:
            precio_unitario = Decimal(str(self.cleaned_data.get('precio_unitario', '0')))
            cantidad = int(self.cleaned_data.get('cantidad', 0))
            precio_total_base = precio_unitario * cantidad
            instance.precio_total = precio_total_base.quantize(Decimal('0.01'))
        except (InvalidOperation, AttributeError, TypeError, ValueError) as e:
            print(f"[ERROR] Error al calcular precio_total: {e}")
            instance.precio_total = Decimal('0.00')

        if commit:
            instance.save()

        return instance


    def clean(self):
        cleaned_data = super().clean()
        equipo = cleaned_data.get('equipo')
        numeros_serie = cleaned_data.get('numeros_serie', '[]')
        
        try:
            numeros_serie = json.loads(numeros_serie)
        except json.JSONDecodeError:
            numeros_serie = [s.strip() for s in numeros_serie.split(',') if s.strip()]
        
        # Filtrar series vacías
        numeros_serie = [s for s in numeros_serie if s]
        cleaned_data['numeros_serie'] = numeros_serie

        if equipo and equipo.requiere_serie:
            if not numeros_serie:
                raise ValidationError("Este equipo requiere al menos un número de serie válido.")
            cleaned_data['cantidad'] = len(numeros_serie)
        else:
            cleaned_data['cantidad'] = 1  # Valor por defecto para equipos sin serie

        return cleaned_data


DetalleAlquilerFormSet = inlineformset_factory(
    Alquiler,
    DetalleAlquiler,
    form=DetalleAlquilerForm,
    extra=1,
    can_delete=True,
    can_delete_extra=True
)


class ConvertirReservaForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ['fecha_inicio', 'fecha_fin', 'observaciones']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Para validar permisos si querés
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        cliente = self.instance.cliente

        # 👉 Lógica de reserva: va a ser activado
        self.instance.es_reserva = False

        # ✅ Validaciones de fechas
        hoy = timezone.now().date()
        if fecha_inicio and fecha_fin:
            if fecha_inicio < hoy:
                raise ValidationError("La fecha de inicio no puede ser en el pasado.")
            if fecha_fin < fecha_inicio:
                raise ValidationError("La fecha de fin debe ser igual o posterior a la fecha de inicio.")

        # ✅ Validación de cliente
        if cliente:
            if cliente.moroso and not (self.request and self.request.user.has_perm('alquiler.override_moroso')):
                raise ValidationError(f"El cliente {cliente.nombre} está marcado como moroso.")
            if cliente.estado_verificacion != 'verificado':
                raise ValidationError(f"El cliente {cliente.nombre} no está verificado.")

        return cleaned_data

    def save(self, commit=True):
        alquiler = super().save(commit=False)
        
        # ✅ Estado
        alquiler.estado_alquiler = 'activo'
        alquiler.fecha_vencimiento = alquiler.fecha_fin
        alquiler.es_reserva = False

        # ✅ Asignar aprobado_por si no existe
        if not alquiler.aprobado_por and self.request:
            alquiler.aprobado_por = getattr(self.request.user, 'nombre_usuario', self.request.user.username)

        if commit:
            alquiler.save()

        return alquiler
    

class RenovarAlquilerForm(forms.Form):
    numero_factura = forms.CharField(
        label="Número de Factura",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_numero_factura(self):
        numero_factura = self.cleaned_data['numero_factura']
        if Alquiler.objects.filter(numero_factura=numero_factura).exists():
            raise ValidationError("Este número de factura ya está en uso")
        return numero_factura




class DocumentosAlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ['contrato_firmado']

class FirmarContratoForm(forms.ModelForm):
    firma_imagen = forms.ImageField(
        label="Subir firma como imagen",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    firma_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = Contrato
        fields = ['fecha_firma']
        widgets = {
            'fecha_firma': forms.DateInput(attrs={'type': 'date'})
        }
        
    def clean_firma(self):
        firma_file = self.cleaned_data.get('firma_imagen')
        firma_data = self.cleaned_data.get('firma_data')
    
        if not firma_file and not firma_data:
            raise forms.ValidationError("Debe proporcionar una firma (dibujada o subida como imagen)")
    
        if firma_file:
        # Verificar tamaño máximo de archivo (1MB)
            if firma_file.size > 1024*1024:
                raise forms.ValidationError("La imagen de firma no puede exceder 1MB")
        
        # Verificar tipo de archivo
            valid_types = ['image/jpeg', 'image/png', 'image/gif']
            if firma_file.content_type not in valid_types:
                raise forms.ValidationError("Formato de imagen no válido. Use JPEG, PNG o GIF")
    
        return self.cleaned_data

class UsuarioCreationForm(forms.ModelForm):
    contraseña1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    contraseña2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('nombre_usuario', 'rol', 'cliente')

    def clean_contraseña2(self):
        password1 = self.cleaned_data.get("contraseña1")
        password2 = self.cleaned_data.get("contraseña2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["contraseña1"])
        if commit:
            user.save()
        return user
