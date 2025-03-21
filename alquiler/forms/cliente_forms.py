from django import forms
from alquiler.models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'  # Usa todos los campos del modelo
