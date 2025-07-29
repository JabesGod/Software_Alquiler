document.addEventListener('DOMContentLoaded', function () {
    const rows = document.querySelectorAll('.clickable-row');
    rows.forEach(row => {
        row.addEventListener('click', function () {
            const href = this.dataset.href;
            if (href) {
                window.location.href = href;
            }
        });
    });

    // Opcional: Para cambiar el cursor y dar indicación de que la fila es clickable
    const style = document.createElement('style');
    style.innerHTML = `
            .clickable-row {
                cursor: pointer;
            }
        `;
    document.head.appendChild(style);
});