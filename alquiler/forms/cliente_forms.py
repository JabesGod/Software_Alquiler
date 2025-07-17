from django import forms
from alquiler.models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ['moroso', 'fecha_marcado_moroso', 'dias_mora', 'deuda_total']
        # También podrías usar fields = '__all__' y luego excluir en el widgets o clean

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_cliente')
        if tipo == 'juridica':
            if not cleaned_data.get('nombre_empresa'):
                self.add_error('nombre_empresa', 'Este campo es obligatorio para clientes jurídicos.')
            if not cleaned_data.get('nit'):
                self.add_error('nit', 'Este campo es obligatorio para clientes jurídicos.')
        return cleaned_data