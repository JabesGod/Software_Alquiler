document.addEventListener('DOMContentLoaded', function () {
    // Toggle sidebar en móviles
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    // Configurar el modo oscuro
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // Configurar el color picker
    const colorPicker = document.getElementById('navColorPicker');
    const root = document.documentElement;
    const colorPreview = document.querySelector('.color-preview');
    
    // Buscador global
    const searchInput = document.getElementById('globalSearchInput');
    const searchForm = document.getElementById('globalSearchForm');
    const searchSuggestions = document.getElementById('searchSuggestions');
    
    // Aplicar configuraciones guardadas
    applySavedSettings();
    
    // Event listeners
    if (menuToggle) menuToggle.addEventListener('click', toggleSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener('click', closeSidebar);
    
    // Configurar submenús
    setupSubmenus();
    
    // Resaltar ítem activo
    highlightActiveMenu();
    
    // Configurar el modo oscuro
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', toggleDarkMode);
    }
    
    // Configurar el color picker
    if (colorPicker) {
        colorPicker.addEventListener('input', updateNavColor);
    }
    
    // Configurar el buscador global
    if (searchInput && searchForm && searchSuggestions) {
        setupSearch(searchInput, searchForm, searchSuggestions);
    }
    
    // Ajustar el sidebar al cambiar el tamaño de la ventana
    window.addEventListener('resize', handleResize);
    
    // Configurar scroll del sidebar
    handleSidebarScroll();
    
    // Funciones principales
    function applySavedSettings() {
        // Aplicar modo oscuro si está activado
        if (localStorage.getItem('darkMode') === 'enabled') {
            body.classList.add('dark-mode');
            if (darkModeToggle) darkModeToggle.checked = true;
        }
        
        // Aplicar color guardado (si existe)
        const savedColor = localStorage.getItem('navColor');
        if (savedColor && colorPicker && colorPreview) {
            root.style.setProperty('--primary-color', savedColor);
            const darkerColor = shadeColor(savedColor, -20);
            root.style.setProperty('--secondary-color', darkerColor);
            colorPicker.value = savedColor;
            colorPreview.style.backgroundColor = savedColor;
        }
    }
    
    function toggleSidebar() {
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
        document.body.classList.toggle('sidebar-open');
    }
    
    function closeSidebar() {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.classList.remove('sidebar-open');
    }
    
    function setupSubmenus() {
        const hasSubmenu = document.querySelectorAll('.has-submenu > .menu-link');
        
        hasSubmenu.forEach(item => {
            item.addEventListener('click', function (e) {
                // Solo prevenir comportamiento por defecto si es un enlace "#"
                if (this.getAttribute('href') === '#') {
                    e.preventDefault();
                }
                
                const parent = this.parentElement;
                
                // Cerrar otros submenús abiertos solo en móviles
                if (window.innerWidth <= 768) {
                    document.querySelectorAll('.has-submenu').forEach(otherItem => {
                        if (otherItem !== parent) {
                            otherItem.classList.remove('active');
                        }
                    });
                }
                
                // Alternar el submenú actual
                parent.classList.toggle('active');
                
                // Cerrar el sidebar en móviles al seleccionar un enlace real
                if (this.getAttribute('href') !== '#' && window.innerWidth <= 768) {
                    closeSidebar();
                }
            });
        });
        
        // Cerrar submenús al hacer clic fuera solo en móviles
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && !e.target.closest('.has-submenu')) {
                document.querySelectorAll('.has-submenu').forEach(item => {
                    item.classList.remove('active');
                });
            }
        });
    }
    
    function highlightActiveMenu() {
        const currentPath = window.location.pathname;
        const menuLinks = document.querySelectorAll('.sidebar-menu a[href]:not([href="#"])');
        
        menuLinks.forEach(link => {
            if (link.href && currentPath.includes(new URL(link.href).pathname)) {
                link.classList.add('active');
                
                // Abrir submenú padre si existe
                const parentSubmenu = link.closest('.submenu');
                if (parentSubmenu) {
                    const parentItem = parentSubmenu.closest('.has-submenu');
                    if (parentItem) {
                        parentItem.classList.add('active');
                        
                        // Abrir también el submenú padre si está anidado
                        const grandParent = parentItem.closest('.submenu');
                        if (grandParent) {
                            grandParent.closest('.has-submenu').classList.add('active');
                        }
                    }
                }
            }
        });
    }
    
    function toggleDarkMode() {
        if (this.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
        }
    }
    
    function updateNavColor() {
        const newColor = this.value;
        root.style.setProperty('--primary-color', newColor);
        
        // Calcular y establecer una versión más oscura para el color secundario
        const darkerColor = shadeColor(newColor, -20);
        root.style.setProperty('--secondary-color', darkerColor);
        
        // Actualizar la vista previa
        colorPreview.style.backgroundColor = newColor;
        
        // Guardar en localStorage
        localStorage.setItem('navColor', newColor);
    }
    
    function handleResize() {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    }
    
    function handleSidebarScroll() {
        if (sidebar) {
            sidebar.addEventListener('touchmove', function(e) {
                e.preventDefault();
            }, { passive: false });
        }
    }
    
    function setupSearch(input, form, suggestionsContainer) {
        // Mostrar/ocultar sugerencias
        input.addEventListener('focus', function() {
            if (this.value.length > 0) {
                fetchSuggestions(this.value);
            }
        });
        
        input.addEventListener('blur', function() {
            setTimeout(() => {
                suggestionsContainer.style.display = 'none';
            }, 200);
        });
        
        // Autocompletado mientras se escribe
        input.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            
            if (query.length > 1) {
                fetchSuggestions(query);
            } else {
                suggestionsContainer.innerHTML = '';
                suggestionsContainer.style.display = 'none';
            }
        }, 300));
        
        // Manejar selección de sugerencias
        suggestionsContainer.addEventListener('click', function(e) {
            const suggestionItem = e.target.closest('.search-suggestion-item');
            if (suggestionItem) {
                input.value = suggestionItem.dataset.text;
                form.submit();
            }
        });
        
        // Prevenir envío del formulario si no hay query
        form.addEventListener('submit', function(e) {
            if (input.value.trim().length < 1) {
                e.preventDefault();
                suggestionsContainer.style.display = 'none';
            }
        });
        
        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!form.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });
        
        function fetchSuggestions(query) {
            // Aquí deberías hacer una llamada AJAX a tu endpoint de sugerencias
            // Ejemplo con datos mock para pruebas
            const mockData = [
                { type: 'equipo', text: '' },
                { type: 'cliente', text: '' },
                { type: 'alquiler', text: '' }
            ];
            
            // Filtrar datos mock basados en la query (simulación)
            const filteredData = mockData.filter(item => 
                item.text.toLowerCase().includes(query.toLowerCase())
            );
            
            showSuggestions(filteredData);
        }
        
        function showSuggestions(suggestions) {
            suggestionsContainer.innerHTML = '';
            
            if (suggestions.length > 0) {
                suggestions.forEach(item => {
                    const suggestion = document.createElement('div');
                    suggestion.className = 'search-suggestion-item';
                    suggestion.dataset.text = item.text.split(' (')[0]; // Para solo tomar el nombre
                    
                    // Icono según el tipo
                    let iconClass = 'fa-question';
                    if (item.type === 'equipo') iconClass = 'fa-laptop';
                    if (item.type === 'cliente') iconClass = 'fa-user';
                    if (item.type === 'alquiler') iconClass = 'fa-handshake';
                    
                    suggestion.innerHTML = `
                        <i class="fas ${iconClass}"></i>
                        <span class="suggestion-text">${item.text}</span>
                    `;
                    
                    suggestionsContainer.appendChild(suggestion);
                });
                suggestionsContainer.style.display = 'block';
            } else {
                const noResults = document.createElement('div');
                noResults.className = 'search-suggestion-item no-results';
                noResults.textContent = 'No se encontraron resultados';
                suggestionsContainer.appendChild(noResults);
                suggestionsContainer.style.display = 'block';
            }
        }
    }
    
    // Función debounce para mejorar rendimiento
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this, args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                func.apply(context, args);
            }, wait);
        };
    }
    
    // Función para aclarar/oscurecer colores
    function shadeColor(color, percent) {
        let R = parseInt(color.substring(1, 3), 16);
        let G = parseInt(color.substring(3, 5), 16);
        let B = parseInt(color.substring(5, 7), 16);

        R = parseInt(R * (100 + percent) / 100);
        G = parseInt(G * (100 + percent) / 100);
        B = parseInt(B * (100 + percent) / 100);

        R = (R < 255) ? R : 255;
        G = (G < 255) ? G : 255;
        B = (B < 255) ? B : 255;

        R = Math.round(R);
        G = Math.round(G);
        B = Math.round(B);

        const RR = ((R.toString(16).length == 1) ? "0" + R.toString(16) : R.toString(16));
        const GG = ((G.toString(16).length == 1) ? "0" + G.toString(16) : G.toString(16));
        const BB = ((B.toString(16).length == 1) ? "0" + B.toString(16) : B.toString(16));

        return "#" + RR + GG + BB;
    }
});


let inactivityTime = function() {
    let time;
    const logoutUrl = "{% url 'inicio_sesion' %}?session_expired=1";
    const warningTime = 1000 * 60 * 4; // 4 minutos (aviso 1 minuto antes)
    
    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeypress = resetTimer;
    
    function showWarning() {
        // Puedes mostrar un modal o notificación aquí
        alert('Tu sesión está a punto de expirar por inactividad. Realiza alguna acción para mantenerte conectado.');
    }
    
    function logout() {
        window.location.href = logoutUrl;
    }
    
    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(showWarning, warningTime);
        time = setTimeout(logout, 1000 * 60 * 5); // 5 minutos
    }
};


