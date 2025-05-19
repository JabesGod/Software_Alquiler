document.addEventListener("DOMContentLoaded", function () {
    // Referencia al canvas
    const canvas = document.getElementById('signature-pad');
    
    // Ajustar el tamaño del canvas para que coincida con sus dimensiones en el HTML
    // Esto es crucial, ya que los canvas requieren que el ancho y alto se establezcan mediante JavaScript
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Inicializar SignaturePad con opciones explícitas
    const signaturePad = new SignaturePad(canvas, {
        minWidth: 1.5,
        maxWidth: 3,
        penColor: "black",
        backgroundColor: "rgba(255, 255, 255, 0)"
    });
    
    // Botón para borrar firma
    const clearButton = document.getElementById('clear-signature');
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            signaturePad.clear();
        });
    }
    
    // Campo oculto para guardar los datos de la firma
    const hiddenInput = document.getElementById('firma_data');
    
    // Al enviar el formulario, guardar los datos de la firma en el campo oculto
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!signaturePad.isEmpty()) {
                const dataURL = signaturePad.toDataURL('image/png');
                hiddenInput.value = dataURL;
                // Opcional: Puedes imprimir en consola para verificar
                console.log("Firma capturada: ", dataURL.substring(0, 50) + "...");
            } else {
                console.log("No hay firma para guardar");
                // Si prefieres no enviar el formulario cuando no hay firma:
                // e.preventDefault();
                // alert("Por favor, dibuja tu firma antes de continuar");
            }
        });
    }
});

