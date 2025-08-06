

function generarPDFenCliente() {

    
    if (typeof jsPDF === 'undefined' || typeof html2canvas === 'undefined') {
        console.error('Las bibliotecas jsPDF y html2canvas son requeridas');
        return;
    }
    
    const { jsPDF } = window.jspdf;
    const element = document.querySelector('.contenedor');
    const filename = 'estadisticas_alquileres.pdf';
    
    html2canvas(element, {
        scale: 2,
        logging: false,
        useCORS: true,
        allowTaint: true
    }).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgProps = pdf.getImageProperties(imgData);
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save(filename);
    });
}
