// editar_alquiler.js
document.addEventListener('DOMContentLoaded', function () {
    // Verificar que jQuery esté cargado
    if (typeof jQuery == 'undefined') {
        console.error('jQuery no está cargado');
        return;
    }

    // Usar una IIFE para evitar contaminación del scope global
    (function ($) {
        // Configuración inicial
        const config = {
            ajaxUrls: {
                series_disponibles: window.SERIES_DISPONIBLES_URL || "/series-disponibles/"
            }
        };

        // Estado de la aplicación
        const state = {
            equiposAgregados: [],
            equiposEliminados: [],
            contadorEquipos: 0
        };

        // ==================== FUNCIONES DE INICIALIZACIÓN ====================

        function init() {
            initSelect2();
            bindEvents();
            cargarEquiposExistentes();
            calcularDuracion();
            actualizarResumenCostos();
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
                closeOnSelect: false
            }).prop('disabled', true);

            $('#periodo-selector').select2({
                placeholder: "Seleccione periodo...",
                allowClear: false,
                width: '100%'
            });
        }

        function bindEvents() {
            // Fechas
            $('#id_fecha_inicio, #id_fecha_fin').off('change').on('change', calcularDuracion);

            // Selectores de equipo
            $('#equipo-selector').off('change').on('change', cargarSeriesDisponibles);
            $('#agregar-equipo').off('click').on('click', agregarEquipo);

            // Resumen de costos
            $('#id_descuento, #id_iva').off('change').on('change', actualizarResumenCostos);

            // Formulario
            $('#form-alquiler').off('submit').on('submit', enviarFormulario);
        }

        // ==================== FUNCIONES PRINCIPALES ====================

        function cargarEquiposExistentes() {
            const equiposExistentesElement = document.getElementById('equipos-existentes');
            if (!equiposExistentesElement) return;

            try {
                const equiposExistentesData = JSON.parse(equiposExistentesElement.textContent);

                equiposExistentesData.forEach((equipo, index) => {
                    let series = Array.isArray(equipo.series)
                        ? equipo.series
                        : (typeof equipo.series === 'string'
                            ? equipo.series.split(',').map(s => s.trim()).filter(Boolean)
                            : []);

                    state.equiposAgregados.push({
                        id: state.contadorEquipos++,
                        equipoId: equipo.equipoId,
                        equipoTexto: equipo.equipoTexto,
                        series: series,
                        periodo: equipo.periodo,
                        periodoTexto: obtenerTextoPeriodo(equipo.periodo),
                        precioUnitario: parseFloat(equipo.precioUnitario) || 0,
                        existente: true,
                        detalleId: equipo.id,
                        formIndex: index
                    });
                });

                actualizarTablaEquipos();
                actualizarInputsOcultos();
            } catch (e) {
                console.error("Error al cargar equipos existentes:", e);
            }
        }

        function calcularDuracion() {
            const inicio = new Date($('#id_fecha_inicio').val());
            const fin = new Date($('#id_fecha_fin').val());

            if (isNaN(inicio) || isNaN(fin)) return;

            const diffDays = Math.ceil((fin - inicio) / (1000 * 60 * 60 * 24)) + 1;
            let texto = diffDays + ' día' + (diffDays !== 1 ? 's' : '');

            if (diffDays >= 7) {
                const semanas = Math.floor(diffDays / 7);
                const diasRestantes = diffDays % 7;
                texto = semanas + ' semana' + (semanas !== 1 ? 's' : '');
                if (diasRestantes > 0) {
                    texto += ' y ' + diasRestantes + ' día' + (diasRestantes !== 1 ? 's' : '');
                }
            }

            $('#duracion-alquiler').val(texto);
            actualizarResumenCostos();
        }

        function cargarSeriesDisponibles() {
            const equipoId = $(this).val();
            const serieSelector = $('#serie-selector');

            if (!equipoId) {
                serieSelector.empty().prop('disabled', true);
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

                    // Filtrar series ya seleccionadas para este equipo
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
            const equipoTexto = $('#equipo-selector option:selected').text().split('(')[0].trim();
            const series = $('#serie-selector').val() || [];
            const periodo = $('#periodo-selector').val();
            const periodoTexto = $('#periodo-selector option:selected').text();

            // Validaciones básicas
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
            const existenteIndex = state.equiposAgregados.findIndex(e =>
                e.equipoId == equipoId && e.periodo == periodo
            );

            if (existenteIndex >= 0) {
                // Verificar series duplicadas
                const seriesDuplicadas = series.filter(serie =>
                    state.equiposAgregados[existenteIndex].series.includes(serie)
                );

                if (seriesDuplicadas.length > 0) {
                    alert(`Las siguientes series ya están agregadas: ${seriesDuplicadas.join(', ')}`);
                    return;
                }

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
                    detalleId: null
                });
            }

            actualizarTablaEquipos();
            actualizarInputsOcultos();
            actualizarResumenCostos();

            // Limpiar selección de series
            $('#serie-selector').val(null).trigger('change');
        }

        // ==================== FUNCIONES DE ACTUALIZACIÓN ====================

        function actualizarTablaEquipos() {
            const tbody = $('#tabla-equipos tbody').empty();

            if (state.equiposAgregados.length === 0) {
                tbody.append(
                    $('<tr>').append(
                        $('<td>').attr('colspan', 6).text('No hay equipos agregados')
                    )
                );
                return;
            }

            state.equiposAgregados.forEach(equipo => {
                const row = $('<tr>').attr('data-id', equipo.id);
                if (equipo.existente) row.addClass('table-info');

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

                // Botón de eliminar
                const deleteBtn = $('<button>').addClass('btn btn-danger btn-sm')
                    .html('<i class="fas fa-trash"></i>')
                    .click(function (e) {
                        e.preventDefault();
                        eliminarEquipo(equipo.id);
                    });

                row.append($('<td>').addClass('text-center').append(deleteBtn));
                tbody.append(row);
            });

            // Manejar cambios en precios
            $('.precio-unitario').off('change').on('change', function () {
                const id = $(this).data('id');
                const nuevoPrecio = parseFloat($(this).val()) || 0;
                const equipoIndex = state.equiposAgregados.findIndex(e => e.id == id);

                if (equipoIndex >= 0) {
                    state.equiposAgregados[equipoIndex].precioUnitario = nuevoPrecio;
                    const cantidad = state.equiposAgregados[equipoIndex].series.length;
                    $(`.precio-total[data-id="${id}"]`).text('$' + (nuevoPrecio * cantidad).toFixed(2));
                    actualizarResumenCostos();
                    actualizarInputsOcultos();
                }
            });
        }

        function eliminarEquipo(id) {
            const index = state.equiposAgregados.findIndex(e => e.id === id);
            if (index >= 0) {
                const equipo = state.equiposAgregados[index];

                // Si es un equipo existente, agregar a la lista de eliminados
                if (equipo.existente && equipo.detalleId) {
                    const yaEliminado = state.equiposEliminados.some(e => e.detalleId === equipo.detalleId);
                    if (!yaEliminado) {
                        state.equiposEliminados.push({
                            detalleId: equipo.detalleId,
                            equipoId: equipo.equipoId,
                            seriesOriginal: equipo.series.slice(),
                            periodoOriginal: equipo.periodo,
                            precioUnitario: equipo.precioUnitario
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

            // Actualizar campos de gestión del formset
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

            // Agregar equipos eliminados primero (para mantener los IDs)
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
                    })
                );
            });

            // Agregar equipos activos
            state.equiposAgregados.forEach((equipo, index) => {
                const formIndex = index + state.equiposEliminados.length;

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
                        value: equipo.series.length
                    }),
                    $('<input>').attr({
                        type: 'hidden',
                        name: `detalles-${formIndex}-precio_unitario`,
                        value: equipo.precioUnitario.toFixed(2)
                    })
                );

                // Solo agregar ID si es un equipo existente
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
            $('#resumen-costos').empty();

            if (state.equiposAgregados.length === 0) {
                $('#resumen-costos').append(
                    $('<li>').addClass('list-group-item').text('No hay equipos agregados')
                );
            }

            state.equiposAgregados.forEach(equipo => {
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

            const descuento = parseFloat($('#id_descuento').val()) || 0;
            const iva = parseFloat($('#id_iva').val()) || 0.19; // 19% por defecto

            const montoDescuento = subtotal * (descuento / 100);
            const subtotalConDescuento = subtotal - montoDescuento;
            const montoIva = subtotalConDescuento * (iva / 100);
            const total = subtotalConDescuento + montoIva;

            $('#subtotal').text('$' + subtotal.toFixed(2));
            $('#monto-descuento').text('$' + montoDescuento.toFixed(2));
            $('#subtotal-con-descuento').text('$' + subtotalConDescuento.toFixed(2));
            $('#monto-iva').text('$' + montoIva.toFixed(2));
            $('#total').text('$' + total.toFixed(2));
            $('#id_total').val(total.toFixed(2));
        }

        // ==================== FUNCIONES AUXILIARES ====================

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

            // Validar cliente
            if (!$('#id_cliente').val()) {
                errores.push('Por favor seleccione un cliente');
            }

            // Validar fechas
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

            // Validar equipos
            if (state.equiposAgregados.length === 0) {
                errores.push('Debe agregar al menos un equipo al alquiler');
            }

            // Validar precios
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

            // Actualizar inputs ocultos antes de enviar
            actualizarInputsOcultos();

            // Mostrar loading
            const submitButton = $(this).find('button[type="submit"]');
            const originalText = submitButton.text();
            submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Guardando...');

            // Enviar formulario
            $.ajax({
                url: $(this).attr('action'),
                method: 'POST',
                data: $(this).serialize(),
                dataType: 'json',  // Asegúrate de esperar una respuesta JSON
                success: function (response) {
                    if (response.success) {
                        if (response.redirect_url) {
                            window.location.href = response.redirect_url;
                        } else {
                            // Redirección por defecto si no viene en la respuesta
                            window.location.href = "{% url 'alquiler:listar_alquileres' %}";
                        }
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

        // Inicializar la aplicación
        init();

    })(jQuery);
});