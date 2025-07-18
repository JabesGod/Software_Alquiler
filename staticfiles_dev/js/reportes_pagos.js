
const datosGraficas = JSON.parse('{{ datos_graficas|escapejs }}');

// Registrar el plugin de datalabels globalmente
Chart.register(ChartDataLabels);

// Configuración común para gráficas
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#6c757d';

// Función para inicializar o destruir un gráfico
function createOrUpdateChart(chartId, chartType, data, options, plugins = []) {
    const canvas = document.getElementById(chartId);
    const noDataDiv = document.getElementById(`noData${chartId.replace('Chart', '')}`);

    if (!canvas) {
        console.error(`Canvas element with ID '${chartId}' not found.`);
        return;
    }

    // Verificar si hay datos para el gráfico
    const hasData = data.labels && data.labels.length > 0 && data.datasets[0] && data.datasets[0].data && data.datasets[0].data.some(val => val > 0);

    if (hasData) {
        canvas.style.display = 'block';
        if (noDataDiv) noDataDiv.classList.add('d-none');

        // Si ya existe un Chart.js en este canvas, destrúyelo primero
        if (Chart.getChart(chartId)) {
            Chart.getChart(chartId).destroy();
        }

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: chartType,
            data: data,
            options: options,
            plugins: plugins
        });
    } else {
        canvas.style.display = 'none';
        if (noDataDiv) noDataDiv.classList.remove('d-none'); // Mostrar mensaje de no data
        // Destruir el gráfico si existía y ahora no hay datos
        if (Chart.getChart(chartId)) {
            Chart.getChart(chartId).destroy();
        }
    }
}


// --- Gráfica de Evolución ---
const evolucionData = {
    labels: datosGraficas.evolucion.labels,
    datasets: [
        {
            label: 'Monto Total ($)',
            data: datosGraficas.evolucion.montos,
            backgroundColor: 'rgba(13, 110, 253, 0.7)',
            borderColor: 'rgba(13, 110, 253, 1)',
            borderWidth: 1,
            yAxisID: 'y'
        },
        {
            label: 'Pagos Completados',
            data: datosGraficas.evolucion.completados,
            backgroundColor: 'rgba(25, 135, 84, 0.7)',
            borderColor: 'rgba(25, 135, 84, 1)',
            borderWidth: 1,
            type: 'line',
            yAxisID: 'y1',
            tension: 0.3 // Suavizar la línea
        }
    ]
};
const evolucionOptions = {
    responsive: true,
    maintainAspectRatio: false, // Permite que height funcione mejor
    interaction: {
        mode: 'index',
        intersect: false,
    },
    plugins: {
        tooltip: {
            callbacks: {
                label: function(context) {
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
        },
        datalabels: { // Ocultar datalabels por defecto en gráfica de línea/barra a menos que sea necesario
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
                text: 'Monto ($)'
            },
            ticks: {
                callback: function(value) {
                    return '$' + value.toLocaleString();
                }
            }
        },
        y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
                display: true,
                text: 'Cantidad de Pagos'
            },
            grid: {
                drawOnChartArea: false
            }
        },
        x: {
            // Configuración del eje X para asegurar que Moment.js lo formatee
            type: 'category', // O 'time' si los labels son objetos Date/Moment
            labels: datosGraficas.evolucion.labels // Si los labels ya son strings formateados
        }
    }
};
createOrUpdateChart('evolucionChart', 'bar', evolucionData, evolucionOptions);


// --- Gráfica de Estados ---
const estadosData = {
    labels: datosGraficas.estados.labels,
    datasets: [{
        data: datosGraficas.estados.data,
        backgroundColor: [
            'rgba(25, 135, 84, 0.7)',   // Pagado (Success)
            'rgba(255, 193, 7, 0.7)',   // Pendiente (Warning)
            'rgba(220, 53, 69, 0.7)',   // Cancelado (Danger)
            'rgba(13, 110, 253, 0.7)',  // Parcial (Primary/Info) - Asegúrate que este orden coincida con tus estados
            'rgba(108, 117, 125, 0.7)'  // Otro (Secondary)
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
        legend: {
            position: 'right',
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    const label = context.label || '';
                    const value = context.raw || 0;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                    return `${label}: $${value.toLocaleString()} (${percentage}%)`;
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
                weight: 'bold'
            }
        }
    }
};
createOrUpdateChart('estadosChart', 'doughnut', estadosData, estadosOptions, [ChartDataLabels]);


// --- Gráfica de Métodos de Pago ---
const metodosData = {
    labels: datosGraficas.metodos.labels,
    datasets: [{
        data: datosGraficas.metodos.data,
        backgroundColor: [
            'rgba(13, 110, 253, 0.7)',   // Primary
            'rgba(111, 66, 193, 0.7)',  // Indigo
            'rgba(214, 51, 132, 0.7)',  // Pink
            'rgba(253, 126, 20, 0.7)',  // Orange
            'rgba(32, 201, 151, 0.7)',  // Teal
            'rgba(20, 220, 200, 0.7)'   // Custom color if needed
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
        legend: {
            position: 'right',
        },
        tooltip: {
            callbacks: {
                label: function(context) {
                    const label = context.label || '';
                    const value = context.raw || 0;
                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                    return `${label}: $${value.toLocaleString()} (${percentage}%)`;
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
                weight: 'bold'
            }
        }
    }
};
createOrUpdateChart('metodosChart', 'pie', metodosData, metodosOptions, [ChartDataLabels]);


// Manejar los botones de período para cambiar el filtro
document.querySelectorAll('.periodo-btn').forEach(button => {
    button.addEventListener('click', function() {
        const periodo = this.dataset.periodo;
        const url = new URL(window.location.href);
        url.searchParams.set('periodo', periodo);
        window.location.href = url.toString();
    });
});

