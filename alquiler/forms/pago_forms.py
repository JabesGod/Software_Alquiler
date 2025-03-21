from django import forms
from alquiler.models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['monto', 'metodo_pago', 'referencia_transaccion']
