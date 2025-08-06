document.addEventListener('DOMContentLoaded', function() {
    const initImageGallery = () => {
        const thumbnails = document.querySelectorAll('.thumbnail-img');
        const mainImg = document.getElementById('mainEquipoImage');
        
        if (thumbnails.length > 0 && mainImg) {
            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    thumbnails.forEach(t => t.classList.remove('active'));
                    
                    this.classList.add('active');
                    
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
            
            const updateButtonVisibility = () => {
                const { scrollLeft, scrollWidth, clientWidth } = similaresScroller;
                
                leftBtn.style.display = scrollLeft > 0 ? 'flex' : 'none';
                rightBtn.style.display = scrollLeft < scrollWidth - clientWidth ? 'flex' : 'none';
            };
            
            similaresScroller.addEventListener('scroll', updateButtonVisibility);
            window.addEventListener('resize', updateButtonVisibility);
            updateButtonVisibility(); 
        }
    };

    const handleImageErrors = () => {
        const images = document.querySelectorAll('.equipo-imagen, .quick-view-img, .main-img, .equipo-similar img');
        images.forEach(img => {
            img.addEventListener('error', function() {
                this.onerror = null;
                this.src = '/alquiler/static/img/default-equipo.png';
                this.style.objectFit = 'contain';
                this.style.padding = '1rem';
                this.style.backgroundColor = '#f8f9fa';
            });
        });
    };

    initImageGallery();
    initSimilarEquipmentCarousel();
    handleImageErrors();
});