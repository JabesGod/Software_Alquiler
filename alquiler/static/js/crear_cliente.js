document.addEventListener('DOMContentLoaded', function() {
    const tipoClienteSelect = document.getElementById('id_tipo_cliente');
    const empresaSection = document.getElementById('empresa-section');
    
    function toggleEmpresaSection() {
        if (tipoClienteSelect.value === 'juridica') {
            empresaSection.style.display = 'block';
            document.getElementById('id_nombre_empresa').required = true;
            document.getElementById('id_nit').required = true;
        } else {
            empresaSection.style.display = 'none';
            document.getElementById('id_nombre_empresa').required = false;
            document.getElementById('id_nit').required = false;
        }
    }
    
    toggleEmpresaSection();
    tipoClienteSelect.addEventListener('change', toggleEmpresaSection);
});