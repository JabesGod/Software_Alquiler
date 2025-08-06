
document.addEventListener('DOMContentLoaded', function() {
    const commonChartConfig = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        size: 12,
                        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                    },
                    padding: 20,
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleFont: {
                    size: 14,
                    weight: 'bold'
                },
                bodyFont: {
                    size: 12
                },
                padding: 12,
                cornerRadius: 6,
                displayColors: true,
                callbacks: {
                    labelColor: function(context) {
                        return {
                            borderColor: 'transparent',
                            backgroundColor: context.dataset.backgroundColor,
                            borderRadius: 4
                        };
                    }
                }
            },
            datalabels: {
                display: false
            }
        },
        layout: {
            padding: {
                top: 20,
                right: 20,
                bottom: 20,
                left: 20
            }
        },
        elements: {
            bar: {
                borderRadius: 6,
                borderSkipped: false
            }
        }
    };

    const chartColors = {
        blue: {
            bg: 'rgba(52, 152, 219, 0.7)',
            border: 'rgba(52, 152, 219, 1)'
        },
        green: {
            bg: 'rgba(46, 204, 113, 0.7)',
            border: 'rgba(46, 204, 113, 1)'
        },
        purple: {
            bg: 'rgba(155, 89, 182, 0.7)',
            border: 'rgba(155, 89, 182, 1)'
        },
        yellow: {
            bg: 'rgba(241, 196, 15, 0.7)',
            border: 'rgba(241, 196, 15, 1)'
        }
    };

    const isMonthlyView = document.body.classList.contains('vista-mensual');

    if (isMonthlyView) {
        initMonthlyCharts();
    } else {
        initEquipmentCharts();
    }

    function initEquipmentCharts() {
        initChart(
            'grafico', 
            'bar', 
            'Número de alquileres', 
            chartColors.blue,
            {
                y: {
                    title: {
                        display: true,
                        text: 'Número de alquileres',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    },
                    ticks: {
                        precision: 0,
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Equipos',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    },
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        );

        initChart(
            'graficoIngresos', 
            'bar', 
            'Ingresos ($)', 
            chartColors.green,
            {
                y: {
                    title: {
                        display: true,
                        text: 'Ingresos ($)',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Equipos',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    },
                    ticks: {
                        autoSkip: false,
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            function(context) {
                return `${context.dataset.label}: $${context.raw.toLocaleString()}`;
            }
        );
    }

    
    function initMonthlyCharts() {
        initChart(
            'grafico', 
            'line', 
            'Alquileres', 
            chartColors.blue,
            {
                y: {
                    title: {
                        display: true,
                        text: 'Número de alquileres',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    },
                    ticks: {
                        precision: 0,
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Mes',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    }
                }
            }
        );

        initChart(
            'graficoIngresos', 
            'line', 
            'Ingresos ($)', 
            chartColors.green,
            {
                y: {
                    title: {
                        display: true,
                        text: 'Ingresos ($)',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Mes',
                        font: { 
                            weight: 'bold',
                            size: 14
                        }
                    }
                }
            },
            function(context) {
                return `${context.dataset.label}: $${context.raw.toLocaleString()}`;
            }
        );
    }

    function initChart(canvasId, chartType, datasetLabel, colors, scalesConfig, customTooltipCallback) {
        const canvas = document.getElementById(canvasId);
        
        if (!canvas) {
            console.error(`No se encontró el canvas con ID: ${canvasId}`);
            return;
        }
        
        const ctx = canvas.getContext('2d');
        
        try {
            const labels = JSON.parse(canvas.dataset.labels || '[]');
            const data = JSON.parse(canvas.dataset.datos || '[]');
            
            if (labels.length === 0 || data.length === 0) {
                showNoDataMessage(canvas);
                return;
            }
            
            const chartOptions = {
                ...commonChartConfig,
                scales: scalesConfig,
                plugins: {
                    ...commonChartConfig.plugins,
                    tooltip: {
                        ...commonChartConfig.plugins.tooltip,
                        callbacks: {
                            ...commonChartConfig.plugins.tooltip.callbacks,
                            label: customTooltipCallback || function(context) {
                                return `${context.dataset.label}: ${context.raw}`;
                            }
                        }
                    }
                }
            };
            
            new Chart(ctx, {
                type: chartType,
                data: {
                    labels: labels,
                    datasets: [{
                        label: datasetLabel,
                        data: data,
                        backgroundColor: colors.bg,
                        borderColor: colors.border,
                        borderWidth: 2,
                        hoverBackgroundColor: colors.bg.replace('0.7', '0.9'),
                        hoverBorderColor: colors.border,
                        hoverBorderWidth: 3,
                        fill: chartType === 'line' ? false : undefined,
                        tension: chartType === 'line' ? 0.1 : undefined
                    }]
                },
                options: chartOptions
            });
            
        } catch (error) {
            handleChartError(canvas, error);
        }
    }

    function showNoDataMessage(canvas) {
        canvas.style.display = 'none';
        
        const messageContainer = document.createElement('div');
        messageContainer.className = 'no-data-message';
        messageContainer.style.textAlign = 'center';
        messageContainer.style.padding = '20px';
        messageContainer.style.backgroundColor = '#f8f9fa';
        messageContainer.style.borderRadius = '8px';
        messageContainer.style.marginTop = '20px';
        messageContainer.style.border = '1px dashed #dee2e6';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-chart-pie';
        icon.style.fontSize = '2rem';
        icon.style.color = '#6c757d';
        icon.style.marginBottom = '10px';
        
        const message = document.createElement('p');
        message.textContent = 'No hay suficientes datos para mostrar el gráfico.';
        message.style.color = '#6c757d';
        message.style.margin = '0';
        message.style.fontSize = '1rem';
        
        messageContainer.appendChild(icon);
        messageContainer.appendChild(message);
        
        canvas.parentNode.insertBefore(messageContainer, canvas.nextSibling);
    }

    function handleChartError(canvas, error) {
        console.error(`Error en el gráfico ${canvas.id}:`, error);
        canvas.style.display = 'none';
        
        const errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';
        errorContainer.style.textAlign = 'center';
        errorContainer.style.padding = '20px';
        errorContainer.style.backgroundColor = '#f8d7da';
        errorContainer.style.borderRadius = '8px';
        errorContainer.style.marginTop = '20px';
        errorContainer.style.border = '1px solid #f5c6cb';
        
        const icon = document.createElement('i');
        icon.className = 'fas fa-exclamation-triangle';
        icon.style.fontSize = '2rem';
        icon.style.color = '#721c24';
        icon.style.marginBottom = '10px';
        
        const message = document.createElement('p');
        message.textContent = 'Error al cargar los datos del gráfico.';
        message.style.color = '#721c24';
        message.style.margin = '0';
        message.style.fontSize = '1rem';
        
        const detail = document.createElement('small');
        detail.textContent = 'Por favor, intente recargar la página.';
        detail.style.display = 'block';
        detail.style.marginTop = '5px';
        detail.style.color = '#721c24';
        detail.style.opacity = '0.8';
        
        errorContainer.appendChild(icon);
        errorContainer.appendChild(message);
        errorContainer.appendChild(detail);
        
        canvas.parentNode.insertBefore(errorContainer, canvas.nextSibling);
    }

    window.addEventListener('resize', function() {
        Chart.helpers.each(Chart.instances, function(instance) {
            instance.resize();
        });
    });
});