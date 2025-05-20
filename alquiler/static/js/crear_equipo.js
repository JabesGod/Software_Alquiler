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

