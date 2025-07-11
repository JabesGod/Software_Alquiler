
document.getElementById('{{ form.tipo_cliente.id_for_label }}').addEventListener('change', function () {
    const empresaSection = document.getElementById('empresa-section');
    if (this.value === 'juridica') {
        empresaSection.style.display = 'block';
        // Hacer campos requeridos si son visibles
        document.getElementById('{{ form.nombre_empresa.id_for_label }}').required = true;
        document.getElementById('{{ form.nit.id_for_label }}').required = true;
    } else {
        empresaSection.style.display = 'none';
        // Quitar requerimiento si no son visibles
        document.getElementById('{{ form.nombre_empresa.id_for_label }}').required = false;
        document.getElementById('{{ form.nit.id_for_label }}').required = false;
    }
});

// Inicializar el estado al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    const tipoCliente = document.getElementById('{{ form.tipo_cliente.id_for_label }}');
    if (tipoCliente.value === 'juridica') {
        document.getElementById('empresa-section').style.display = 'block';
    }
});
