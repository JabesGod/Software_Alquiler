// auditoria.js - Versión simplificada para debugging

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado');
    
    // Verificar si Chart.js está disponible
    if (typeof Chart === 'undefined') {
        console.error('Chart.js no está disponible');
        return;
    }
    
    console.log('Chart.js está disponible');
    
    // Buscar el canvas
    const canvas = document.getElementById('accesosChart');
    if (!canvas) {
        console.error('Canvas no encontrado');
        return;
    }
    
    console.log('Canvas encontrado');
    
    // Buscar el script con los datos
    const dataScript = document.getElementById('chart-data');
    if (!dataScript) {
        console.error('Script con datos no encontrado');
        return;
    }
    
    console.log('Script de datos encontrado');
    
    try {
        // Parsear los datos
        const statsData = JSON.parse(dataScript.textContent);
        console.log('Datos parseados:', statsData);
        
        // Verificar que los datos son válidos
        if (!statsData || !statsData.months || !statsData.success || !statsData.failed) {
            console.error('Datos inválidos:', statsData);
            return;
        }
        
        console.log('Datos válidos, creando gráfico...');
        
        // Crear el gráfico
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
        
        console.log('Gráfico creado exitosamente');
        
    } catch (error) {
        console.error('Error al crear el gráfico:', error);
    }
});