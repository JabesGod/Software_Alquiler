from django import forms
from alquiler.models import Equipo

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'
