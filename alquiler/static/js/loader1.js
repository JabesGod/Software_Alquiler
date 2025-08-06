function createParticles() {
    const particlesContainer = document.querySelector('.particles');
    if (particlesContainer) {
        particlesContainer.innerHTML = '';
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
}

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
        if (messageIndex < messages.length && loadingText) {
            loadingText.innerHTML = messages[messageIndex] + '<span class="loading-dots"></span>';
            messageIndex++;
        } else {
            clearInterval(messageInterval);
        }
    }, 600);
    return messageInterval;
}

function hideLoader() {
    const loaderContainer = document.getElementById('loader-container');
    const appContainer = document.querySelector('.app-container');
    
    if (loaderContainer) {
        loaderContainer.classList.add('loader-hidden');
        if (appContainer) {
            appContainer.style.opacity = '1';
            appContainer.style.visibility = 'visible';
        }
        setTimeout(() => {
            if (loaderContainer && loaderContainer.parentNode) {
                loaderContainer.parentNode.removeChild(loaderContainer);
            }
        }, 800);
    }
}

const powerButtonInterval = setInterval(() => {
    const powerButton = document.querySelector('.power-button');
    if (powerButton) {
        const colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#3498db'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        powerButton.style.background = randomColor;
        powerButton.style.boxShadow = `0 0 8px ${randomColor}`;
    } else {
        clearInterval(powerButtonInterval);
    }
}, 1500);

document.addEventListener('DOMContentLoaded', function() {
    const loaderContainer = document.getElementById('loader-container');
    const appContainer = document.querySelector('.app-container');
    const loadingText = document.querySelector('.loading-text');

    if (appContainer) {
        appContainer.style.opacity = '0';
        appContainer.style.visibility = 'hidden';
        appContainer.style.transition = 'opacity 0.8s ease-in-out, visibility 0.8s ease-in-out';
    }

    if (!loaderContainer) {
        if (appContainer) {
            appContainer.style.opacity = '1';
            appContainer.style.visibility = 'visible';
        }
        return;
    }

    createParticles();
    const loadingInterval = simulateLoading();

    let extraWaitTime = 0; 
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;

    if (connection && connection.effectiveType) {
        switch (connection.effectiveType) {
            case '4g':
                extraWaitTime = 0; 
                if (loadingText) loadingText.innerHTML = "Cargando rápido gracias a tu conexión 🚀 <span class='loading-dots'></span>";
                break;
            case '3g':
                extraWaitTime = 1000; 
                break;
            case '2g':
            case 'slow-2g':
                extraWaitTime = 3000;
                if (loadingText) loadingText.innerHTML = "Conexión lenta detectada... optimizando carga <span class='loading-dots'></span>";
                break;
            default:
                extraWaitTime = 500; 
        }
        console.log(`Tipo de conexión: ${connection.effectiveType}. Tiempo de espera adicional: ${extraWaitTime / 1000}s`);
    } else {
        extraWaitTime = 0;
        console.log("No se pudo detectar el tipo de conexión. Ocultando el loader tan pronto como sea posible.");
    }

    Promise.all([
        new Promise(resolve => setTimeout(resolve, extraWaitTime)),
        new Promise(resolve => window.addEventListener('load', resolve))
    ]).then(() => {
        clearInterval(loadingInterval);
        clearInterval(powerButtonInterval);
        hideLoader();
    });

    setTimeout(() => {
        clearInterval(loadingInterval);
        clearInterval(powerButtonInterval);
        hideLoader();
    }, 6000);
});