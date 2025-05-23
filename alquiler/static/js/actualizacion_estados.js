document.addEventListener('DOMContentLoaded', function() {
    // Selección/deselección de todos los equipos
    const checkTodos = document.getElementById('check-todos');
    const checksEquipos = document.querySelectorAll('.check-equipo');
    const btnSeleccionarTodos = document.getElementById('seleccionar-todos');
    const btnDeseleccionarTodos = document.getElementById('deseleccionar-todos');
    
    checkTodos.addEventListener('change', function() {
        checksEquipos.forEach(check => {
            check.checked = this.checked;
        });
    });
    
    btnSeleccionarTodos.addEventListener('click', function(e) {
        e.preventDefault();
        checksEquipos.forEach(check => {
            check.checked = true;
        });
        checkTodos.checked = true;
    });
    
    btnDeseleccionarTodos.addEventListener('click', function(e) {
        e.preventDefault();
        checksEquipos.forEach(check => {
            check.checked = false;
        });
        checkTodos.checked = false;
    });
    
    // Filtrado de equipos
    const filtroEquipos = document.getElementById('filtro-equipos');
    const filasEquipos = document.querySelectorAll('.equipo-fila');
    
    filtroEquipos.addEventListener('input', function() {
        const texto = this.value.toLowerCase();
        
        filasEquipos.forEach(fila => {
            const textoFila = fila.textContent.toLowerCase();
            fila.style.display = textoFila.includes(texto) ? '' : 'none';
        });
    });
    
    // Validación del formulario
    const form = document.querySelector('.form-actualizacion');
    
    form.addEventListener('submit', function(e) {
        const checksSeleccionados = document.querySelectorAll('.check-equipo:checked');
        const estadoSeleccionado = document.querySelector('.select-estado').value;
        
        if (checksSeleccionados.length === 0) {
            e.preventDefault();
            alert('Por favor seleccione al menos un equipo');
            return false;
        }
        
        if (!estadoSeleccionado) {
            e.preventDefault();
            alert('Por favor seleccione un estado');
            return false;
        }
        
        // Confirmación antes de actualizar
        if (!confirm(`¿Está seguro de actualizar ${checksSeleccionados.length} equipo(s) al estado seleccionado?`)) {
            e.preventDefault();
            return false;
        }
    });
    
    // Resaltar estado seleccionado
    const selectEstado = document.querySelector('.select-estado');
    
    selectEstado.addEventListener('change', function() {
        // Remover clases de color anteriores
        selectEstado.className = 'select-estado';
        
        // Agregar clase de color según la opción seleccionada
        const opcionSeleccionada = this.options[this.selectedIndex];
        if (opcionSeleccionada.dataset.color) {
            selectEstado.classList.add(opcionSeleccionada.dataset.color);
        }
    });
});