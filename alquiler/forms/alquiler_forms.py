from django import forms
from alquiler.models import Alquiler, Usuario, Contrato, Cliente, Equipo, DetalleAlquiler
from django.utils import timezone
from datetime import timedelta
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
import json
import pytz


def validate_fecha_fin(value):
    bogota_tz = pytz.timezone('America/Bogota')
    hoy_colombia = timezone.now().astimezone(bogota_tz).date()
    if value < hoy_colombia:
        raise ValidationError(f"La fecha de fin ({value}) no puede ser anterior a hoy ({hoy_colombia})")


class AlquilerForm(forms.ModelForm):
    cliente = forms.ModelChoiceField( queryset=Cliente.objects.all(),widget=forms.Select(attrs={'class': 'select2'}), required=True
    )
    
    fecha_inicio = forms.DateField( widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), initial=timezone.now().date()
    )
    
    fecha_fin = forms.DateField( widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), initial=(timezone.now() + timedelta(days=7)).date(), validators=[validate_fecha_fin]
    )
    
    numero_factura = forms.CharField( required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), help_text="Requerido para alquileres activos"
    )
    
    class Meta:
        model = Alquiler
        fields = [
            'cliente', 'fecha_inicio', 'fecha_fin', 'numero_factura',
            'observaciones', 'aprobado_por', 'contrato_firmado', 'renovacion',
            'fecha_vencimiento'
        ]
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_vencimiento'].initial = self.fields['fecha_fin'].initial
        self.fields['renovacion'].initial = False
        self.fields['renovacion'].widget.attrs.update({'class': 'form-check-input'})
        
        if getattr(self.instance, 'es_reserva', False):
            self.fields['numero_factura'].widget = forms.HiddenInput()
            self.fields['numero_factura'].required = False

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        es_reserva = getattr(self.instance, 'es_reserva', False)
        es_renovacion = cleaned_data.get('renovacion', False)

        # Obtener la fecha actual en la zona horaria de Colombia
        bogota_tz = pytz.timezone('America/Bogota')
        hoy_colombia = timezone.now().astimezone(bogota_tz).date()

        # Validación de número de factura
        if not es_reserva and not cleaned_data.get('numero_factura'):
            self.add_error('numero_factura', "Debe ingresar un número de factura para alquileres activos.")

        # Validación de fechas
        if fecha_inicio and fecha_fin:
            # Validación específica para renovaciones
            if es_renovacion and fecha_inicio < hoy_colombia:
                self.add_error('fecha_inicio', "La fecha de inicio no puede ser en el pasado para renovaciones.")
            
            # Validación general para todos los casos excepto reservas
            elif not es_reserva and fecha_inicio < hoy_colombia:
                self.add_error('fecha_inicio', f"La fecha de inicio ({fecha_inicio}) no puede ser anterior a hoy ({hoy_colombia}) para nuevos alquileres.")
            
            if fecha_fin <= fecha_inicio:
                self.add_error('fecha_fin', "La fecha de fin debe ser posterior a la fecha de inicio.")

        return cleaned_data


class DetalleAlquilerForm(forms.ModelForm):
    numeros_serie = forms.CharField( required=True, widget=forms.HiddenInput(), help_text="Números de serie en formato JSON"
    )
    precio_unitario = forms.DecimalField( required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}), decimal_places=2, max_digits=10
    )
    class Meta:
        model = DetalleAlquiler
        fields = ['equipo', 'numeros_serie', 'periodo_alquiler', 'cantidad']
        widgets = {
            'equipo': forms.HiddenInput(),
            'periodo_alquiler': forms.HiddenInput(),
            'cantidad': forms.HiddenInput(),
        }

    def clean_numeros_serie(self):
        numeros_serie = self.cleaned_data.get('numeros_serie', '[]')
        
        try:
            # Convertir de JSON string a lista Python
            if isinstance(numeros_serie, str):
                return json.loads(numeros_serie)
            return numeros_serie
        except json.JSONDecodeError:
            raise forms.ValidationError("Formato inválido para números de serie")

    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('precio_unitario'):
            periodo = cleaned_data.get('periodo_alquiler')
            equipo = cleaned_data.get('equipo')
            if equipo and periodo:
                # Establecer precio basado en periodo
                cleaned_data['precio_unitario'] = getattr(equipo, f'precio_{periodo}', 0)
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
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # ✅ Forzar reserva antes de que el modelo la valide
        self.instance.es_reserva = True

        if fecha_inicio and fecha_fin:
            if fecha_inicio < timezone.now().date():
                raise ValidationError("La fecha de inicio no puede ser en el pasado.")
            if fecha_fin <= fecha_inicio:
                raise ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        return cleaned_data


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
