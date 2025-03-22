from django import forms
from alquiler.models import Alquiler
from alquiler.models import Contrato

class AlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = '__all__' 

class DocumentosAlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = ['contrato_firmado']



class FirmarContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['fecha_firma']
        widgets = {
            'fecha_firma': forms.DateInput(attrs={'type': 'date'})
        }
