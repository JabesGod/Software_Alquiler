function createParticles() {
    const particlesContainer = document.querySelector('.particles');

    for (let i = 0; i < 8; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 2 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Simulador de progreso de carga más realista
function simulateLoading() {
    const loadingText = document.querySelector('.loading-text');
    const messages = [
        'Iniciando sistema...',
        'Cargando componentes...',
        'Estableciendo conexiones...',
        'Procesando datos...',
        'Finalizando...'
    ];

    let messageIndex = 0;
    const messageInterval = setInterval(() => {
        if (messageIndex < messages.length) {
            loadingText.innerHTML = messages[messageIndex] + '<span class="loading-dots"></span>';
            messageIndex++;
        } else {
            clearInterval(messageInterval);
        }
    }, 800);
}

// Cuando la página se carga completamente
window.addEventListener('load', function () {
    const loaderContainer = document.getElementById('loader-container');
    const pageContent = document.getElementById('page-content');

    // Crear partículas adicionales
    createParticles();

    // Simular proceso de carga
    simulateLoading();

    // Tiempo mínimo de visualización del loader (3 segundos para apreciar la animación)
    setTimeout(() => {
        // Oculta la pantalla de carga
        loaderContainer.classList.add('loader-hidden');

        // Muestra el contenido después de la transición
        setTimeout(() => {
            pageContent.style.opacity = '1';
            // Eliminar el loader del DOM para optimizar
            loaderContainer.remove();
        }, 800);
    }, 3000); // 3 segundos de duración mínima
});

// Efecto adicional: cambiar color del botón de encendido
setInterval(() => {
    const powerButton = document.querySelector('.power-button');
    if (powerButton) {
        const colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        powerButton.style.background = randomColor;
        powerButton.style.boxShadow = `0 0 8px ${randomColor}`;
    }
}, 2000);