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
