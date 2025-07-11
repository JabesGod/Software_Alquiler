document.addEventListener("DOMContentLoaded", function() {
    // Verificar si los datos del gráfico están disponibles antes de intentar renderizar
    // Estos datos se inyectarán globalmente o a través de un elemento HTML, como veremos.
    if (typeof statsDataMonths !== 'undefined' && statsDataMonths.length > 0) {
        var ctx = document.getElementById('accesosChart');
        if (ctx) {
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: statsDataMonths,
                    datasets: [
                        {
                            label: 'Accesos exitosos',
                            backgroundColor: '#28a745',
                            data: statsDataSuccess,
                            borderWidth: 1
                        },
                        {
                            label: 'Intentos fallidos',
                            backgroundColor: '#dc3545',
                            data: statsDataFailed,
                            borderWidth: 1
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
                                precision: 0,
                                stepSize: 1
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
    }
});