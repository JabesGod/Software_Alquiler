document.addEventListener('DOMContentLoaded', function() {
    // Efectos de hover para los items de resultado
    const resultItems = document.querySelectorAll('.result-item');
    
    resultItems.forEach(item => {
        // Efecto de escala al hacer hover
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.zIndex = '10';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.zIndex = '';
        });
        
        // Click en toda la tarjeta
        item.addEventListener('click', function(e) {
            // Si el click no fue en un enlace interno
            if (!e.target.closest('a') && !e.target.closest('button')) {
                const link = this.querySelector('h3 a');
                if (link) {
                    window.location.href = link.href;
                }
            }
        });
    });
    
    // Mejorar la accesibilidad del teclado
    resultItems.forEach(item => {
        item.setAttribute('tabindex', '0');
        item.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const link = this.querySelector('h3 a');
                if (link) {
                    window.location.href = link.href;
                }
            }
        });
    });
    
    // Animación de carga inicial
    setTimeout(() => {
        document.querySelector('.search-results-container').style.opacity = '1';
    }, 100);
});

// Opcional: Integración con la API de búsqueda para sugerencias en vivo
function setupLiveSearch() {
    const searchInput = document.querySelector('.search-form input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Implementar lógica de búsqueda en vivo aquí
        });
    }
}