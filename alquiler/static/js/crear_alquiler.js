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
        const equipoOption = $('#equipo-selector option:selected');
        const requiereSerie = equipoOption.data('requiere-serie') === 'True';

        serieSelector.empty().prop('disabled', true);
        $('#sinSerieHelp').hide();

        if (!equipoId) return;

        // Mostrar mensaje especial para equipos sin serie
        if (!requiereSerie) {
            $('#sinSerieHelp').show();
            serieSelector.append($('<option>', {
                value: '',
                text: 'Este equipo no requiere número de serie',
                selected: true,
                disabled: true
            }));
            return;
        }

        // Cargar series disponibles para equipos que las requieren
        const url = window.SERIES_DISPONIBLES_URL.replace('{equipoId}', equipoId);

        $.ajax({
            url: url,
            success: function (data) {
                serieSelector.empty();

                if (data.series.length === 0) {
                    serieSelector.append($('<option>', {
                        value: '',
                        text: 'No hay series disponibles para este equipo',
                        disabled: true
                    }));
                    return;
                }

                $.each(data.series, function (index, value) {
                    serieSelector.append($('<option>', {
                        value: value,
                        text: value
                    }));
                });

                serieSelector.prop('disabled', false);
            },
            error: function (xhr, status, error) {
                console.error("Error al cargar series:", error);
                serieSelector.empty().append($('<option>', {
                    value: '',
                    text: 'Error al cargar series',
                    disabled: true
                }));
            }
        });
    });

    // Inicializar Select2 para el selector de series
    $('#serie-selector').select2({
        placeholder: "Seleccione series...",
        allowClear: true,
        width: '100%',
        closeOnSelect: false,
        language: {
            noResults: function () {
                return "Este equipo no requiere número de serie";
            }
        }
    }).prop('disabled', true);

    // Inicializar Select2 para el selector de periodo
    $('#periodo-selector').select2({
        placeholder: "Seleccione periodo...",
        allowClear: false,
        width: '100%'
    });

    // Agregar equipo a la tabla
    // Agregar equipo a la tabla
    $('#agregar-equipo').click(function () {
        const equipoId = $('#equipo-selector').val();
        const equipoOption = $('#equipo-selector option:selected');
        const equipoTexto = equipoOption.text().split('(')[0].trim();
        const series = $('#serie-selector').val() || [];
        const periodo = $('#periodo-selector').val();
        const periodoTexto = $('#periodo-selector option:selected').text();
        const requiereSerie = equipoOption.data('requiere-serie') === 'True';

        // Validaciones básicas
        if (!equipoId) {
            alert('Por favor seleccione un equipo');
            return;
        }

        // Solo validar series si el equipo las requiere
        if (requiereSerie && series.length === 0) {
            alert('Por favor seleccione al menos un número de serie');
            return; // Aquí se mantiene la validación si el equipo requiere serie
        }

        // Obtener precios del equipo
        const precios = {
            dia: parseFloat(equipoOption.data('precio-dia')) || 0,
            semana: parseFloat(equipoOption.data('precio-semana')) || 0,
            mes: parseFloat(equipoOption.data('precio-mes')) || 0,
            trimestre: parseFloat(equipoOption.data('precio-trimestre')) || 0,
            semestre: parseFloat(equipoOption.data('precio-semestre')) || 0,
            anio: parseFloat(equipoOption.data('precio-anio')) || 0
        };

        const precioUnitario = precios[periodo] || 0;

        // Agregar nuevo equipo (sin verificar duplicados para equipos sin serie)
        equiposAgregados.push({
            id: contadorEquipos++,
            equipoId: equipoId,
            equipoTexto: equipoTexto,
            series: series,
            periodo: periodo,
            periodoTexto: periodoTexto,
            precioUnitario: precioUnitario,
            conIva: true,
            requiereSerie: requiereSerie
        });

        actualizarTablaEquipos();
        actualizarInputsOcultos();
        actualizarResumenCostos();

        // Limpiar selección
        $('#equipo-selector').val('').trigger('change');
        $('#serie-selector').val(null).trigger('change');
    });


    // Actualizar la tabla de equipos
    function actualizarTablaEquipos() {
        const tbody = $('#tabla-equipos tbody');
        tbody.empty();

        if (equiposAgregados.length === 0) {
            tbody.append(
                $('<tr>').append(
                    $('<td>').attr('colspan', 7).text('No hay equipos agregados')
                )
            );
            return;
        }

        equiposAgregados.forEach(equipo => {
            const row = $('<tr>').attr('data-id', equipo.id);

            row.append($('<td>').text(equipo.equipoTexto));

            // Celda de series (mostrar solo si hay o si el equipo las requiere)
            const seriesText = equipo.requiereSerie ?
                (equipo.series.length > 0 ? equipo.series.join(', ') : 'Sin serie') :
                'No aplica';
            row.append($('<td>').text(seriesText));

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
            const cantidad = equipo.requiereSerie ? equipo.series.length : 1;
            row.append($('<td>').addClass('text-end precio-total').attr('data-id', equipo.id)
                .text('$' + (equipo.precioUnitario * cantidad).toFixed(2)));

            // Celda de switch para IVA
            const ivaSwitch = $('<div>').addClass('form-check form-switch').append(
                $('<input>').attr({
                    type: 'checkbox',
                    class: 'form-check-input iva-checkbox',
                    id: `iva-${equipo.id}`,
                    'data-id': equipo.id,
                    checked: equipo.conIva !== false
                }),
                $('<label>').attr('for', `iva-${equipo.id}`).addClass('form-check-label').text('IVA')
            );
            row.append($('<td>').addClass('text-center').append(ivaSwitch));

            // Botón de eliminar
            const deleteBtn = $('<button>').addClass('btn btn-danger btn-sm')
                .html('<i class="fas fa-trash"></i>')
                .click(function () {
                    eliminarEquipo(equipo.id);
                });

            row.append($('<td>').addClass('text-center').append(deleteBtn));

            tbody.append(row);
        });

        // Agregar manejador de eventos para cambios en precios
        $('.precio-unitario').change(function () {
            const id = $(this).data('id');
            const nuevoPrecio = parseFloat($(this).val()) || 0;

            const equipoIndex = equiposAgregados.findIndex(e => e.id == id);
            if (equipoIndex >= 0) {
                equiposAgregados[equipoIndex].precioUnitario = nuevoPrecio;
                const cantidad = equiposAgregados[equipoIndex].requiereSerie ?
                    equiposAgregados[equipoIndex].series.length : 1;
                $(`.precio-total[data-id="${id}"]`).text('$' + (nuevoPrecio * cantidad).toFixed(2));
                actualizarResumenCostos();
                actualizarInputsOcultos();
            }
        });

        // Agregar manejador de eventos para cambios en IVA
        $('.iva-checkbox').change(function () {
            const id = $(this).data('id');
            const conIva = $(this).is(':checked');

            const equipoIndex = equiposAgregados.findIndex(e => e.id == id);
            if (equipoIndex >= 0) {
                equiposAgregados[equipoIndex].conIva = conIva;
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

            // Input para la cantidad (1 si no requiere serie)
            const cantidad = equipo.requiereSerie ? equipo.series.length : 1;
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-cantidad`,
                    value: cantidad
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

            // Input para con_iva
            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: `detalles-${index}-con_iva`,
                    value: equipo.conIva ? 'on' : ''
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
        let impuestos = 0;
        $('#resumen-costos').empty();

        if (equiposAgregados.length === 0) {
            $('#resumen-costos').append(
                $('<li>').addClass('list-group-item').text('No hay equipos agregados')
            );
        }

        equiposAgregados.forEach(equipo => {
            let precioTotal = 0;
            let descripcionPeriodo = '';
            const cantidad = equipo.requiereSerie ? equipo.series.length : 1;

            if (equipo.periodo === 'dia') {
                precioTotal = equipo.precioUnitario * cantidad * duracion;
                descripcionPeriodo = `${duracion} día${duracion !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'semana') {
                const semanas = Math.ceil(duracion / 7);
                precioTotal = equipo.precioUnitario * cantidad * semanas;
                descripcionPeriodo = `${semanas} semana${semanas !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'mes') {
                const meses = Math.ceil(duracion / 30);
                precioTotal = equipo.precioUnitario * cantidad * meses;
                descripcionPeriodo = `${meses} mes${meses !== 1 ? 'es' : ''}`;
            } else if (equipo.periodo === 'trimestre') {
                const trimestres = Math.ceil(duracion / 90);
                precioTotal = equipo.precioUnitario * cantidad * trimestres;
                descripcionPeriodo = `${trimestres} trimestre${trimestres !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'semestre') {
                const semestres = Math.ceil(duracion / 180);
                precioTotal = equipo.precioUnitario * cantidad * semestres;
                descripcionPeriodo = `${semestres} semestre${semestres !== 1 ? 's' : ''}`;
            } else if (equipo.periodo === 'anio') {
                const anios = Math.ceil(duracion / 365);
                precioTotal = equipo.precioUnitario * cantidad * anios;
                descripcionPeriodo = `${anios} año${anios !== 1 ? 's' : ''}`;
            }

            subtotal += precioTotal;

            // Calcular impuestos solo si el producto tiene IVA
            if (equipo.conIva !== false) {
                impuestos += precioTotal * 0.19;
            }

            $('#resumen-costos').append(`
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    ${cantidad} x ${equipo.equipoTexto} (${descripcionPeriodo})
                    <span class="badge bg-primary rounded-pill">$${precioTotal.toFixed(2)}</span>
                </li>
            `);
        });

        const total = subtotal + impuestos;

        $('#subtotal').text('$' + subtotal.toFixed(2));
        $('#impuestos').text('$' + impuestos.toFixed(2));
        $('#total').text('$' + total.toFixed(2));
    }

    // Validación del formulario
    (function () {
        'use strict';

        var forms = document.querySelectorAll('.needs-validation');

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