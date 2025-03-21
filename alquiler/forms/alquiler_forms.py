from django import forms
from alquiler.models import Alquiler

class AlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = '__all__' 
