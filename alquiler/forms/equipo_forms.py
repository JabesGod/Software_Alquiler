from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from ..models import Equipo, FotoEquipo
from decimal import Decimal
from django.db.models import Q


class MultipleFileInput(widgets.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)

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
    descripcion_larga = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
        label="Descripción detallada"
    )
    
    class Meta:
        model = Equipo
        fields = [
            'sku', 'marca', 'modelo', 'numero_serie', 'requiere_serie', 'especificaciones',
            'estado', 'ubicacion', 'cantidad_total', 'cantidad_disponible',
            'precio_dia', 'precio_semana', 'precio_mes', 'precio_trimestre',
            'precio_semestre', 'precio_anio', 'descripcion_larga', 'es_html'
        ]
        widgets = {
            'numero_serie': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ingrese números de serie separados por comas\nEj: SN123, SN456, SN789'
            }),
            'sku': forms.TextInput(attrs={
                'placeholder': 'Ej: SKU-001'
            })
        }
        help_texts = {
            'numero_serie': 'Ingrese todos los números de serie separados por comas',
            'sku': 'Código único de identificación del equipo'
        }

    def clean_numero_serie(self):
        numero_serie = self.cleaned_data.get('numero_serie', '')
        if not numero_serie:
            return numero_serie
            
        numeros = [s.strip() for s in numero_serie.split(',') if s.strip()]
        
        # Verificar duplicados dentro del mismo equipo
        if len(numeros) != len(set(numeros)):
            raise ValidationError("Hay números de serie duplicados en la lista")
            
        # Verificar si alguno ya existe en otros equipos
        for num in numeros:
            if Equipo.objects.filter(
                Q(numero_serie__contains=num) & 
                ~Q(pk=self.instance.pk if self.instance else None)
            ).exists():
                raise ValidationError(f"El número de serie {num} ya está registrado en otro equipo")
        
        return ', '.join(numeros)

    def clean(self):
        cleaned_data = super().clean()
        cantidad_total = cleaned_data.get('cantidad_total', 1)
        numero_serie = cleaned_data.get('numero_serie', '')
        
        if numero_serie:
            cantidad_series = len([s for s in numero_serie.split(',') if s.strip()])
            if cantidad_series > cantidad_total:
                self.add_error(
                    'cantidad_total',
                    f'La cantidad total ({cantidad_total}) debe ser al menos igual a la cantidad de números de serie ({cantidad_series})'
                )
        
        # Validación de cantidad disponible no puede ser mayor que cantidad total
        cantidad_disponible = cleaned_data.get('cantidad_disponible', 1)
        if cantidad_disponible > cantidad_total:
            self.add_error('cantidad_disponible', 'La cantidad disponible no puede ser mayor que la cantidad total')
        
        # Cálculo de precios automáticos
        precio_dia = cleaned_data.get('precio_dia', 0)
        if precio_dia:
            if not cleaned_data.get('precio_semana'):
                cleaned_data['precio_semana'] = precio_dia * 7 * Decimal('0.9')
            if not cleaned_data.get('precio_mes'):
                cleaned_data['precio_mes'] = precio_dia * 30 * Decimal('0.8')
        
        return cleaned_data
    

class EquipoForm(EquipoBaseForm):
    fotos = MultipleFileField(
        required=False,
        label="Subir fotos del equipo",
        help_text="Seleccione una o más fotos (mínimo 1 requerido para nuevo equipo)"
    )

    seriales = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Números de serie",
        help_text="Ingrese un número de serie por línea. Cada línea crea una unidad."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fotos'].required = not bool(self.instance and self.instance.pk)

    def clean_fotos(self):
        fotos = self.files.getlist('fotos')
        for foto in fotos:
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError(f"La foto {foto.name} es demasiado grande (máximo 5MB).")
            if foto.content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                raise ValidationError(f"Tipo de archivo no soportado para {foto.name}. Use JPG, PNG, GIF o WEBP.")
        return fotos


    def save(self, commit=True):
        equipo = super().save(commit=False)

        if commit:
            equipo.save()

            # Guardar fotos
            fotos = self.cleaned_data.get('fotos', [])
            if fotos:
                es_principal = not equipo.fotos.exists()
                for i, foto in enumerate(fotos):
                    FotoEquipo.objects.create(
                        equipo=equipo,
                        foto=foto,
                        es_principal=es_principal and i == 0,
                        descripcion=f"Foto del equipo {equipo.marca} {equipo.modelo}"
                    )

        return equipo



class EquipoEditForm(EquipoBaseForm):
    # Versión para edición que no requiere fotos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar campo para nuevas fotos adicionales
        self.fields['nuevas_fotos'] = MultipleFileField(
            required=False,
            label="Subir fotos adicionales",
            help_text="Seleccione fotos adicionales (opcional)"
        )
    
    def clean_nuevas_fotos(self):
        """Validar las nuevas fotos que se están subiendo"""
        fotos = self.files.getlist('nuevas_fotos[]')  # Nota el [] en el nombre
        for foto in fotos:
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError(f"La foto {foto.name} es demasiado grande (máximo 5MB).")
            if foto.content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                raise ValidationError(f"Tipo de archivo no soportado para {foto.name}. Use JPG, PNG, GIF o WEBP.")
        return fotos
    
    def clean(self):
        cleaned_data = super().clean()
        
        # No validar fotos aquí, ya que se manejan a través del formset
        # La validación de fotos se debe hacer en la vista después de procesar el formset
        
        return cleaned_data
    
    def save(self, commit=True):
        equipo = super().save(commit=False)

        if commit:
            equipo.save()

            # Guardar nuevas fotos adicionales si las hay
            nuevas_fotos = self.files.getlist('nuevas_fotos[]')
            if nuevas_fotos:
                for i, foto in enumerate(nuevas_fotos):
                    FotoEquipo.objects.create(
                        equipo=equipo,
                        foto=foto,
                        es_principal=False,  # Las nuevas fotos no son principales por defecto
                        descripcion=f"Foto del equipo {equipo.marca} {equipo.modelo}"
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