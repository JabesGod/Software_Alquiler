document.addEventListener('DOMContentLoaded', function () {
    console.log('Inicializando sistema de firmas...');

    const signatureConfig = {
        penColor: 'rgb(0, 0, 0)',
        minWidth: 0.8,
        maxWidth: 2.5,
        throttle: 8,
        velocityFilterWeight: 0.8,
        dotSize: 1.5,
        minDistance: 1
    };

    const canvasCliente = document.getElementById('signature-pad-cliente');
    const canvasRepresentante = document.getElementById('signature-pad-representante');
    
    if (!canvasCliente || !canvasRepresentante) {
        console.error('No se encontraron los canvas de firma');
        return;
    }

    let signaturePadCliente, signaturePadRepresentante;
    
    try {
        signaturePadCliente = new SignaturePad(canvasCliente, signatureConfig);
        signaturePadRepresentante = new SignaturePad(canvasRepresentante, signatureConfig);
        console.log('SignaturePads inicializados correctamente');
    } catch (error) {
        console.error('Error al inicializar SignaturePads:', error);
        return;
    }

    function setupCanvas(canvas, signaturePad) {
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        
        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);
        
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        
        signaturePad.clear();
    }

    setTimeout(() => {
        setupCanvas(canvasCliente, signaturePadCliente);
        setupCanvas(canvasRepresentante, signaturePadRepresentante);
    }, 100);

    function updateSignatureStatus(signaturePad, statusElementId) {
        const statusElement = document.getElementById(statusElementId);
        if (statusElement) {
            if (signaturePad.isEmpty()) {
                statusElement.innerHTML = '<i class="fas fa-pen icon"></i>Esperando firma...';
                statusElement.className = 'signature-status signature-empty';
            } else {
                statusElement.innerHTML = '<i class="fas fa-check icon"></i>Firma lista';
                statusElement.className = 'signature-status signature-ready';
            }
        }
    }

    function addStatusElements() {
        const clienteContainer = canvasCliente.closest('.firma-container');
        const representanteContainer = canvasRepresentante.closest('.firma-container');
        
        if (clienteContainer && !document.getElementById('status-cliente')) {
            const statusDiv = document.createElement('div');
            statusDiv.id = 'status-cliente';
            statusDiv.className = 'signature-status signature-empty';
            statusDiv.innerHTML = '<i class="fas fa-pen icon"></i>Esperando firma...';
            canvasCliente.parentNode.insertBefore(statusDiv, canvasCliente.nextSibling);
        }
        
        if (representanteContainer && !document.getElementById('status-representante')) {
            const statusDiv = document.createElement('div');
            statusDiv.id = 'status-representante';
            statusDiv.className = 'signature-status signature-empty';
            statusDiv.innerHTML = '<i class="fas fa-pen icon"></i>Esperando firma...';
            canvasRepresentante.parentNode.insertBefore(statusDiv, canvasRepresentante.nextSibling);
        }
    }

    addStatusElements();

    signaturePadCliente.addEventListener('beginStroke', () => {
        console.log('Iniciando firma del cliente');
    });

    signaturePadCliente.addEventListener('endStroke', () => {
        updateSignatureStatus(signaturePadCliente, 'status-cliente');
        console.log('Firma del cliente actualizada');
    });

    signaturePadRepresentante.addEventListener('beginStroke', () => {
        console.log('Iniciando firma del representante');
    });

    signaturePadRepresentante.addEventListener('endStroke', () => {
        updateSignatureStatus(signaturePadRepresentante, 'status-representante');
        console.log('Firma del representante actualizada');
    });

    const clearClienteBtn = document.getElementById('clear-signature-cliente');
    const clearRepresentanteBtn = document.getElementById('clear-signature-representante');

    if (clearClienteBtn) {
        clearClienteBtn.addEventListener('click', function() {
            signaturePadCliente.clear();
            updateSignatureStatus(signaturePadCliente, 'status-cliente');
            const firmaDataField = document.getElementById('firma-data-cliente');
            if (firmaDataField) {
                firmaDataField.value = '';
            }
            console.log('Firma del cliente borrada');
        });
    }

    if (clearRepresentanteBtn) {
        clearRepresentanteBtn.addEventListener('click', function() {
            signaturePadRepresentante.clear();
            updateSignatureStatus(signaturePadRepresentante, 'status-representante');
            const firmaDataField = document.getElementById('firma-data-representante');
            if (firmaDataField) {
                firmaDataField.value = '';
            }
            console.log('Firma del representante borrada');
        });
    }

    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            console.log('Redimensionando canvas...');
            setupCanvas(canvasCliente, signaturePadCliente);
            setupCanvas(canvasRepresentante, signaturePadRepresentante);
        }, 250);
    });

    const form = document.getElementById('firmaForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Preparando envío del formulario...');
            
            const firmaClienteField = document.getElementById('firma-data-cliente');
            const firmaRepresentanteField = document.getElementById('firma-data-representante');
            
            if (!signaturePadCliente.isEmpty() && firmaClienteField) {
                firmaClienteField.value = signaturePadCliente.toDataURL('image/png');
                console.log('Firma del cliente guardada en campo: firma_data');
            }
            
            if (!signaturePadRepresentante.isEmpty() && firmaRepresentanteField) {
                firmaRepresentanteField.value = signaturePadRepresentante.toDataURL('image/png');
                console.log('Firma del representante guardada en campo: firma_representante_data');
            }
            
            const clienteImageFile = document.querySelector('input[name="firma_imagen"]');
            const representanteImageFile = document.querySelector('input[name="firma_representante_imagen"]');
            
            const hasClienteSignature = !signaturePadCliente.isEmpty() || 
                (clienteImageFile && clienteImageFile.files.length > 0);
                
            const hasRepresentanteSignature = !signaturePadRepresentante.isEmpty() || 
                (representanteImageFile && representanteImageFile.files.length > 0);
                
            if (!hasClienteSignature) {
                e.preventDefault();
                alert('Por favor, proporcione la firma del cliente (dibujada o como imagen)');
                console.warn('Falta firma del cliente');
                return false;
            }

            if (!hasRepresentanteSignature) {
                e.preventDefault();
                alert('Por favor, proporcione la firma del representante (dibujada o como imagen)');
                console.warn('Falta firma del representante');
                return false;
            }
            
            console.log('Datos del formulario:', {
                firma_data: firmaClienteField ? firmaClienteField.value.substring(0, 50) + '...' : 'null',
                firma_representante_data: firmaRepresentanteField ? firmaRepresentanteField.value.substring(0, 50) + '...' : 'null',
                firma_imagen: clienteImageFile ? clienteImageFile.files.length : 0,
                firma_representante_imagen: representanteImageFile ? representanteImageFile.files.length : 0
            });
            
            console.log('Todas las firmas están completas, enviando formulario...');
            return true;
        });
    }

    function setupFileInput(inputElement, signaturePad, statusId) {
        if (inputElement) {
            inputElement.addEventListener('change', function() {
                if (this.files.length > 0) {
                    const file = this.files[0];
                    console.log('Archivo seleccionado:', file.name);
                    
                    if (file.size > 2 * 1024 * 1024) {
                        alert('El archivo es demasiado grande. Máximo 2MB.');
                        this.value = '';
                        return;
                    }
                    
                    if (!file.type.startsWith('image/')) {
                        alert('Por favor, seleccione solo archivos de imagen.');
                        this.value = '';
                        return;
                    }
                    
                    updateSignatureStatus({ isEmpty: () => false }, statusId);
                }
            });
        }
    }

    setupFileInput(
        document.querySelector('input[name="firma_imagen"]'), 
        signaturePadCliente, 
        'status-cliente'
    );
    
    setupFileInput(
        document.querySelector('input[name="firma_representante_imagen"]'), 
        signaturePadRepresentante, 
        'status-representante'
    );

    console.log('Sistema de firmas completamente inicializado');
});

document.addEventListener('DOMContentLoaded', function() {
    if (typeof SignaturePad === 'undefined') {
        console.error('SignaturePad no se cargó correctamente');
        alert('Error: No se pudo cargar el sistema de firmas. Por favor, recarga la página.');
    } else {
        console.log('SignaturePad cargado correctamente');
    }
});