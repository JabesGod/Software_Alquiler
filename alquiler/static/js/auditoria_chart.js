// auditoria.js

document.addEventListener('DOMContentLoaded', function() {
    // Solo intentar cargar el gráfico si existe el canvas y hay datos
    const chartCanvas = document.getElementById('accesosChart');
    const chartDataElement = document.getElementById('chart-data');
    
    if (chartCanvas && chartDataElement) {
        const statsData = JSON.parse(chartDataElement.textContent);
        
        if (statsData && statsData.months && statsData.months.length > 0) {
            renderChart(statsData);
        }
    }
});

function renderChart(statsData) {
    const ctx = document.getElementById('accesosChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: statsData.months,
            datasets: [
                {
                    label: 'Accesos exitosos',
                    backgroundColor: '#28a745',
                    data: statsData.success
                },
                {
                    label: 'Intentos fallidos',
                    backgroundColor: '#dc3545',
                    data: statsData.failed
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw;
                        }
                    }
                }
            }
        }
    });
}