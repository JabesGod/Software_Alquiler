document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.pagos-table tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('click', function() {
            const paymentId = this.getAttribute('data-payment-id');
            if (paymentId) {
                window.location.href = `/pagos/detalle/${paymentId}/`;
            }
        });
        
        row.style.cursor = 'pointer';
        row.style.transition = 'background-color 0.2s ease';
    });
    
    const filterInput = document.getElementById('filter-input');
    if (filterInput) {
        filterInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
});