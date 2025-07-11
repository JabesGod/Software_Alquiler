$(document).ready(function () {
    // Inicializar Select2
    $('.select2').select2({
        placeholder: "Seleccione...",
        allowClear: true,
        width: '100%'
    });

    // Variables
    let equiposAgregados = [];
    let contadorEquipos = 0;
    let equiposEliminados = [];

    // Cargar equipos existentes
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

                equiposAgregados.push({
                    id: contadorEquipos++,
                    equipoId: equipo.equipoId,
                    equipoTexto: equipo.equipoTexto,
                    series: series,
                    periodo: equipo.periodo,
                    periodoTexto: equipo.periodoTexto,
                    precioUnitario: parseFloat(equipo.precioUnitario) || 0,
                    existente: true,
                    detalleId: equipo.id,
                    formIndex: index
                });
            });

            actualizarTablaEquipos();
            actualizarResumenCostos();
            actualizarInputsOcultos();
        } catch (e) {
            console.error("Error al cargar equipos existentes:", e);
        }
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

    $('#id_fecha_inicio, #id_fecha_fin').change(calcularDuracion);
    calcularDuracion();

    $('#equipo-selector').change(function () {
        const equipoId = $(this).val();
        const serieSelector = $('#serie-selector');
        if (!equipoId) return serieSelector.empty().prop('disabled', true);

        $.ajax({
            url: `/equipos/${equipoId}/series-disponibles/`,
            success: function (data) {
                serieSelector.empty();
                data.series.forEach(value => {
                    serieSelector.append($('<option>', { value, text: value }));
                });

                const yaSeleccionadas = equiposAgregados
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

    $('#agregar-equipo').click(function () {
        const equipoId = $('#equipo-selector').val();
        const equipoTexto = $('#equipo-selector option:selected').text().split('(')[0].trim();
        const series = $('#serie-selector').val() || [];
        const periodo = $('#periodo-selector').val();
        const periodoTexto = $('#periodo-selector option:selected').text();

        if (!equipoId || series.length === 0 || !periodo) {
            alert('Todos los campos del equipo son requeridos.');
            return;
        }

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

        const existenteIndex = equiposAgregados.findIndex(e => e.equipoId == equipoId && e.periodo == periodo);
        if (existenteIndex >= 0) {
            const duplicadas = series.filter(serie =>
                equiposAgregados[existenteIndex].series.includes(serie));
            if (duplicadas.length) {
                return alert(`Series duplicadas: ${duplicadas.join(', ')}`);
            }
            equiposAgregados[existenteIndex].series = [...new Set([...equiposAgregados[existenteIndex].series, ...series])];
        } else {
            equiposAgregados.push({
                id: contadorEquipos++,
                equipoId,
                equipoTexto,
                series,
                periodo,
                periodoTexto,
                precioUnitario,
                existente: false,
                detalleId: null
            });
        }

        actualizarTablaEquipos();
        actualizarInputsOcultos();
        actualizarResumenCostos();
        $('#serie-selector').val(null).trigger('change');
    });

    function actualizarTablaEquipos() {
        const tbody = $('#tabla-equipos tbody').empty();

        if (!equiposAgregados.length) {
            return tbody.append('<tr><td colspan="6">No hay equipos agregados</td></tr>');
        }

        equiposAgregados.forEach(equipo => {
            const row = $('<tr>').attr('data-id', equipo.id);
            if (equipo.existente) row.addClass('table-info');

            row.append(`<td>${equipo.equipoTexto}</td>`);
            row.append(`<td>${equipo.series.join(', ')}</td>`);
            row.append(`<td>${equipo.periodoTexto}</td>`);

            const inputPrecio = $('<input>', {
                type: 'number',
                class: 'form-control precio-unitario',
                value: equipo.precioUnitario.toFixed(2),
                'data-id': equipo.id,
                step: '0.01',
                min: '0',
                style: 'width: 100px;'
            });

            row.append($('<td class="text-end">').append(inputPrecio));
            row.append(`<td class="text-end precio-total" data-id="${equipo.id}">$${(equipo.precioUnitario * equipo.series.length).toFixed(2)}</td>`);

            // Botón de eliminar corregido
            const deleteButton = $('<button>', {
                type: 'button', // Importante: type="button" para que no envíe el formulario
                class: 'btn btn-danger btn-sm',
                html: '<i class="fas fa-trash"></i>',
                click: function (e) {
                    eliminarEquipo(equipo.id, e);
                }
            });

            row.append($('<td class="text-center">').append(deleteButton));
            tbody.append(row);
        });

        $('.precio-unitario').change(function () {
            const id = $(this).data('id');
            const nuevoPrecio = parseFloat($(this).val()) || 0;
            const idx = equiposAgregados.findIndex(e => e.id == id);
            if (idx >= 0) {
                equiposAgregados[idx].precioUnitario = nuevoPrecio;
                $(`.precio-total[data-id="${id}"]`).text('$' + (nuevoPrecio * equiposAgregados[idx].series.length).toFixed(2));
                actualizarResumenCostos();
                actualizarInputsOcultos();
            }
        });
    }

    function eliminarEquipo(id, event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        const index = equiposAgregados.findIndex(e => e.id === id);
        if (index >= 0) {
            const equipo = equiposAgregados[index];
            if (equipo.existente && equipo.detalleId) {
                const yaEliminado = equiposEliminados.some(e => e.detalleId === equipo.detalleId);
                if (!yaEliminado) {
                    equiposEliminados.push({
                        detalleId: equipo.detalleId,
                        equipoId: equipo.equipoId,
                        seriesOriginal: equipo.series.slice(),
                        periodoOriginal: equipo.periodo,
                        precioUnitario: equipo.precioUnitario ?? 0  // <- aquí aseguras que nunca sea undefined
                    });

                }
            }
            equiposAgregados.splice(index, 1);
        }
        actualizarTablaEquipos();
        actualizarInputsOcultos();
        actualizarResumenCostos();
    }

    function actualizarInputsOcultos() {
        const form = $('#form-alquiler');
        form.find('input[name^="detalles-"], input[name^="equipos_eliminados"]').remove();

        // Calcular correctamente los formularios iniciales
        const initialForms = equiposAgregados.filter(e => e.existente).length + equiposEliminados.length;

        $('<input>', {
            type: 'hidden',
            name: 'detalles-TOTAL_FORMS',
            value: equiposAgregados.length + equiposEliminados.length
        }).appendTo(form);

        $('<input>', {
            type: 'hidden',
            name: 'detalles-INITIAL_FORMS',
            value: initialForms
        }).appendTo(form);

        // Contador para formularios
        let formIndex = 0;

        // Primero agregar los equipos eliminados (para mantener los IDs)
        // Eliminados primero
        equiposEliminados.forEach(equipo => {
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-id`,
                value: equipo.detalleId
            }).appendTo(form);

            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-DELETE`,
                value: 'on'
            }).appendTo(form);

            // 📌 Ahora agregamos los campos requeridos con sus valores originales
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-equipo`,
                value: equipo.equipoId
            }).appendTo(form);
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-numeros_serie`,
                value: JSON.stringify(equipo.seriesOriginal || [])
            }).appendTo(form);
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-periodo_alquiler`,
                value: equipo.periodoOriginal
            }).appendTo(form);
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-cantidad`,
                value: (equipo.seriesOriginal || []).length
            }).appendTo(form);
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-precio_unitario`,
                value: equipo.precioUnitario.toFixed(2)
            }).appendTo(form);

            formIndex++;
        });


        // Luego agregar los equipos activos
        equiposAgregados.forEach(equipo => {
            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-equipo`,
                value: equipo.equipoId
            }).appendTo(form);

            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-numeros_serie`,
                value: JSON.stringify(equipo.series)
            }).appendTo(form);

            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-periodo_alquiler`,
                value: equipo.periodo
            }).appendTo(form);

            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-cantidad`,
                value: equipo.series.length
            }).appendTo(form);

            $('<input>', {
                type: 'hidden',
                name: `detalles-${formIndex}-precio_unitario`,
                value: equipo.precioUnitario.toFixed(2)
            }).appendTo(form);

            // Solo agregar ID si es un equipo existente
            if (equipo.existente && equipo.detalleId) {
                $('<input>', {
                    type: 'hidden',
                    name: `detalles-${formIndex}-id`,
                    value: equipo.detalleId
                }).appendTo(form);
            }

            formIndex++;
        });
    }

    function actualizarResumenCostos() {
        let subtotal = equiposAgregados.reduce((acc, eq) => acc + (eq.precioUnitario * eq.series.length), 0);
        const descuento = parseFloat($('#id_descuento').val()) || 0;
        const iva = parseFloat($('#id_iva').val()) || 0;
        const montoDescuento = subtotal * (descuento / 100);
        const subtotalConDescuento = subtotal - montoDescuento;
        const montoIva = subtotalConDescuento * (iva / 100);
        const total = subtotalConDescuento + montoIva;

        $('#subtotal').text('$' + subtotal.toFixed(2));
        $('#monto-descuento').text('$' + montoDescuento.toFixed(2));
        $('#subtotal-con-descuento').text('$' + subtotalConDescuento.toFixed(2));
        $('#monto-iva').text('$' + montoIva.toFixed(2));
        $('#total-final').text('$' + total.toFixed(2));
        $('#id_total').val(total.toFixed(2));
    }

    $('#id_descuento, #id_iva').change(actualizarResumenCostos);

    $('#form-alquiler').off('submit').on('submit', function (e) {
        e.preventDefault();

        if (equiposAgregados.length === 0) {
            alert('Debe agregar al menos un equipo al alquiler');
            return false;
        }

        let errores = [];
        equiposAgregados.forEach((e, i) => {
            if (!e.equipoId) errores.push(`Equipo ${i + 1}: ID faltante`);
            if (!e.series || e.series.length === 0) errores.push(`Equipo ${i + 1}: Series faltantes`);
            if (!e.periodo) errores.push(`Equipo ${i + 1}: Periodo faltante`);
            if (!e.precioUnitario || e.precioUnitario <= 0) errores.push(`Equipo ${i + 1}: Precio inválido`);
        });

        if (errores.length) {
            alert('Errores:\n' + errores.join('\n'));
            return false;
        }

        actualizarInputsOcultos();
        this.submit();
    });

    // Inicializar la página
    function inicializar() {
        if (document.getElementById('equipos-existentes')) cargarEquiposExistentes();
        calcularDuracion();
        actualizarResumenCostos();
    }

    inicializar();
});