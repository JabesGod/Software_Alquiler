$(document).ready(function () {
    // Inicializar Select2
    $('.select2').select2({
        placeholder: "Seleccione...",
        allowClear: true,
        width: '100%'
    });

    let equiposAgregados = [];
    let contadorEquipos = 0;

    // Calcular duración
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

    $('#id_fecha_inicio, #id_fecha_fin').change(function () {
        if ($('#id_fecha_fin').val() && !$('#id_fecha_vencimiento').val()) {
            $('#id_fecha_vencimiento').val($('#id_fecha_fin').val());
        }
        calcularDuracion();
    });

    // Manejar cambio de equipo
    $('#equipo-selector').change(function () {
        const equipoId = $(this).val();
        const serieSelector = $('#serie-selector');

        if (!equipoId) {
            serieSelector.empty().prop('disabled', true);
            return;
        }

        serieSelector.empty().prop('disabled', true);
        serieSelector.append($('<option>', { value: '', text: 'Cargando series...' }));

        $.ajax({
            url: window.SERIES_DISPONIBLES_URL.replace('{equipoId}', equipoId),
            success: function (data) {
                serieSelector.empty();
                serieSelector.append($('<option>', { value: 'no_serie', text: 'No especificar serie' }));

                if (data.series && data.series.length > 0) {
                    data.series.forEach(value => {
                        serieSelector.append($('<option>', { value: value, text: value }));
                    });
                }

                serieSelector.prop('disabled', false);
            },
            error: function () {
                serieSelector.empty().append($('<option>', {
                    value: 'no_serie',
                    text: 'No especificar serie'
                })).prop('disabled', false);
            }
        });
    });

    // Configurar Select2 para series
    $('#serie-selector').select2({
        placeholder: "Seleccione series o 'No especificar serie'...",
        allowClear: true,
        width: '100%',
        closeOnSelect: false
    }).prop('disabled', true);

    // Agregar equipo
    $('#agregar-equipo').click(function () {
        const equipoId = $('#equipo-selector').val();
        const equipoTexto = $('#equipo-selector option:selected').text().split('(')[0].trim();
        let series = $('#serie-selector').val() || [];
        const periodo = $('#periodo-selector').val();
        const periodoTexto = $('#periodo-selector option:selected').text();
        const match = $('#equipo-selector option:selected').text().match(/Disponibles: (\d+)/);
        const disponible = match ? parseInt(match[1]) : 0;

        // Validaciones básicas
        if (!equipoId) return alert('Seleccione un equipo');
        if (!periodo) return alert('Seleccione un periodo');

        // Filtrar opción vacía si existe
        series = series.filter(serie => serie !== '');

        // Manejar caso sin serie específica
        if (series.length === 0 || (series.length === 1 && series[0] === 'no_serie')) {
            if (disponible <= 0) return alert('No hay unidades disponibles');
            series = ['no_serie'];
        }

        // Obtener precios
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

        // Verificar si ya existe este equipo
        const indexExistente = equiposAgregados.findIndex(e =>
            e.equipoId == equipoId && e.periodo == periodo
        );

        if (indexExistente >= 0) {
            const seriesDuplicadas = series.filter(serie =>
                serie !== 'no_serie' && equiposAgregados[indexExistente].series.includes(serie)
            );
            if (seriesDuplicadas.length > 0) {
                return alert(`Series ya agregadas: ${seriesDuplicadas.join(', ')}`);
            }
            equiposAgregados[indexExistente].series = [...new Set([...equiposAgregados[indexExistente].series, ...series])];
        } else {
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
        $('#serie-selector').val(null).trigger('change');
    });

    // Actualizar tabla de equipos
    function actualizarTablaEquipos() {
        const tbody = $('#tabla-equipos tbody').empty();

        if (equiposAgregados.length === 0) {
            tbody.append($('<tr>').append($('<td>').attr('colspan', 6).text('No hay equipos')));
            return;
        }

        equiposAgregados.forEach(equipo => {
            const row = $('<tr>').attr('data-id', equipo.id);
            row.append($('<td>').text(equipo.equipoTexto));
            row.append($('<td>').text(equipo.series[0] === 'no_serie' ? 'No especificado' : equipo.series.join(', ')));
            row.append($('<td>').text(equipo.periodoTexto));

            const precioInput = $('<input>').attr({
                type: 'number',
                class: 'form-control precio-unitario',
                value: equipo.precioUnitario.toFixed(2),
                'data-id': equipo.id,
                step: '0.01',
                min: '0'
            }).on('change', function () {
                const id = $(this).data('id');
                const nuevoPrecio = parseFloat($(this).val()) || 0;
                const index = equiposAgregados.findIndex(e => e.id == id);
                if (index >= 0) {
                    equiposAgregados[index].precioUnitario = nuevoPrecio;
                    actualizarResumenCostos();
                    actualizarInputsOcultos();
                }
            });

            row.append($('<td>').addClass('text-end').append(precioInput));

            const cantidad = equipo.series[0] === 'no_serie' ? 1 : equipo.series.length;
            row.append($('<td>').addClass('text-end').text('$' + (equipo.precioUnitario * cantidad).toFixed(2)));

            row.append($('<td>').addClass('text-center').append(
                $('<button>').addClass('btn btn-danger btn-sm').html('<i class="fas fa-trash"></i>').click(function () {
                    eliminarEquipo(equipo.id);
                })
            ));

            tbody.append(row);
        });
    }

    // Eliminar equipo
    function eliminarEquipo(id) {
        equiposAgregados = equiposAgregados.filter(e => e.id !== id);
        actualizarTablaEquipos();
        actualizarInputsOcultos();
        actualizarResumenCostos();
    }

    // Actualizar inputs ocultos
    function actualizarInputsOcultos() {
        const container = $('#equipos-container').empty();

        equiposAgregados.forEach((equipo, index) => {
            const seriesValue = equipo.series[0] === 'no_serie' ? '[]' : JSON.stringify(equipo.series);
            const cantidad = equipo.series[0] === 'no_serie' ? 1 : equipo.series.length;

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-equipo`,
                value: equipo.equipoId
            }));

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-numeros_serie`,
                value: seriesValue
            }));

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-periodo_alquiler`,
                value: equipo.periodo
            }));

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-cantidad`,
                value: cantidad
            }));

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-precio_unitario`,
                value: equipo.precioUnitario.toFixed(2)
            }));

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-id`,
                value: ''
            }));

            container.append($('<input>').attr({
                type: 'hidden',
                name: `detalles-${index}-DELETE`,
                value: 'false'
            }));
        });

        $('#id_detalles-TOTAL_FORMS').val(equiposAgregados.length);
    }

    // Actualizar resumen de costos
    // Actualizar resumen de costos
    function actualizarResumenCostos() {
        const conIva = $('#id_con_iva').is(':checked');
        const duracion = ($('#id_fecha_fin').val() && $('#id_fecha_inicio').val()) ?
            Math.ceil((new Date($('#id_fecha_fin').val()) - new Date($('#id_fecha_inicio').val())) / (1000 * 60 * 60 * 24)) + 1 : 1;

        let subtotal = 0;
        $('#resumen-costos').empty();

        equiposAgregados.forEach(equipo => {
            const cantidad = equipo.series[0] === 'no_serie' ? 1 : equipo.series.length;
            let precioTotal = 0;

            if (equipo.periodo === 'dia') {
                precioTotal = equipo.precioUnitario * cantidad * duracion;
            } else if (equipo.periodo === 'semana') {
                const semanas = Math.ceil(duracion / 7);
                precioTotal = equipo.precioUnitario * cantidad * semanas;
            } else if (equipo.periodo === 'mes') {
                const meses = Math.ceil(duracion / 30);
                precioTotal = equipo.precioUnitario * cantidad * meses;
            } else if (equipo.periodo === 'trimestre') {
                const trimestres = Math.ceil(duracion / 90);
                precioTotal = equipo.precioUnitario * cantidad * trimestres;
            } else if (equipo.periodo === 'semestre') {
                const semestres = Math.ceil(duracion / 180);
                precioTotal = equipo.precioUnitario * cantidad * semestres;
            } else if (equipo.periodo === 'anio') {
                const anios = Math.ceil(duracion / 365);
                precioTotal = equipo.precioUnitario * cantidad * anios;
            }

            subtotal += precioTotal;

            $('#resumen-costos').append(`
            <li class="list-group-item d-flex justify-content-between align-items-center">
                ${cantidad} x ${equipo.equipoTexto} (${equipo.periodoTexto})
                <span class="badge bg-primary rounded-pill">$${precioTotal.toFixed(2)}</span>
            </li>
        `);
        });

        const iva = parseFloat((conIva ? subtotal * 0.19 : 0).toFixed(2));
        const total = parseFloat((subtotal + iva).toFixed(2));

        $('#subtotal').text('$' + subtotal.toFixed(2));
        $('#impuestos').text('$' + iva.toFixed(2));
        $('#total').text('$' + total.toFixed(2));

        // Actualizar campos ocultos con valores por defecto si son null/undefined
        $('#id_iva').val(iva.toFixed(2));
        $('#id_precio_total').val(total.toFixed(2));
        $('#id_precio_sin_iva').val(subtotal.toFixed(2));
    }
    // Escuchar cambios en el checkbox de IVA
    $('#id_con_iva').change(actualizarResumenCostos);

    // Validación del formulario
    $('.needs-validation').on('submit', function (event) {
        if (equiposAgregados.length === 0) {
            event.preventDefault();
            alert('Debe agregar al menos un equipo');
            return;
        }

        if (!this.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }

        $(this).addClass('was-validated');
    });

    // Inicializar
    calcularDuracion();
    actualizarResumenCostos();
});