document.addEventListener('DOMContentLoaded', function () {
    const grafico = document.getElementById('grafico');
    const labels = JSON.parse(grafico.dataset.labels || "[]");  // Evita errores si está vacío
    const datos = JSON.parse(grafico.dataset.datos || "[]");

    console.log("Labels:", labels);  // Debug en consola
    console.log("Datos:", datos);  // Debug en consola

    if (labels.length === 0 || datos.length === 0) {
        alert("No hay datos de alquileres.");
        return;
    }

    new Chart(grafico.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total de Alquileres',
                data: datos,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});
