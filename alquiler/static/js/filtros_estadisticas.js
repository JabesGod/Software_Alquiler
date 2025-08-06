
document.addEventListener('DOMContentLoaded', function() {
  
    const formFiltros = document.querySelector('.form-filtros');
    if (formFiltros) {
   
        
        formFiltros.addEventListener('submit', function(e) {
      
            const fechaInicio = document.getElementById('rango-fechas').dataset.startDate;
            const fechaFin = document.getElementById('rango-fechas').dataset.endDate;
            
            if (fechaInicio && fechaFin && fechaInicio > fechaFin) {
                e.preventDefault();
                alert('La fecha de inicio no puede ser mayor a la fecha de fin');
                return false;
            }
            
       
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
        

        window.addEventListener('load', function() {
            if (loader) loader.remove();
        });
    }
});