document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('.photo-card input[name$="-es_principal"]').forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.checked) {
                document.querySelectorAll('.photo-card input[name$="-es_principal"]').forEach(otherRadio => {
                    if (otherRadio !== this) {
                        otherRadio.checked = false;
                    }
                });
            }
        });
    });

    const fileInput = document.querySelector('input[name="nuevas_fotos"]');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {

        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const modalElement = document.getElementById("confirmDeleteModal");

    modalElement.classList.remove("show");
    modalElement.style.display = "none";

    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(b => b.remove());

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
    
    document.querySelector('form').addEventListener('submit', function(e) {
        const files = document.querySelector('.file-upload-input').files;
        let isValid = true;
        
        for (let i = 0; i < files.length; i++) {
            if (files[i].size > 5 * 1024 * 1024) { 
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