from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Pago, Alquiler, Cliente


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        
        fields = [
            'alquiler', 'monto', 'metodo_pago', 'estado_pago',
            'referencia_transaccion', 'fecha_vencimiento',
            'comprobante_pago', 'notas'
        ]
        widgets = {
            'alquiler': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'estado_pago': forms.Select(attrs={'class': 'form-control'}),
            'referencia_transaccion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'comprobante_pago': forms.FileInput(attrs={'class': 'form-control'}),
        }
    

class PagoParcialForm(PagoForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['monto'].widget.attrs.update({
            'max': self.instance.alquiler.saldo_pendiente if self.instance.alquiler else ''
        })

    def clean_monto(self):
        monto = super().clean_monto()
        alquiler = self.instance.alquiler
        if alquiler and monto > alquiler.saldo_pendiente:
            raise ValidationError(f"El monto no puede ser mayor al saldo pendiente (${alquiler.saldo_pendiente})")
        return monto

class AprobarPagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['estado_pago', 'notas']


class FiltroPagosForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        required=False,
        label='Filtrar por Cliente'
    )
    estado = forms.ChoiceField(
        choices=Pago.ESTADO_PAGO,
        required=False,
        label='Filtrar por Estado'
    )
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Desde'
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Hasta'
    )