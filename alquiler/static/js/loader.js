

window.addEventListener('load', function() {
    const loaderContainer = document.getElementById('loader-container');
    const pageContent = document.getElementById('page-content');
    
    // Oculta la pantalla de carga con la clase CSS
    loaderContainer.classList.add('loader-hidden');
    
    // Hace visible el contenido de la página después de que el loader se haya desvanecido
    setTimeout(() => {
        pageContent.style.opacity = '1';
        // Opcional: Eliminar el loader del DOM para limpiar
        loaderContainer.remove(); 
    }, 500); 
});