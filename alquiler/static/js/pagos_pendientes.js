// pagos_pendientes.js
document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality for the payments page
    const rows = document.querySelectorAll('.pagos-table tbody tr');
    
    rows.forEach(row => {
        row.addEventListener('click', function() {
            // Example: Navigate to payment detail when row is clicked
            const paymentId = this.getAttribute('data-payment-id');
            if (paymentId) {
                window.location.href = `/pagos/detalle/${paymentId}/`;
            }
        });
        
        // Add hover effect
        row.style.cursor = 'pointer';
        row.style.transition = 'background-color 0.2s ease';
    });
    
    // Add filter functionality if needed
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