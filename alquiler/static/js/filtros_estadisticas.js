// filtros_estadisticas.js - Manejo avanzado de filtros

document.addEventListener('DOMContentLoaded', function() {
    // Manejar cambios en los filtros
    const formFiltros = document.querySelector('.form-filtros');
    if (formFiltros) {
        // Puedes agregar lógica adicional para manejar cambios en los filtros
        // Por ejemplo, validaciones o actualizaciones en tiempo real
        
        formFiltros.addEventListener('submit', function(e) {
            // Validación adicional si es necesaria
            const fechaInicio = document.getElementById('rango-fechas').dataset.startDate;
            const fechaFin = document.getElementById('rango-fechas').dataset.endDate;
            
            if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
                e.preventDefault();
                alert('La fecha de inicio no puede ser mayor a la fecha de fin');
                return false;
            }
            
            // Mostrar loader mientras se cargan los datos
            mostrarLoader();
        });
    }
    
    function mostrarLoader() {
        const loader = document.createElement('div');
        loader.className = 'loader-overlay';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p>Procesando datos...</p>
            </div>
        `;
        document.body.appendChild(loader);
        
        // Ocultar loader cuando la página termine de cargar
        window.addEventListener('load', function() {
            if (loader) loader.remove();
        });
    }
});