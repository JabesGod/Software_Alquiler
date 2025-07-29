document.addEventListener('DOMContentLoaded', function() {
    // Filtrado por tipo
    const filterButtons = document.querySelectorAll('.filter-btn');
    const resultCards = document.querySelectorAll('.result-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.dataset.filter;
            
            // Actualizar botones activos
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Mostrar/ocultar resultados
            resultCards.forEach(card => {
                if (filter === 'todos' || card.dataset.type === filter) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // Animación al cargar
    const cards = document.querySelectorAll('.result-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });

    // Manejar clics en las tarjetas (redundante pero seguro)
    document.querySelectorAll('.result-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Permitir clics en enlaces internos
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            window.location.href = this.getAttribute('onclick').match(/window\.location\.href='(.*?)'/)[1];
        });
    });
});