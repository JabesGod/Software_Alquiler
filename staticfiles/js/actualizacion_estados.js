document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const form = document.getElementById('form-actualizacion');
    const checkTodos = document.getElementById('check-todos');
    const checkEquipos = document.querySelectorAll('.check-equipo');
    const btnSeleccionarTodos = document.getElementById('seleccionar-todos');
    const btnDeseleccionarTodos = document.getElementById('deseleccionar-todos');
    const filtroEquipos = document.getElementById('filtro-equipos');
    const selectEstado = document.getElementById('select-estado');
    const btnActualizar = document.getElementById('btn-actualizar');
    const modal = document.getElementById('modal-confirmacion');
    const btnCancelar = document.getElementById('btn-cancelar');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const textoConfirmacion = document.getElementById('texto-confirmacion');

    // Filtrado de equipos
    filtroEquipos.addEventListener('input', function() {
        const filtro = this.value.toLowerCase();
        const filas = document.querySelectorAll('.equipo-fila');
        
        filas.forEach(fila => {
            const textoFila = fila.textContent.toLowerCase();
            fila.style.display = textoFila.includes(filtro) ? '' : 'none';
        });
    });

    // Selección de todos los equipos disponibles
    btnSeleccionarTodos.addEventListener('click', function(e) {
        e.preventDefault();
        const equiposDisponibles = document.querySelectorAll('.equipo-fila[data-alquilado="false"] .check-equipo:not(:disabled)');
        
        equiposDisponibles.forEach(checkbox => {
            checkbox.checked = true;
        });
        
        checkTodos.checked = [...document.querySelectorAll('.check-equipo:not(:disabled)')]
            .every(checkbox => checkbox.checked);
    });

    // Deselección de todos los equipos
    btnDeseleccionarTodos.addEventListener('click', function(e) {
        e.preventDefault();
        checkEquipos.forEach(checkbox => {
            checkbox.checked = false;
        });
        checkTodos.checked = false;
    });

    // Control del checkbox "todos"
    checkTodos.addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('.check-equipo:not(:disabled)');
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
    });

    // Validación del formulario antes de enviar
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const equiposSeleccionados = [...document.querySelectorAll('.check-equipo:checked')];
        const nuevoEstado = selectEstado.value;
        
        if (equiposSeleccionados.length === 0) {
            Swal.fire({
                title: 'Error',
                text: 'Debes seleccionar al menos un equipo',
                icon: 'error',
                confirmButtonColor: '#4361ee'
            });
            return;
        }
        
        if (!nuevoEstado) {
            Swal.fire({
                title: 'Error',
                text: 'Debes seleccionar un estado válido',
                icon: 'error',
                confirmButtonColor: '#4361ee'
            });
            return;
        }
        
        // Mostrar modal de confirmación
        const equiposConAlquiler = [...document.querySelectorAll('.check-equipo:checked')]
            .filter(checkbox => checkbox.closest('tr').dataset.alquilado === 'true');
        
        if (equiposConAlquiler.length > 0) {
            Swal.fire({
                title: 'Alerta',
                html: `<p>${equiposConAlquiler.length} equipos seleccionados tienen alquileres activos y no serán actualizados.</p>
                      <p>¿Deseas continuar con la actualización del resto?</p>`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#4361ee',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, actualizar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Enviar solo los equipos sin alquiler activo
                    const equiposParaActualizar = equiposSeleccionados
                        .filter(checkbox => checkbox.closest('tr').dataset.alquilado === 'false')
                        .map(checkbox => checkbox.value);
                    
                    // Crear input oculto con los IDs válidos
                    const inputOculto = document.createElement('input');
                    inputOculto.type = 'hidden';
                    inputOculto.name = 'ids_equipos';
                    inputOculto.value = equiposParaActualizar.join(',');
                    form.appendChild(inputOculto);
                    
                    // Deshabilitar los checkboxes originales
                    document.querySelectorAll('input[name="ids_equipos"]').forEach(input => {
                        input.disabled = true;
                    });
                    
                    form.submit();
                }
            });
        } else {
            // Todos los equipos seleccionados pueden ser actualizados
            Swal.fire({
                title: 'Confirmar',
                text: `¿Estás seguro de actualizar ${equiposSeleccionados.length} equipos al estado seleccionado?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#4361ee',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, actualizar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        }
    });

    // Actualizar interfaz cuando cambia el estado seleccionado
    selectEstado.addEventListener('change', function() {
        const color = this.options[this.selectedIndex].dataset.color;
        btnActualizar.className = `btn-actualizar ${color}`;
    });
});