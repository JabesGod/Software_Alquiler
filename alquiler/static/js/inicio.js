document.addEventListener('DOMContentLoaded', function() {
    const panels = document.querySelectorAll('.panel-item');
    
    panels.forEach(panel => {
        panel.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
        
        panel.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });
    
    setTimeout(() => {
        document.querySelector('.inicio-container').style.opacity = '1';
    }, 100);
});

let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', e => {
    touchStartX = e.changedTouches[0].screenX;
}, false);

document.addEventListener('touchend', e => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
}, false); 

function handleSwipe() {
    if (touchEndX < touchStartX) {
        console.log('Swiped left');
    }
    if (touchEndX > touchStartX) {
        console.log('Swiped right');
    }
}

