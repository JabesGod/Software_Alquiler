$(document).ready(function () {
    // Inicializar Select2 para los selects
    $('.select2').select2({
        placeholder: "Seleccione...",
        allowClear: true,
        width: '100%'
    });

    // Variables globales
    let equiposAgregados = [];
    let contadorEquipos = 0;

    // Calcular duración de la reserva
    function calcularDuracion() {
        const inicio = new Date($('#id_fecha_inicio').val());
        const fin = new Date($('#id_fecha_fin').val());

        if (isNaN(inicio) || isNaN(fin)) return;

        const diffTime = fin - inicio;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

        let textoDuracion = diffDays + ' día' + (diffDays !== 1 ? 's' : '');

        if (diffDays >= 7) {
            const semanas = Math.floor(diffDays / 7);
            const diasRestantes = diffDays % 7;

            textoDuracion = semanas + ' semana' + (semanas !== 1 ? 's' : '');
            if (diasRestantes > 0) {
                textoDuracion += ' y ' + diasRestantes + ' día' + (diasRestantes !== 1 ? 's' : '');
            }
        }

        $('#duracion-reserva').val(textoDuracion);
    }

    $('#id_fecha_inicio, #id_fecha_fin').change(calcularDuracion);
    calcularDuracion();

    // Manejar cambio de equipo para cargar números de serie
    // Manejar cambio de equipo para cargar números de serie
    $('#equipo-selector').change(function () {
        const equipoId = $(this).val();
        const serieSelector = $('#serie-selector');

        if (!equipoId) {
            serieSelector.empty().prop('disabled', true);
            return;
        }

        // Usar la URL definida globalmente
        $.ajax({
            url: window.SERIES_DISPONIBLES_URL.replace('{equipoId}', equipoId),
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                serieSelector.empty();
                data.series.forEach(value => {
                    serieSelector.append($('<option>', {
                        value: value,
                        text: value
                    }));
                });

                // Filtrar series ya seleccionadas para este equipo
                const yaSeleccionadas = equiposAgregados
                    .filter(e => e.equipoId == equipoId)
                    .flatMap(e => e.series);

                if (yaSeleccionadas.length > 0) {
                    serieSelector.val(yaSeleccionadas).trigger('change');
                }

                serieSelector.prop('disabled', false);
            },
            error: function (xhr, status, error) {
                console.error("Error al cargar series:", error);
                serieSelector.empty().prop('disabled', true);
            }
        });
    });

    // Inicializar Select2 para el selector de series
    $('#serie-selector').select2({
        placeholder: "Seleccione series...",
        allowClear: true,
        width: '100%',
        closeOnSelect: false
    }).prop('disabled', true);

    // Inicializar Select2 para el selector de periodo
    $('#periodo-selector').select2({
        placeholder: "Seleccione periodo...",
        allowClear: false,
        width: '100%'
    });

    // Agregar equipo a la tabla
    $('#agregar-equipo').click(function () {
        const equipoId = $('#equipo-selector').val();
        const equipoTexto = $('#equipo-selector option:selected').text().split('(')[0].trim();
        const series = $('#serie-selector').val() || [];
        const periodo = $('#periodo-selector').val();
        const periodoTexto = $('#periodo-selector option:selected').text();

        if (!equipoId) {
            alert('Por favor seleccione un equipo');
            return;
        }

        if (series.length === 0) {
            alert('Por favor seleccione al menos un número de serie');
            return;
        }

        if (!periodo) {
            alert('Por favor seleccione un periodo de reserva');
            return;
        }

        // Obtener precios del equipo
        const selectedOption = $('#equipo-selector option:selected');
        const precios = {
            dia: parseFloat(selectedOption.data('precio-dia')) || 0,
            semana: parseFloat(selectedOption.data('precio-semana')) || 0,
            mes: parseFloat(selectedOption.data('precio-mes')) || 0,
            trimestre: parseFloat(selectedOption.data('precio-trimestre')) || 0,
            semestre: parseFloat(selectedOption.data('precio-semestre')) || 0,
            anio: parseFloat(selectedOption.data('precio-anio')) || 0
        };

        const precioUnitario = precios[periodo] || 0;

        // Verificar si ya existe este equipo con el mismo periodo
        const indexExistente = equiposAgregados.findIndex(e =>
            e.equipoId == equipoId && e.periodo == periodo
        );

        if (indexExistente >= 0) {
            // Verificar si hay series duplicadas
            const seriesDuplicadas = series.filter(serie =>
                equiposAgregados[indexExistente].series.includes(serie)
            );

            if (seriesDuplicadas.length > 0) {
                alert(`Las siguientes series ya están agregadas: ${seriesDuplicadas.join(', ')}`);
                return;
            }

            // Actualizar series existentes
            equiposAgregados[indexExistente].series = [
                ...new Set([...equiposAgregados[indexExistente].series, ...series])
            ];
        } else {
            // Agregar nuevo equipo
            equiposAgregados.push({
                id: contadorEquipos++,
                equipoId: equipoId,
                equipoTexto: equipoTexto,
                series: series,
                periodo: periodo,
                periodoTexto: periodoTexto,
                precioUnitario: precioUnitario
            });
        }

        actualizarTablaEquipos();
        actualizarInputsOcultos();

        // Limpiar selección de series
        $('#serie-selector').val(null).trigger('change');
    });

    // Actualizar la tabla de equipos
    function actualizarTablaEquipos() {
        const tbody = $('#tabla-equipos tbody');
        tbody.empty();

        if (equiposAgregados.length === 0) {
            tbody.append(
                $('<tr>').append(
                    $('<td>').attr('colspan', 5).text('No hay equipos agregados')
                )
            );
            return;
        }

        equiposAgregados.forEach(equipo => {
            const row = $('<tr>').attr('data-id', equipo.id);

            row.append($('<td>').text(equipo.equipoTexto));
            row.append($('<td>').text(equipo.series.join(', ')));
            row.append($('<td>').text(equipo.periodoTexto));
            row.append($('<td>').addClass('text-end').text('$' + equipo.precioUnitario.toFixed(2)));

            const deleteBtn = $('<button>').addClass('btn btn-danger btn-sm')
                .html('<i class="fas fa-trash"></i>')
                .click(function () {
                    eliminarEquipo(equipo.id);
                });

            row.append($('<td>').addClass('text-center').append(deleteBtn));

            tbody.append(row);
        });
    }

    // Eliminar equipo de la lista
    function eliminarEquipo(id) {
        equiposAgregados = equiposAgregados.filter(e => e.id !== id);
        actualizarTablaEquipos();
        actualizarInputsOcultos();
    }

    // Actualizar los inputs ocultos para el formulario
    function actualizarInputsOcultos() {
        const container = $('#equipos-container');
        container.empty();

        equiposAgregados.forEach((equipo, index) => {
            // Input para el equipo
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-equipo`,
                    value: equipo.equipoId
                })
            );

            // Input para los números de serie (como lista JSON)
            container.append(
                $('<input>', {
                    type: 'hidden',
                    name: `detalles-${index}-numeros_serie`,
                    value: JSON.stringify(equipo.series)  // ✅ esto sí debe funcionar si el campo es JSONField
                })
            );


            // Input para el periodo
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-periodo_alquiler`,
                    value: equipo.periodo
                })
            );

            // Input para la cantidad
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-cantidad`,
                    value: equipo.series.length
                })
            );

            // Input para el ID (si es una edición)
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-id`,
                    value: ''
                })
            );

            // Input para DELETE si es necesario
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-DELETE`,
                    value: 'false'
                })
            );
        });

        // Actualizar el TOTAL_FORMS
        $('#id_detalles-TOTAL_FORMS').val(equiposAgregados.length);
    }

    // Validación del formulario
    (function () {
        'use strict';

        // Fetch all the forms we want to apply custom Bootstrap validation styles to
        var forms = document.querySelectorAll('.needs-validation');

        // Loop over them and prevent submission
        Array.prototype.slice.call(forms)
            .forEach(function (form) {
                form.addEventListener('submit', function (event) {
                    if (equiposAgregados.length === 0) {
                        event.preventDefault();
                        event.stopPropagation();
                        alert('Debe agregar al menos un equipo a la reserva');
                        return;
                    }

                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }

                    form.classList.add('was-validated');
                }, false);
            });
    })();

    // Inicializar la tabla de equipos
    actualizarTablaEquipos();
});