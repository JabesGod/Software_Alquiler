document.addEventListener('DOMContentLoaded', function() {
    // Obtener los datos del canvas
    const canvas = document.getElementById('grafico');
    
    if (!canvas) {
        console.error('No se encontró el elemento canvas');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Obtener los datos pasados desde Django
    // Ya no es necesario parsearlo pues ya vienen en formato JSON desde Django
    try {
        const labels = JSON.parse(canvas.dataset.labels || '[]');
        const datos = JSON.parse(canvas.dataset.datos || '[]');
        
        console.log('Labels:', labels);
        console.log('Datos:', datos);
        
        // Verificar si hay datos para mostrar
        if (labels.length === 0 || datos.length === 0) {
            canvas.style.display = 'none';
            const mensaje = document.createElement('p');
            mensaje.textContent = 'No hay suficientes datos para mostrar el gráfico.';
            mensaje.style.textAlign = 'center';
            mensaje.style.marginTop = '20px';
            mensaje.style.color = 'var(--error-color)';
            canvas.parentNode.insertBefore(mensaje, canvas.nextSibling);
            return;
        }
        
        // Crear el gráfico
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Número de alquileres',
                    data: datos,
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.7)',
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(155, 89, 182, 0.7)',
                        'rgba(52, 73, 94, 0.7)',
                        'rgba(241, 196, 15, 0.7)',
                        'rgba(230, 126, 34, 0.7)',
                        'rgba(231, 76, 60, 0.7)',
                        'rgba(26, 188, 156, 0.7)',
                        'rgba(41, 128, 185, 0.7)',
                        'rgba(142, 68, 173, 0.7)'
                    ],
                    borderColor: [
                        'rgba(52, 152, 219, 1)',
                        'rgba(46, 204, 113, 1)',
                        'rgba(155, 89, 182, 1)',
                        'rgba(52, 73, 94, 1)',
                        'rgba(241, 196, 15, 1)',
                        'rgba(230, 126, 34, 1)',
                        'rgba(231, 76, 60, 1)',
                        'rgba(26, 188, 156, 1)',
                        'rgba(41, 128, 185, 1)',
                        'rgba(142, 68, 173, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de alquileres',
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Equipos',
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Alquileres: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error al procesar los datos del gráfico:', error);
        canvas.style.display = 'none';
        const mensaje = document.createElement('p');
        mensaje.textContent = 'Error al procesar los datos del gráfico.';
        mensaje.style.textAlign = 'center';
        mensaje.style.marginTop = '20px';
        mensaje.style.color = 'var(--error-color)';
        canvas.parentNode.insertBefore(mensaje, canvas.nextSibling);
    }
});