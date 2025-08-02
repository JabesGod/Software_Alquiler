function createParticles() {
    const particlesContainer = document.querySelector('.particles');
    
    // Limpiar partículas existentes primero
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
        if (messageIndex < messages.length && loadingText) {
            loadingText.innerHTML = messages[messageIndex] + '<span class="loading-dots"></span>';
            messageIndex++;
        } else {
            clearInterval(messageInterval);
        }
    }, 600); // Reducido a 600ms para que sea más rápido

    return messageInterval;
}

// Función para ocultar el loader
function hideLoader() {
    const loaderContainer = document.getElementById('loader-container');
    const appContainer = document.querySelector('.app-container');
    
    if (loaderContainer) {
        // Añadir clase para ocultar con animación
        loaderContainer.classList.add('loader-hidden');
        
        // Mostrar el contenido principal
        if (appContainer) {
            appContainer.style.opacity = '1';
            appContainer.style.visibility = 'visible';
        }
        
        // Eliminar el loader del DOM después de la animación
        setTimeout(() => {
            if (loaderContainer && loaderContainer.parentNode) {
                loaderContainer.parentNode.removeChild(loaderContainer);
            }
        }, 800);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const loaderContainer = document.getElementById('loader-container');
    const appContainer = document.querySelector('.app-container');
    
    // Ocultar el contenido principal inicialmente
    if (appContainer) {
        appContainer.style.opacity = '0';
        appContainer.style.visibility = 'hidden';
        appContainer.style.transition = 'opacity 0.8s ease-in-out, visibility 0.8s ease-in-out';
    }
    
    // Crear partículas adicionales si existe el contenedor
    if (loaderContainer) {
        createParticles();
        const loadingInterval = simulateLoading();
        
        // Esperar a que la página se cargue completamente
        window.addEventListener('load', function() {
            // Tiempo mínimo de visualización del loader (2 segundos)
            setTimeout(() => {
                clearInterval(loadingInterval);
                hideLoader();
            }, 2000);
        });
        
        // Fallback: ocultar después de 5 segundos máximo
        setTimeout(() => {
            clearInterval(loadingInterval);
            hideLoader();
        }, 5000);
    } else {
        // Si no hay loader, mostrar el contenido inmediatamente
        if (appContainer) {
            appContainer.style.opacity = '1';
            appContainer.style.visibility = 'visible';
        }
    }
});

// Efecto adicional: cambiar color del botón de encendido
const powerButtonInterval = setInterval(() => {
    const powerButton = document.querySelector('.power-button');
    if (powerButton) {
        const colors = ['#00d4ff', '#00ff88', '#ff6b6b', '#ffd93d', '#3498db'];
        const randomColor = colors[Math.floor(Math.random() * colors.length)];
        powerButton.style.background = randomColor;
        powerButton.style.boxShadow = `0 0 8px ${randomColor}`;
    } else {
        // Si el botón no existe, limpiar el intervalo
        clearInterval(powerButtonInterval);
    }
}, 1500);

// Limpiar intervalo cuando se oculte el loader
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        clearInterval(powerButtonInterval);
    }, 6000);
});