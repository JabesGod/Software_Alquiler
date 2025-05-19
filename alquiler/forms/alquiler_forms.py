from django import forms
from alquiler.models import Alquiler, Usuario, Contrato

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
