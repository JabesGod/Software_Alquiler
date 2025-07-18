document.addEventListener('DOMContentLoaded', function() {
    initEstadoEquiposChart();
});

function initEstadoEquiposChart() {
    const ctx = document.getElementById('estadoEquiposChart');
    
    if (!ctx) {
        console.log('No se encontró el elemento estadoEquiposChart');
        return;
    }
    
    try {
        // Obtener los datos de los atributos data-*
        const labels = JSON.parse(`[${ctx.getAttribute('data-labels')}]`);
        const data = JSON.parse(`[${ctx.getAttribute('data-values')}]`);
        const colors = JSON.parse(`[${ctx.getAttribute('data-colors')}]`);
        
        const chartData = {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 1,
                hoverOffset: 10,
                hoverBorderColor: '#fff'
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