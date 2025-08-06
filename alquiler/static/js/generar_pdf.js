document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('export-excel')?.addEventListener('click', function() {
        exportarAExcel();
    });

    document.getElementById('export-pdf')?.addEventListener('click', function() {
        exportarAPDF();
    });
});

function exportarAExcel() {
    const params = new URLSearchParams(window.location.search);
    params.set('export', 'excel');
    
    window.location.href = window.location.pathname + '?' + params.toString();
}

function exportarAPDF() {
    const params = new URLSearchParams(window.location.search);
    params.set('export', 'pdf');
    
    window.location.href = window.location.pathname + '?' + params.toString();
}