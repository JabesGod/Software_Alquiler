// dashboard.js - Enhanced with error handling
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts only if elements exist
    initEstadoEquiposChart();
    // Add other chart initializations here if needed
});

function initEstadoEquiposChart() {
    const ctx = document.getElementById('estadoEquiposChart');
    
    if (!ctx) {
        console.log('No se encontró el elemento estadoEquiposChart');
        return;
    }
    
    try {
        const chartData = {
            labels: JSON.parse(ctx.getAttribute('data-labels') || [],
            datasets: [{
                data: JSON.parse(ctx.getAttribute('data-values')) || [],
                backgroundColor: JSON.parse(ctx.getAttribute('data-colors')) || [],
                borderWidth: 1,
                hoverOffset: 10
            }]
        };
        
        new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                cutout: '70%',
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    } catch (error) {
        console.error('Error al inicializar el gráfico:', error);
    }
}