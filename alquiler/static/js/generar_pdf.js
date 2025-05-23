document.addEventListener('DOMContentLoaded', function() {
    // Exportar a Excel
    document.getElementById('export-excel')?.addEventListener('click', function() {
        exportarAExcel();
    });

    // Exportar a PDF (versión cliente - alternativa)
    document.getElementById('export-pdf')?.addEventListener('click', function() {
        exportarAPDF();
    });
});

function exportarAExcel() {
    // Obtener parámetros actuales de filtro
    const params = new URLSearchParams(window.location.search);
    params.set('export', 'excel');
    
    // Redirigir a la misma URL pero con parámetro de exportación
    window.location.href = window.location.pathname + '?' + params.toString();
}

function exportarAPDF() {
    // Obtener parámetros actuales de filtro
    const params = new URLSearchParams(window.location.search);
    params.set('export', 'pdf');
    
    // Redirigir a la misma URL pero con parámetro de exportación
    window.location.href = window.location.pathname + '?' + params.toString();
}