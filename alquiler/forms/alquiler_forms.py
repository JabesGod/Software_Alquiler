from django import forms
from alquiler.models import Alquiler

class AlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = '__all__' 

class DocumentosAlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ['contrato_firmado']