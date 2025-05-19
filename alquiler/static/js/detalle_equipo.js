document.addEventListener('DOMContentLoaded', function() {
    // Galería de imágenes del equipo principal
    const initImageGallery = () => {
        const thumbnails = document.querySelectorAll('.thumbnail-img');
        const mainImg = document.getElementById('mainEquipoImage');
        
        if (thumbnails.length > 0 && mainImg) {
            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    // Remover clase active de todas las miniaturas
                    thumbnails.forEach(t => t.classList.remove('active'));
                    
                    // Añadir clase active a la miniatura clickeada
                    this.classList.add('active');
                    
                    // Cambiar imagen principal con efecto fade
                    const newSrc = this.getAttribute('data-full-img');
                    mainImg.style.opacity = 0;
                    
                    setTimeout(() => {
                        mainImg.src = newSrc;
                        mainImg.style.opacity = 1;
                    }, 200);
                });
            });
        }
    };

    // Carrusel de equipos similares
    const initSimilarEquipmentCarousel = () => {
        const similaresScroller = document.querySelector('.similares-scroller');
        const leftBtn = document.querySelector('.left-btn');
        const rightBtn = document.querySelector('.right-btn');
        
        if (similaresScroller && leftBtn && rightBtn) {
            const scrollAmount = 300;
            
            leftBtn.addEventListener('click', () => {
                similaresScroller.scrollBy({
                    left: -scrollAmount,
                    behavior: 'smooth'
                });
            });
            
            rightBtn.addEventListener('click', () => {
                similaresScroller.scrollBy({
                    left: scrollAmount,
                    behavior: 'smooth'
                });
            });
            
            // Ocultar/mostrar botones según posición del scroll
            const updateButtonVisibility = () => {
                const { scrollLeft, scrollWidth, clientWidth } = similaresScroller;
                
                leftBtn.style.display = scrollLeft > 0 ? 'flex' : 'none';
                rightBtn.style.display = scrollLeft < scrollWidth - clientWidth ? 'flex' : 'none';
            };
            
            similaresScroller.addEventListener('scroll', updateButtonVisibility);
            window.addEventListener('resize', updateButtonVisibility);
            updateButtonVisibility(); // Estado inicial
        }
    };

    // Manejo de errores en imágenes
    const handleImageErrors = () => {
        const images = document.querySelectorAll('.equipo-imagen, .quick-view-img, .main-img, .equipo-similar img');
        images.forEach(img => {
            img.addEventListener('error', function() {
                this.onerror = null;
                this.src = '/static/img/default-equipo.png';
                this.style.objectFit = 'contain';
                this.style.padding = '1rem';
                this.style.backgroundColor = '#f8f9fa';
            });
        });
    };

    // Inicializar todos los componentes
    initImageGallery();
    initSimilarEquipmentCarousel();
    handleImageErrors();
});