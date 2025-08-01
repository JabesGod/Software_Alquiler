// Script específico para edición
document.addEventListener('DOMContentLoaded', function () {
    // Manejar la selección de foto principal
    document.querySelectorAll('.photo-card input[name$="-es_principal"]').forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.checked) {
                // Desmarcar las otras fotos principales
                document.querySelectorAll('.photo-card input[name$="-es_principal"]').forEach(otherRadio => {
                    if (otherRadio !== this) {
                        otherRadio.checked = false;
                    }
                });
            }
        });
    });

    // Previsualización de nuevas fotos
    const fileInput = document.querySelector('input[name="nuevas_fotos"]');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            // Implementar previsualización de nuevas fotos aquí
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const modalElement = document.getElementById("confirmDeleteModal");

    // 1. Eliminar clases de Bootstrap que lo abren automáticamente
    modalElement.classList.remove("show");
    modalElement.style.display = "none";

    // 2. Eliminar backdrop si quedó colgado
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(b => b.remove());

    // 3. Quitar scroll-block de body si quedó bloqueado
    document.body.classList.remove("modal-open");
    document.body.style.paddingRight = "";
});

    document.addEventListener('DOMContentLoaded', function () {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][name$="es_principal"]');

        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    checkboxes.forEach(cb => {
                        if (cb !== this) cb.checked = false;
                    });
                }
            });
        });
    });

document.addEventListener('DOMContentLoaded', function() {
    // Manejar la visualización de archivos seleccionados
    const fileInput = document.querySelector('.file-upload-input');
    const uploadContent = document.querySelector('.upload-content');
    
    if (fileInput && uploadContent) {
        fileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                uploadContent.innerHTML = `
                    <i class="fas fa-check-circle text-success"></i>
                    <p>${this.files.length} archivo(s) seleccionado(s)</p>
                    <small class="text-muted">Listo para subir</small>
                `;
            }
        });
    }
    
    // Validación de tamaño de archivo
    document.querySelector('form').addEventListener('submit', function(e) {
        const files = document.querySelector('.file-upload-input').files;
        let isValid = true;
        
        for (let i = 0; i < files.length; i++) {
            if (files[i].size > 5 * 1024 * 1024) { // 5MB
                alert(`El archivo ${files[i].name} es demasiado grande (máximo 5MB)`);
                isValid = false;
                break;
            }
            
            const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!validTypes.includes(files[i].type)) {
                alert(`Tipo de archivo no soportado para ${files[i].name}. Use JPG, PNG o GIF.`);
                isValid = false;
                break;
            }
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
});    