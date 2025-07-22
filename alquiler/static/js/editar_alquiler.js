document.addEventListener('DOMContentLoaded', function () {
    if (typeof jQuery == 'undefined') {
        console.error('jQuery no está cargado');
        return;
    }

    (function ($) {
        const state = {
            equiposAgregados: [],
            equiposEliminados: [],
            contadorEquipos: 0
        };

        function init() {
            initSelect2();
            bindEvents();
            cargarEquiposExistentes();
            calcularDuracion();
            actualizarResumenCostos();
            sincronizarFechasVencimiento();
        }

        function initSelect2() {
            $('.select2').select2({
                placeholder: "Seleccione...",
                allowClear: true,
                width: '100%'
            });

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

            $('#periodo-selector').select2({
                placeholder: "Seleccione periodo...",
                allowClear: false,
                width: '100%'
            });
        }

        function bindEvents() {
            $('#id_fecha_inicio, #id_fecha_fin').on('change', function() {
                calcularDuracion();
                sincronizarFechasVencimiento();
            });

            $('#equipo-selector').on('change', cargarSeriesDisponibles);
            $('#agregar-equipo').on('click', agregarEquipo);
            $('#form-alquiler').on('submit', enviarFormulario);
        }

        function sincronizarFechasVencimiento() {
            const fechaFin = $('#id_fecha_fin').val();
            if (fechaFin) {
                $('#id_fecha_vencimiento').val(fechaFin);
            }
        }

        function cargarEquiposExistentes() {
    const equiposExistentesElement = document.getElementById('equipos-existentes');
    if (!equiposExistentesElement) return;

    try {
        const equiposExistentesData = JSON.parse(equiposExistentesElement.textContent);

        equiposExistentesData.forEach((equipo, index) => {
            // Filtrar series vacías
            let series = Array.isArray(equipo.series)
                ? equipo.series.filter(s => s && s.trim() !== '')
                : (typeof equipo.series === 'string'
                    ? equipo.series.split(',').map(s => s.trim()).filter(Boolean)
                    : []);

            // Obtener el precio del periodo seleccionado
            const equipoOption = $(`#equipo-selector option[value="${equipo.equipoId}"]`);
            let precioUnitario = parseFloat(equipo.precioUnitario) || 0;
            
            // Si no tiene precio, obtenerlo del equipo
            if (precioUnitario <= 0 && equipoOption.length) {
                precioUnitario = parseFloat(equipoOption.data(`precio-${equipo.periodo}`)) || 0;
            }

            state.equiposAgregados.push({
                id: state.contadorEquipos++,
                equipoId: equipo.equipoId,
                equipoTexto: equipo.equipoTexto,
                series: series,
                periodo: equipo.periodo,
                periodoTexto: obtenerTextoPeriodo(equipo.periodo),
                precioUnitario: precioUnitario,
                existente: true,
                detalleId: equipo.id,
                formIndex: index,
                conIva: equipo.conIva !== false,
                requiereSerie: equipo.requiereSerie || (equipoOption.length && equipoOption.data('requiere-serie') === 'True')
            });
        });

        actualizarTablaEquipos();
        actualizarInputsOcultos();
    } catch (e) {
        console.error("Error al cargar equipos existentes:", e);
    }
}

        function cargarSeriesDisponibles() {
            const equipoId = $(this).val();
            const serieSelector = $('#serie-selector');
            const equipoOption = $('#equipo-selector option:selected');
            const requiereSerie = equipoOption.data('requiere-serie') === 'True';

            serieSelector.empty().prop('disabled', true);
            $('#sinSerieHelp').hide();

            if (!equipoId) return;

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

            $.ajax({
                url: window.SERIES_DISPONIBLES_URL.replace('{equipoId}', equipoId),
                method: 'GET',
                dataType: 'json',
                success: function (data) {
                    serieSelector.empty();
                    data.series.forEach(value => {
                        serieSelector.append($('<option>', { value, text: value }));
                    });

                    const yaSeleccionadas = state.equiposAgregados
                        .filter(e => e.equipoId == equipoId)
                        .flatMap(e => e.series);

                    if (yaSeleccionadas.length) {
                        serieSelector.val(yaSeleccionadas).trigger('change');
                    }

                    serieSelector.prop('disabled', false);
                },
                error: function (xhr, status, error) {
                    console.error("Error al cargar series:", error);
                    serieSelector.empty().prop('disabled', true);
                }
            });
        }

        function agregarEquipo() {
            const equipoId = $('#equipo-selector').val();
            const equipoOption = $('#equipo-selector option:selected');
            const equipoTexto = equipoOption.text().split('(')[0].trim();
            const series = $('#serie-selector').val() || [];
            const periodo = $('#periodo-selector').val();
            const periodoTexto = $('#periodo-selector option:selected').text();
            const requiereSerie = equipoOption.data('requiere-serie') === 'True';
            const precioUnitario = parseFloat(equipoOption.data(`precio-${periodo}`)) || 0;

            if (!equipoId) {
                alert('Por favor seleccione un equipo');
                return;
            }

            if (requiereSerie && series.length === 0) {
                alert('Por favor seleccione al menos un número de serie');
                return;
            }

            // Permitir múltiples equipos sin serie
            if (!requiereSerie) {
                state.equiposAgregados.push({
                    id: state.contadorEquipos++,
                    equipoId: equipoId,
                    equipoTexto: equipoTexto,
                    series: [],
                    periodo: periodo,
                    periodoTexto: periodoTexto,
                    precioUnitario: precioUnitario,
                    existente: false,
                    detalleId: null,
                    conIva: true,
                    requiereSerie: false
                });
            } else {
                // Verificar si ya existe este equipo con el mismo periodo
                const existenteIndex = state.equiposAgregados.findIndex(e =>
                    e.equipoId == equipoId && e.periodo == periodo
                );

                if (existenteIndex >= 0) {
                    // Actualizar series existentes
                    state.equiposAgregados[existenteIndex].series = [
                        ...new Set([...state.equiposAgregados[existenteIndex].series, ...series])
                    ];
                } else {
                    // Agregar nuevo equipo
                    state.equiposAgregados.push({
                        id: state.contadorEquipos++,
                        equipoId: equipoId,
                        equipoTexto: equipoTexto,
                        series: series,
                        periodo: periodo,
                        periodoTexto: periodoTexto,
                        precioUnitario: precioUnitario,
                        existente: false,
                        detalleId: null,
                        conIva: true,
                        requiereSerie: true
                    });
                }
            }

            actualizarTablaEquipos();
            actualizarInputsOcultos();
            actualizarResumenCostos();

            // Limpiar selección
            $('#equipo-selector').val('').trigger('change');
            $('#serie-selector').val(null).trigger('change');
        }

        function actualizarTablaEquipos() {
            const tbody = $('#tabla-equipos tbody').empty();

            if (state.equiposAgregados.length === 0) {
                tbody.append(
                    $('<tr>').append(
                        $('<td>').attr('colspan', 7).text('No hay equipos agregados')
                    )
                );
                return;
            }

            state.equiposAgregados.forEach(equipo => {
                const row = $('<tr>').attr('data-id', equipo.id);
                if (equipo.existente) row.addClass('table-info');

                row.append($('<td>').text(equipo.equipoTexto));

                const seriesText = equipo.requiereSerie ?
                    (equipo.series.length > 0 ? equipo.series.join(', ') : 'Sin serie') :
                    'No aplica';
                row.append($('<td>').text(seriesText));

                row.append($('<td>').text(equipo.periodoTexto));

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

                const cantidad = equipo.requiereSerie ? equipo.series.length : 1;
                row.append($('<td>').addClass('text-end precio-total').attr('data-id', equipo.id)
                    .text('$' + (equipo.precioUnitario * cantidad).toFixed(2)));

                const ivaSwitch = $('<div>').addClass('form-check form-switch').append(
                    $('<input>').attr({
                        type: 'checkbox',
                        class: 'form-check-input iva-checkbox',
                        id: `iva-${equipo.id}`,
                        'data-id': equipo.id,
                        checked: equipo.conIva
                    }),
                    $('<label>').attr('for', `iva-${equipo.id}`).addClass('form-check-label').text('IVA')
                );
                row.append($('<td>').addClass('text-center').append(ivaSwitch));

                const deleteBtn = $('<button>').addClass('btn btn-danger btn-sm')
                    .html('<i class="fas fa-trash"></i>')
                    .click(function (e) {
                        e.preventDefault();
                        eliminarEquipo(equipo.id);
                    });

                row.append($('<td>').addClass('text-center').append(deleteBtn));
                tbody.append(row);
            });

            $('.precio-unitario').off('change').on('change', function () {
                const id = $(this).data('id');
                const nuevoPrecio = parseFloat($(this).val()) || 0;
                const equipoIndex = state.equiposAgregados.findIndex(e => e.id == id);

                if (equipoIndex >= 0) {
                    state.equiposAgregados[equipoIndex].precioUnitario = nuevoPrecio;
                    const cantidad = state.equiposAgregados[equipoIndex].requiereSerie ? 
                        state.equiposAgregados[equipoIndex].series.length : 1;
                    $(`.precio-total[data-id="${id}"]`).text('$' + (nuevoPrecio * cantidad).toFixed(2));
                    actualizarResumenCostos();
                    actualizarInputsOcultos();
                }
            });

            $('.iva-checkbox').off('change').on('change', function () {
                const id = $(this).data('id');
                const conIva = $(this).is(':checked');

                const equipoIndex = state.equiposAgregados.findIndex(e => e.id == id);
                if (equipoIndex >= 0) {
                    state.equiposAgregados[equipoIndex].conIva = conIva;
                    actualizarResumenCostos();
                    actualizarInputsOcultos();
                }
            });
        }

        function eliminarEquipo(id) {
            const index = state.equiposAgregados.findIndex(e => e.id === id);
            if (index >= 0) {
                const equipo = state.equiposAgregados[index];

                if (equipo.existente && equipo.detalleId) {
                    const yaEliminado = state.equiposEliminados.some(e => e.detalleId === equipo.detalleId);
                    if (!yaEliminado) {
                        state.equiposEliminados.push({
                            detalleId: equipo.detalleId,
                            equipoId: equipo.equipoId,
                            seriesOriginal: equipo.series.slice(),
                            periodoOriginal: equipo.periodo,
                            precioUnitario: equipo.precioUnitario,
                            conIva: equipo.conIva
                        });
                    }
                }

                state.equiposAgregados.splice(index, 1);
                actualizarTablaEquipos();
                actualizarInputsOcultos();
                actualizarResumenCostos();
            }
        }

        function actualizarInputsOcultos() {
            const container = $('#equipos-container').empty();
            const totalForms = state.equiposAgregados.length + state.equiposEliminados.length;
            const initialForms = state.equiposAgregados.filter(e => e.existente).length + state.equiposEliminados.length;

            container.append(
                $('<input>').attr({
                    type: 'hidden',
                    name: 'detalles-TOTAL_FORMS',
                    value: totalForms
                }),
                $('<input>').attr({
                    type: 'hidden',
                    name: 'detalles-INITIAL_FORMS',
                    value: initialForms
                })
            );

            state.equiposEliminados.forEach((equipo, index) => {
                container.append(
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-id`,
                        value: equipo.detalleId
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-DELETE`,
                        value: 'on'
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-equipo`,
                        value: equipo.equipoId
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-numeros_serie`,
                        value: JSON.stringify(equipo.seriesOriginal)
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-periodo_alquiler`,
                        value: equipo.periodoOriginal
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-cantidad`,
                        value: equipo.seriesOriginal.length
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-precio_unitario`,
                        value: equipo.precioUnitario.toFixed(2)
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${index}-con_iva`,
                        value: equipo.conIva ? 'on' : ''
                    })
                );
            });

            state.equiposAgregados.forEach((equipo, index) => {
                const formIndex = index + state.equiposEliminados.length;
                const cantidad = equipo.requiereSerie ? equipo.series.length : 1;

                container.append(
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-equipo`,
                        value: equipo.equipoId
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-numeros_serie`,
                        value: JSON.stringify(equipo.series)
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-periodo_alquiler`,
                        value: equipo.periodo
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-cantidad`,
                        value: cantidad
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-precio_unitario`,
                        value: equipo.precioUnitario.toFixed(2)
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-con_iva`,
                        value: equipo.conIva ? 'on' : ''
                    })
                );

                if (equipo.existente && equipo.detalleId) {
                    container.append(
                        $('<input>').attr({
                            type: 'hidden',
                            name: `detalles-${formIndex}-id`,
                            value: equipo.detalleId
                        })
                    );
                }
            });
        }

        function actualizarResumenCostos() {
            const duracionText = $('#duracion-alquiler').val();
            const duracionMatch = duracionText.match(/\d+/);
            const duracion = duracionMatch ? parseInt(duracionMatch[0]) : 1;

            let subtotal = 0;
            let impuestos = 0;
            $('#resumen-costos').empty();

            if (state.equiposAgregados.length === 0) {
                $('#resumen-costos').append(
                    $('<li>').addClass('list-group-item').text('No hay equipos agregados')
                );
            }

            state.equiposAgregados.forEach(equipo => {
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

                if (equipo.conIva) {
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

        function obtenerTextoPeriodo(periodo) {
            const periodos = {
                'dia': 'Por día',
                'semana': 'Por semana',
                'mes': 'Por mes',
                'trimestre': 'Por trimestre',
                'semestre': 'Por semestre',
                'anio': 'Por año'
            };
            return periodos[periodo] || periodo;
        }

        function validarFormulario() {
            const errores = [];

            if (!$('#id_cliente').val()) {
                errores.push('Por favor seleccione un cliente');
            }

            const fechaInicio = $('#id_fecha_inicio').val();
            const fechaFin = $('#id_fecha_fin').val();

            if (!fechaInicio) {
                errores.push('Por favor ingrese una fecha de inicio');
            }

            if (!fechaFin) {
                errores.push('Por favor ingrese una fecha de fin');
            }

            if (fechaInicio && fechaFin && new Date(fechaInicio) > new Date(fechaFin)) {
                errores.push('La fecha de inicio no puede ser posterior a la fecha de fin');
            }

            if (state.equiposAgregados.length === 0) {
                errores.push('Debe agregar al menos un equipo al alquiler');
            }

            const equiposConPreciosInvalidos = state.equiposAgregados.filter(eq =>
                isNaN(eq.precioUnitario) || eq.precioUnitario <= 0
            );

            if (equiposConPreciosInvalidos.length > 0) {
                errores.push('Todos los equipos deben tener un precio unitario válido mayor a 0');
            }

            return errores;
        }

        function enviarFormulario(e) {
            e.preventDefault();

            const errores = validarFormulario();

            if (errores.length > 0) {
                alert('Por favor corrija los siguientes errores:\n\n' + errores.join('\n'));
                return false;
            }

            actualizarInputsOcultos();

            const submitButton = $(this).find('button[type="submit"]');
            const originalText = submitButton.text();
            submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Guardando...');

            $.ajax({
                url: $(this).attr('action'),
                method: 'POST',
                data: $(this).serialize(),
                dataType: 'json',
                success: function (response) {
                    if (response.success) {
                        window.location.href = response.redirect_url || "{% url 'alquiler:listar_alquileres' %}";
                    } else {
                        let errorMessage = 'Error al guardar el alquiler';
                        if (response.errors) {
                            errorMessage += ': ' + Object.values(response.errors).join('\n');
                        }
                        alert(errorMessage);
                        submitButton.prop('disabled', false).html(originalText);
                    }
                },
                error: function (xhr) {
                    let errorMessage = 'Error al guardar el alquiler';
                    try {
                        const errors = JSON.parse(xhr.responseText);
                        errorMessage += ':\n' + Object.values(errors).join('\n');
                    } catch (e) {
                        errorMessage += '. Por favor intente nuevamente.';
                    }
                    alert(errorMessage);
                    submitButton.prop('disabled', false).html(originalText);
                }
            });
        }

        init();

    })(jQuery);
});