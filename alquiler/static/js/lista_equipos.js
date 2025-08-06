document.addEventListener('DOMContentLoaded', function() {
    const quickViewButtons = document.querySelectorAll('.quick-view-btn');
    const closeButtons = document.querySelectorAll('.close-quick-view, .close-quick-view-btn');
    
    quickViewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const equipoId = this.getAttribute('data-equipo-id');
            const modal = document.getElementById(`quickViewModal-${equipoId}`);
            if (modal) {
                modal.style.display = 'block';
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modals = document.querySelectorAll('.quick-view-modal');
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
            document.body.style.overflow = 'auto';
        });
    });
    
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('quick-view-modal')) {
            event.target.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
    
    const equipoCards = document.querySelectorAll('.equipo-card');
    equipoCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
        });
    });
    
    const images = document.querySelectorAll('.equipo-imagen, .quick-view-img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.onerror = null;
            this.src = '/alquiler/static/img/default-equipo.png';
            this.style.objectFit = 'contain';
            this.style.padding = '1rem';
            this.style.backgroundColor = '#f8f9fa';
        });
    });
});

