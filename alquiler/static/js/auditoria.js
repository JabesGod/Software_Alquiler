document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        return;
    }
    
    const canvas = document.getElementById('accesosChart');
    if (!canvas) {
        return;
    }
    
    const dataScript = document.getElementById('chart-data');
    if (!dataScript) {
        return;
    }
    
    try {
        const statsData = JSON.parse(dataScript.textContent);
        
        if (!statsData || !statsData.months || !statsData.success || !statsData.failed) {
            return;
        }
        
        const ctx = canvas.getContext('2d');
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
                }
            }
        });
    } catch (error) {
        console.error('Error al crear el gráfico:', error);
    }
});