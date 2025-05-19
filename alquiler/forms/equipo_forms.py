from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from ..models import Equipo, FotoEquipo

# Widget personalizado para múltiples archivos
class MultipleFileInput(widgets.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file'
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class FotoEquipoForm(forms.ModelForm):
    class Meta:
        model = FotoEquipo
        fields = ['foto', 'es_principal', 'descripcion']
        widgets = {
            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Descripción breve de la foto...',
                'class': 'form-control'
            }),
            'es_principal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foto'].required = False
        self.fields['foto'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'image/*'
        })

class EquipoBaseForm(forms.ModelForm):
    # Configuración común para ambos formularios
    descripcion_larga = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control',
            'placeholder': 'Ingrese una descripción detallada del equipo...'
        }),
        required=False,
        label="Descripción detallada"
    )
    
    class Meta:
        model = Equipo
        fields = [
            'marca', 'modelo', 'numero_serie', 'especificaciones',
            'estado', 'ubicacion', 'descripcion_larga', 'es_html'
        ]
        widgets = {
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Dell, HP, Lenovo...'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Latitude E7450, ProBook 450 G7...'
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie único del equipo'
            }),
            'especificaciones': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Especificaciones técnicas del equipo...'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ubicación física del equipo'
            }),
            'es_html': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'es_html': mark_safe('Marcar si la descripción contiene formato HTML. <small class="text-muted">Use con cuidado.</small>'),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('es_html') and not cleaned_data.get('descripcion_larga'):
            self.add_error('descripcion_larga', 'Debe proporcionar una descripción cuando selecciona formato HTML')
        return cleaned_data

class EquipoForm(EquipoBaseForm):
    # Campo para subir múltiples fotos usando nuestro Field personalizado
    fotos = MultipleFileField(
        required=False,
        label="Subir fotos del equipo",
        help_text="Seleccione una o más fotos (mínimo 1 requerido para nuevo equipo)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['fotos'].required = False
            self.fields['fotos'].help_text = "Subir fotos adicionales (opcional)"
        else:
            self.fields['fotos'].required = True
    
    def clean_fotos(self):
        fotos = self.files.getlist('fotos')
        
        if not self.instance.pk and not fotos:
            raise ValidationError("Debe subir al menos una foto del equipo.")
        
        for foto in fotos:
            if foto.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError(f"La foto {foto.name} es demasiado grande (máximo 5MB)")
            
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if foto.content_type not in valid_types:
                raise ValidationError(f"Tipo de archivo no soportado para {foto.name}. Use JPG, PNG o GIF.")
        
        return fotos
    
    def save(self, commit=True):
        equipo = super().save(commit=commit)
        
        fotos_subidas = self.cleaned_data.get('fotos', [])
        if fotos_subidas:
            es_principal = not equipo.fotos.exists()
            
            for i, foto in enumerate(fotos_subidas):
                FotoEquipo.objects.create(
                    equipo=equipo,
                    foto=foto,
                    es_principal=es_principal and (i == 0),
                    descripcion=f"Foto del equipo {equipo.marca} {equipo.modelo}"
                )
        
        return equipo

class EquipoEditForm(EquipoBaseForm):
    # Versión para edición que no requiere fotos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fotos'] = MultipleFileField(
            required=False,
            label="Subir fotos adicionales",
            help_text="Seleccione fotos adicionales (opcional)"
        )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que haya al menos una foto (existente o nueva)
        fotos_subidas = self.files.getlist('fotos')
        if not self.instance.fotos.exists() and not fotos_subidas:
            raise ValidationError("El equipo debe tener al menos una foto.")
        
        return cleaned_data
    
    def save(self, commit=True):
        equipo = super().save(commit=commit)
        
        fotos_subidas = self.files.getlist('fotos')
        if fotos_subidas:
            # Al editar, las nuevas fotos no serán principales
            for foto in fotos_subidas:
                FotoEquipo.objects.create(
                    equipo=equipo,
                    foto=foto,
                    es_principal=False,
                    descripcion=f"Foto adicional del equipo {equipo.marca} {equipo.modelo}"
                )
        
        return equipo

# Formset para manejar fotos existentes
FotoEquipoFormSet = forms.inlineformset_factory(
    Equipo,
    FotoEquipo,
    form=FotoEquipoForm,
    extra=1,
    can_delete=True,
    fields=['foto', 'es_principal', 'descripcion']
)