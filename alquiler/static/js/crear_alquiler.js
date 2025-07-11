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

    // Calcular duración del alquiler
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

        $('#duracion-alquiler').val(textoDuracion);
        actualizarResumenCostos();
    }

    $('#id_fecha_inicio, #id_fecha_fin').change(calcularDuracion);
    calcularDuracion();

    // Manejar cambio de equipo para cargar números de serie
    $('#equipo-selector').change(function () {
        const equipoId = $(this).val();
        const serieSelector = $('#serie-selector');

        if (equipoId) {
            $.ajax({
                url: '/equipos/' + equipoId + '/series-disponibles/',
                success: function (data) {
                    serieSelector.empty();
                    $.each(data.series, function (index, value) {
                        serieSelector.append($('<option>', {
                            value: value,
                            text: value
                        }));
                    });

                    // Verificar si hay series ya seleccionadas para este equipo
                    const seriesYaSeleccionadas = equiposAgregados
                        .filter(e => e.equipoId == equipoId)
                        .flatMap(e => e.series);

                    if (seriesYaSeleccionadas.length > 0) {
                        serieSelector.val(seriesYaSeleccionadas).trigger('change');
                    }

                    // Habilitar el select de series
                    serieSelector.prop('disabled', false);
                },
                error: function (xhr, status, error) {
                    console.error("Error al cargar series:", error);
                    serieSelector.empty().prop('disabled', true);
                }
            });
        } else {
            serieSelector.empty().prop('disabled', true);
        }
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
            alert('Por favor seleccione un periodo de alquiler');
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
        actualizarResumenCostos();

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
                    $('<td>').attr('colspan', 6).text('No hay equipos agregados')
                )
            );
            return;
        }

        equiposAgregados.forEach(equipo => {
            const row = $('<tr>').attr('data-id', equipo.id);

            row.append($('<td>').text(equipo.equipoTexto));
            row.append($('<td>').text(equipo.series.join(', ')));
            row.append($('<td>').text(equipo.periodoTexto));

            // Celda de precio unitario editable
            const precioInput = $('<input>').attr({
                type: 'number',
                class: 'form-control precio-unitario',
                value: equipo.precioUnitario.toFixed(2),
                'data-id': equipo.id,
                step: '0.01',
                min: '0',
                style: 'width: 100px;'
            });
            row.append($('<td>').addClass('text-end').append(precioInput));

            // Celda de precio total (calculado)
            row.append($('<td>').addClass('text-end precio-total').attr('data-id', equipo.id)
                .text('$' + (equipo.precioUnitario * equipo.series.length).toFixed(2)));

            const deleteBtn = $('<button>').addClass('btn btn-danger btn-sm')
                .html('<i class="fas fa-trash"></i>')
                .click(function () {
                    eliminarEquipo(equipo.id);
                });

            row.append($('<td>').addClass('text-center').append(deleteBtn));

            tbody.append(row);
        });

        // Agregar manejador de eventos para cambios en precios
        $('.precio-unitario').change(function() {
            const id = $(this).data('id');
            const nuevoPrecio = parseFloat($(this).val()) || 0;

            // Actualizar el precio en el array
            const equipoIndex = equiposAgregados.findIndex(e => e.id == id);
            if (equipoIndex >= 0) {
                equiposAgregados[equipoIndex].precioUnitario = nuevoPrecio;

                // Actualizar el precio total
                const cantidad = equiposAgregados[equipoIndex].series.length;
                $(`.precio-total[data-id="${id}"]`).text('$' + (nuevoPrecio * cantidad).toFixed(2));

                actualizarResumenCostos();
                actualizarInputsOcultos();
            }
        });
    }

    // Eliminar equipo de la lista
    function eliminarEquipo(id) {
        equiposAgregados = equiposAgregados.filter(e => e.id !== id);
        actualizarTablaEquipos();
        actualizarInputsOcultos();
        actualizarResumenCostos();
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
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-numeros_serie`,
                    value: JSON.stringify(equipo.series)
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

            // Input para el precio unitario
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-precio_unitario`,
                    value: equipo.precioUnitario
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

    // Actualizar el resumen de costos
    function actualizarResumenCostos() {
        const duracionText = $('#duracion-alquiler').val();
        const duracionMatch = duracionText.match(/\d+/);
        const duracion = duracionMatch ? parseInt(duracionMatch[0]) : 1;

        let subtotal = 0;
        $('#resumen-costos').empty();

        if (equiposAgregados.length === 0) {
            $('#resumen-costos').append(
                $('<li>').addClass('list-group-item').text('No hay equipos agregados')
            );
        }

        equiposAgregados.forEach(equipo => {
            let precioTotal = 0;
            let descripcionPeriodo = '';

            if (equipo.periodo === 'dia') {
                precioTotal = equipo.precioUnitario * equipo.series.length * duracion;
                descripcionPeriodo = `${duracion} día${duracion !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'semana') {
                const semanas = Math.ceil(duracion / 7);
                precioTotal = equipo.precioUnitario * equipo.series.length * semanas;
                descripcionPeriodo = `${semanas} semana${semanas !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'mes') {
                const meses = Math.ceil(duracion / 30);
                precioTotal = equipo.precioUnitario * equipo.series.length * meses;
                descripcionPeriodo = `${meses} mes${meses !== 1 ? 'es' : ''}`;
            } else if (equipo.periodo === 'trimestre') {
                const trimestres = Math.ceil(duracion / 90);
                precioTotal = equipo.precioUnitario * equipo.series.length * trimestres;
                descripcionPeriodo = `${trimestres} trimestre${trimestres !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'semestre') {
                const semestres = Math.ceil(duracion / 180);
                precioTotal = equipo.precioUnitario * equipo.series.length * semestres;
                descripcionPeriodo = `${semestres} semestre${semestres !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'anio') {
                const anios = Math.ceil(duracion / 365);
                precioTotal = equipo.precioUnitario * equipo.series.length * anios;
                descripcionPeriodo = `${anios} año${anios !== 1 ? 's' : ''}`;
            }

            subtotal += precioTotal;

            $('#resumen-costos').append(`
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    ${equipo.series.length} x ${equipo.equipoTexto} (${descripcionPeriodo})
                    <span class="badge bg-primary rounded-pill">$${precioTotal.toFixed(2)}</span>
                </li>
            `);
        });

        const impuestos = subtotal * 0.19; // 19% de IVA
        const total = subtotal + impuestos;

        $('#subtotal').text('$' + subtotal.toFixed(2));
        $('#impuestos').text('$' + impuestos.toFixed(2));
        $('#total').text('$' + total.toFixed(2));
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
                        alert('Debe agregar al menos un equipo al alquiler');
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
    actualizarResumenCostos();
});