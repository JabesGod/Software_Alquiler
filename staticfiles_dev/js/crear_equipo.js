// Funcionalidad adicional para el formulario de equipos

$(document).ready(function() {
    // Validación de cantidad disponible
    $('#id_cantidad_total, #id_cantidad_disponible').change(function() {
        const total = parseInt($('#id_cantidad_total').val()) || 0;
        const disponible = parseInt($('#id_cantidad_disponible').val()) || 0;
        
        if (disponible > total) {
            alert('La cantidad disponible no puede ser mayor que la cantidad total');
            $('#id_cantidad_disponible').val(total);
        }
    });

    // Auto-completar ubicación si está vacío
    $('#id_ubicacion').blur(function() {
        if (!$(this).val()) {
            $(this).val('Almacén Principal');
        }
    });

    // Mostrar/ocultar ayuda para campos de precio
    $('.precio-help').tooltip({
        trigger: 'hover focus',
        placement: 'right'
    });

    // Validar que al menos una foto esté marcada como principal
    $('form').submit(function(e) {
        const hasPrincipal = $('input[name$="-es_principal"]:checked').length > 0;
        const hasPhotos = $('.foto-card').length > 0 || $('#id_fotos')[0].files.length > 0;
        
        if (!hasPrincipal && hasPhotos) {
            e.preventDefault();
            alert('Debe seleccionar al menos una foto como principal');
        }
    });

    // Mostrar calculadora de precios
    $('#show-price-calculator').click(function(e) {
        e.preventDefault();
        $('#price-calculator').toggleClass('d-none');
    });
});

// Función para calcular precios basados en días
function calculatePrices() {
    const dailyPrice = parseFloat($('#id_precio_dia').val()) || 0;
    const days = parseInt($('#calculation-days').val()) || 1;
    
    if (dailyPrice > 0 && days > 0) {
        $('#calculated-price').text((dailyPrice * days).toFixed(2));
    }
}




document.addEventListener('DOMContentLoaded', function() {
    const principalRadios = document.querySelectorAll('input[name$="-es_principal"]');
    
    principalRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                principalRadios.forEach(r => {
                    if (r !== this) r.checked = false;
                });
            }
        });
    });
    
    // Mostrar vista previa de las fotos seleccionadas
    const fotoInput = document.getElementById('id_fotos');
    if (fotoInput) {
        fotoInput.addEventListener('change', function(e) {
            const files = e.target.files;
            const previewContainer = document.createElement('div');
            previewContainer.className = 'row mt-3';
            
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (!file.type.match('image.*')) continue;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const col = document.createElement('div');
                    col.className = 'col-md-3 mb-3';
                    
                    const card = document.createElement('div');
                    card.className = 'card';
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'card-img-top';
                    img.style.maxHeight = '150px';
                    img.style.objectFit = 'cover';
                    
                    const cardBody = document.createElement('div');
                    cardBody.className = 'card-body p-2';
                    
                    const fileName = document.createElement('small');
                    fileName.className = 'text-muted';
                    fileName.textContent = file.name;
                    
                    cardBody.appendChild(fileName);
                    card.appendChild(img);
                    card.appendChild(cardBody);
                    col.appendChild(card);
                    previewContainer.appendChild(col);
                };
                reader.readAsDataURL(file);
            }
            
            const existingPreview = document.getElementById('fotos-preview');
            if (existingPreview) {
                existingPreview.replaceWith(previewContainer);
            } else {
                fotoInput.after(previewContainer);
            }
            previewContainer.id = 'fotos-preview';
        });
    }

    // Auto-calcular precios para periodos más largos si están vacíos
    const precioDiaInput = document.getElementById('id_precio_dia');
    if (precioDiaInput) {
        precioDiaInput.addEventListener('change', function() {
            const precioDia = parseFloat(this.value) || 0;
            
            // Solo calcular si los campos están vacíos
            if (!document.getElementById('id_precio_semana').value) {
                document.getElementById('id_precio_semana').value = (precioDia * 7 * 0.9).toFixed(2);
            }
            
            if (!document.getElementById('id_precio_mes').value) {
                document.getElementById('id_precio_mes').value = (precioDia * 30 * 0.8).toFixed(2);
            }
            
            if (!document.getElementById('id_precio_trimestre').value) {
                document.getElementById('id_precio_trimestre').value = (precioDia * 90 * 0.75).toFixed(2);
            }
            
            if (!document.getElementById('id_precio_semestre').value) {
                document.getElementById('id_precio_semestre').value = (precioDia * 180 * 0.7).toFixed(2);
            }
            
            if (!document.getElementById('id_precio_anio').value) {
                document.getElementById('id_precio_anio').value = (precioDia * 365 * 0.65).toFixed(2);
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', function () {
        const formsetDiv = document.getElementById('serial-formset');
        const addBtn = document.getElementById('add-serial');
        const totalForms = document.querySelector('[name="serialequipo_set-TOTAL_FORMS"]');

        addBtn.addEventListener('click', () => {
            const currentForms = parseInt(totalForms.value);
            const newFormHtml = formsetDiv.querySelector('.serial-entry').outerHTML.replaceAll(`-${currentForms - 1}-`, `-${currentForms}-`).replaceAll(`_${currentForms - 1}`, `_${currentForms}`);
            formsetDiv.insertAdjacentHTML('beforeend', newFormHtml);
            totalForms.value = currentForms + 1;
        });
    });