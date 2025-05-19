# alquiler/forms/usuario_forms.py
from django import forms
from django.contrib.auth.password_validation import validate_password
from ..models import Usuario

class RegistroForm(forms.Form):
    nombre_usuario = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': ' '})
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': ' '}),
        required=True
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': ' '}),
        required=True
    )

    def clean_nombre_usuario(self):
        nombre = self.cleaned_data.get('nombre_usuario')
        if Usuario.objects.filter(nombre_usuario=nombre).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso")
        return nombre

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        validate_password(password1)
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden")

        return cleaned_data