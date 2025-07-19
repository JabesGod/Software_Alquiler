document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, iniciando configuración de gráficas...');

    // Verificar si datosGraficas existe
    if (typeof datosGraficas === 'undefined') {
        console.error('ERROR: datosGraficas no está definido');
        return;
    }

    console.log('Datos recibidos:', datosGraficas);

    // Registrar el plugin de datalabels globalmente
    if (typeof ChartDataLabels !== 'undefined') {
        Chart.register(ChartDataLabels);
    }

    // Configuración común para gráficas
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.color = '#6c757d';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 4;
    Chart.defaults.plugins.tooltip.boxPadding = 4;
    // Función para inicializar o destruir un gráfico
    function initChart(chartId, chartType, data, options, plugins = []) {
        const canvas = document.getElementById(chartId);
        const noDataDiv = document.getElementById(`noData${chartId.replace('Chart', '')}`);

        if (!canvas) {
            console.error(`Canvas element with ID '${chartId}' not found.`);
            return;
        }

        console.log(`[${chartId}] Datos recibidos:`, data);

        // Verificar si hay datos de manera más robusta
        let hasData = false;
        try {
            if (data.labels && data.labels.length > 0) {
                if (chartType === 'bar' || chartType === 'line') {
                    hasData = data.datasets.some(dataset =>
                        dataset.data && dataset.data.length > 0 &&
                        dataset.data.some(value => value !== null && value !== undefined && !isNaN(value))
                    );
                } else if (chartType === 'pie' || chartType === 'doughnut') {
                    hasData = data.datasets[0]?.data?.some(value =>
                        value !== null && value !== undefined && !isNaN(value) && value > 0
                    );
                }
            }
        } catch (e) {
            console.error(`Error verificando datos para ${chartId}:`, e);
        }

        console.log(`[${chartId}] ¿Tiene datos?`, hasData);

        if (hasData) {
            canvas.style.display = 'block';
            if (noDataDiv) noDataDiv.classList.add('d-none');

            const existingChart = Chart.getChart(chartId);
            if (existingChart) existingChart.destroy();

            try {
                new Chart(canvas.getContext('2d'), {
                    type: chartType,
                    data: data,
                    options: options,
                    plugins: plugins
                });
                console.log(`[${chartId}] Gráfico creado exitosamente`);
            } catch (e) {
                console.error(`Error creando gráfico ${chartId}:`, e);
                canvas.style.display = 'none';
                if (noDataDiv) noDataDiv.classList.remove('d-none');
            }
        } else {
            console.log(`[${chartId}] No hay datos válidos para mostrar`);
            canvas.style.display = 'none';
            if (noDataDiv) noDataDiv.classList.remove('d-none');
            const existingChart = Chart.getChart(chartId);
            if (existingChart) existingChart.destroy();
        }
    }
    // Función para crear o actualizar gráfico
    function createOrUpdateChart(chartId, chartType, data, options, plugins = []) {
        const canvas = document.getElementById(chartId);
        const noDataDiv = document.getElementById(`noData${chartId.replace('Chart', '')}`);

        if (!canvas) {
            console.error(`Canvas element with ID '${chartId}' not found.`);
            return;
        }

        console.log(`[DEBUG - ${chartId}] - Data recibida:`, data);

        // Verificar si hay datos
        let hasData = false;
        if (data.labels && data.labels.length > 0) {
            if (chartType === 'bar' || chartType === 'line') {
                hasData = data.datasets.some(dataset =>
                    dataset.data && dataset.data.length > 0 && dataset.data.some(value => value > 0)
                );
            } else if (chartType === 'pie' || chartType === 'doughnut') {
                hasData = data.datasets[0] && data.datasets[0].data &&
                    data.datasets[0].data.length > 0 &&
                    data.datasets[0].data.some(value => value > 0);
            }
        }

        console.log(`[DEBUG - ${chartId}] - hasData evaluado como:`, hasData);

        if (hasData) {
            canvas.style.display = 'block';
            if (noDataDiv) noDataDiv.classList.add('d-none');

            // Destruir gráfico existente
            const existingChart = Chart.getChart(chartId);
            if (existingChart) {
                existingChart.destroy();
            }

            const ctx = canvas.getContext('2d');
            const newChart = new Chart(ctx, {
                type: chartType,
                data: data,
                options: options,
                plugins: plugins
            });

            console.log(`[DEBUG - ${chartId}] - Gráfico creado exitosamente.`);
        } else {
            canvas.style.display = 'none';
            if (noDataDiv) noDataDiv.classList.remove('d-none');

            // Destruir gráfico existente
            const existingChart = Chart.getChart(chartId);
            if (existingChart) {
                existingChart.destroy();
            }

            console.log(`[DEBUG - ${chartId}] - No hay datos, gráfico oculto.`);
        }
    }

    // --- Gráfica de Evolución ---
    function createEvolucionChart() {
        const evolucionData = {
            labels: datosGraficas.evolucion.labels || [],
            datasets: [
                {
                    label: 'Monto Total ($)',
                    data: datosGraficas.evolucion.montos || [],
                    backgroundColor: 'rgba(13, 110, 253, 0.7)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    borderWidth: 1,
                    yAxisID: 'y'
                },
                {
                    label: 'Pagos Completados',
                    data: datosGraficas.evolucion.completados || [],
                    backgroundColor: 'rgba(25, 135, 84, 0.7)',
                    borderColor: 'rgba(25, 135, 84, 1)',
                    borderWidth: 1,
                    type: 'line',
                    yAxisID: 'y1',
                    tension: 0.3
                }
            ]
        };

        const evolucionOptions = {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: 10,
                    cornerRadius: 4,
                    boxPadding: 4,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.dataset.yAxisID === 'y') {
                                label += '$' + context.parsed.y.toLocaleString();
                            } else {
                                label += context.parsed.y;
                            }
                            return label;
                        }
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                datalabels: {
                    display: false,
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Monto ($)',
                        font: {
                            size: 10
                        }
                    },
                    ticks: {
                        callback: function (value) {
                            return '$' + value.toLocaleString();
                        },
                        font: {
                            size: 10
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Cantidad de Pagos',
                        font: {
                            size: 10
                        }
                    },
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                x: {
                    type: 'category',
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                }
            }
        };

        createOrUpdateChart('evolucionChart', 'bar', evolucionData, evolucionOptions);
    }

    // --- Gráfica de Estados ---
    function createEstadosChart() {
        const estadosData = {
            labels: datosGraficas.estados.labels || [],
            datasets: [{
                data: datosGraficas.estados.data || [],
                backgroundColor: [
                    'rgba(25, 135, 84, 0.7)',    // Pagado (Success)
                    'rgba(255, 193, 7, 0.7)',    // Pendiente (Warning)
                    'rgba(220, 53, 69, 0.7)',    // Cancelado (Danger)
                    'rgba(13, 110, 253, 0.7)',   // Parcial (Primary/Info)
                    'rgba(108, 117, 125, 0.7)'   // Otro (Secondary)
                ],
                borderColor: [
                    'rgba(25, 135, 84, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(13, 110, 253, 1)',
                    'rgba(108, 117, 125, 1)'
                ],
                borderWidth: 1
            }]
        };

        const estadosOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: 10,
                    cornerRadius: 4,
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                datalabels: {
                    formatter: (value, ctx) => {
                        const dataArr = ctx.chart.data.datasets[0].data;
                        const sum = dataArr.reduce((a, b) => a + b, 0);
                        const percentage = sum > 0 ? (value * 100 / sum).toFixed(1) + '%' : '0%';
                        return percentage;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold',
                        size: 10
                    }
                }
            }
        };

        const plugins = typeof ChartDataLabels !== 'undefined' ? [ChartDataLabels] : [];
        createOrUpdateChart('estadosChart', 'doughnut', estadosData, estadosOptions, plugins);
    }

    // --- Gráfica de Métodos de Pago ---
    function createMetodosChart() {
        const metodosData = {
            labels: datosGraficas.metodos.labels || [],
            datasets: [{
                data: datosGraficas.metodos.data || [],
                backgroundColor: [
                    'rgba(13, 110, 253, 0.7)',    // Primary
                    'rgba(111, 66, 193, 0.7)',    // Indigo
                    'rgba(214, 51, 132, 0.7)',    // Pink
                    'rgba(253, 126, 20, 0.7)',    // Orange
                    'rgba(32, 201, 151, 0.7)',    // Teal
                    'rgba(20, 220, 200, 0.7)'     // Custom color
                ],
                borderColor: [
                    'rgba(13, 110, 253, 1)',
                    'rgba(111, 66, 193, 1)',
                    'rgba(214, 51, 132, 1)',
                    'rgba(253, 126, 20, 1)',
                    'rgba(32, 201, 151, 1)',
                    'rgba(20, 220, 200, 1)'
                ],
                borderWidth: 1
            }]
        };

        const metodosOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: 10,
                    cornerRadius: 4,
                    callbacks: {
                        label: function (context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                            return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                },
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                },
                datalabels: {
                    formatter: (value, ctx) => {
                        const dataArr = ctx.chart.data.datasets[0].data;
                        const sum = dataArr.reduce((a, b) => a + b, 0);
                        const percentage = sum > 0 ? (value * 100 / sum).toFixed(1) + '%' : '0%';
                        return percentage;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold',
                        size: 10
                    }
                }
            }
        };

        const plugins = typeof ChartDataLabels !== 'undefined' ? [ChartDataLabels] : [];
        createOrUpdateChart('metodosChart', 'pie', metodosData, metodosOptions, plugins);
    }

    // Crear todas las gráficas
    createEvolucionChart();
    createEstadosChart();
    createMetodosChart();

    // Manejar los botones de período para cambiar el filtro
    document.querySelectorAll('.periodo-btn').forEach(button => {
        button.addEventListener('click', function () {
            const periodo = this.dataset.periodo;
            const url = new URL(window.location.href);
            url.searchParams.set('periodo', periodo);
            window.location.href = url.toString();
        });
    });
});