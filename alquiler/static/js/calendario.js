document.addEventListener('DOMContentLoaded', function() {
    const contenedor = document.getElementById('calendarioContainer');
    const anioActual = document.getElementById('anioActual');
    const btnPrev = document.getElementById('anioAnterior');
    const btnNext = document.getElementById('anioSiguiente');

    let anio = new Date().getFullYear();
    anioActual.textContent = anio;

    // Configuración
    const maxEventosVisibles = 3;
    const diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];
    const nombresMeses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];

    // Renderizar calendario
    function renderCalendario(anio) {
        contenedor.innerHTML = '';
        
        for (let mes = 0; mes < 12; mes++) {
            const primerDia = new Date(anio, mes, 1).getDay();
            const diasEnMes = new Date(anio, mes + 1, 0).getDate();
            const ajusteLunes = (primerDia + 6) % 7; // Ajuste para que semana empiece en lunes

            // Crear tarjeta del mes
            const tarjeta = document.createElement('div');
            tarjeta.className = 'mes mb-4';
            
            // Título del mes
            const titulo = document.createElement('h3');
            titulo.className = 'titulo-mes text-center mb-3';
            titulo.textContent = nombresMeses[mes];
            tarjeta.appendChild(titulo);

            // Tabla del mes
            const tabla = document.createElement('table');
            tabla.className = 'table table-bordered';
            
            // Cabecera con días de la semana
            const thead = document.createElement('thead');
            const trHead = document.createElement('tr');
            
            diasSemana.forEach(dia => {
                const th = document.createElement('th');
                th.className = 'text-center';
                th.textContent = dia;
                trHead.appendChild(th);
            });
            
            thead.appendChild(trHead);
            tabla.appendChild(thead);

            // Cuerpo del calendario
            const tbody = document.createElement('tbody');
            let tr = document.createElement('tr');
            
            // Días vacíos iniciales
            for (let i = 0; i < ajusteLunes; i++) {
                tr.appendChild(document.createElement('td'));
            }

            // Días del mes
            for (let dia = 1; dia <= diasEnMes; dia++) {
                if (tr.children.length === 7) {
                    tbody.appendChild(tr);
                    tr = document.createElement('tr');
                }

                const td = document.createElement('td');
                td.className = 'celda-dia';
                
                // Número del día
                const numDia = document.createElement('div');
                numDia.className = 'numero-dia';
                numDia.textContent = dia;
                td.appendChild(numDia);

                // Contenedor de eventos
                const eventosContainer = document.createElement('div');
                eventosContainer.className = 'eventos-container';
                td.appendChild(eventosContainer);

                // Resaltar día actual
                const hoy = new Date();
                if (dia === hoy.getDate() && mes === hoy.getMonth() && anio === hoy.getFullYear()) {
                    td.classList.add('hoy');
                }

                // Filtrar eventos para este día
                const fechaActual = `${anio}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
                const eventosDia = isAdmin ? 
                    eventos.filter(e => e.start === fechaActual) :
                    eventos.filter(e => e.start === fechaActual && e.es_propio);
                
                // Mostrar eventos (hasta el máximo permitido)
                eventosDia.slice(0, maxEventosVisibles).forEach(e => {
                    const evento = crearElementoEvento(e);
                    eventosContainer.appendChild(evento);
                });

                // Mostrar indicador si hay más eventos
                if (eventosDia.length > maxEventosVisibles) {
                    const masEventos = document.createElement('div');
                    masEventos.className = 'mas-eventos badge badge-secondary';
                    masEventos.textContent = `+${eventosDia.length - maxEventosVisibles}`;
                    masEventos.addEventListener('click', (e) => {
                        e.stopPropagation();
                        mostrarModalEventos(fechaActual, eventosDia);
                    });
                    eventosContainer.appendChild(masEventos);
                }

                tr.appendChild(td);
            }

            // Completar última fila
            if (tr.children.length > 0) {
                while (tr.children.length < 7) {
                    tr.appendChild(document.createElement('td'));
                }
                tbody.appendChild(tr);
            }

            tabla.appendChild(tbody);
            tarjeta.appendChild(tabla);
            contenedor.appendChild(tarjeta);
        }
    }

    // Función para crear elementos de evento
    function crearElementoEvento(evento) {
        const elemento = document.createElement('div');
        elemento.className = 'evento small';
        
        // Resaltar eventos propios
        if (evento.es_propio) {
            elemento.classList.add('evento-propio');
        }

        // Determinar icono según tipo de evento
        const icono = document.createElement('i');
        icono.className = 'fas mr-1 ';
        
        if (evento.title.includes('INICIO')) {
            icono.classList.add('fa-play', 'text-success');
        } else if (evento.title.includes('FIN')) {
            icono.classList.add('fa-stop', 'text-danger');
        } else {
            icono.classList.add('fa-exclamation-triangle', 'text-warning');
        }

        // Texto del evento (recortado para vista compacta)
        const texto = document.createElement('span');
        texto.textContent = evento.title.split(' - ')[0];
        
        elemento.appendChild(icono);
        elemento.appendChild(texto);
        elemento.title = evento.title; // Tooltip completo

        // Hacer clickable si tiene URL
        if (evento.url) {
            elemento.style.cursor = 'pointer';
            elemento.addEventListener('click', (e) => {
                e.stopPropagation();
                window.location.href = evento.url;
            });
        }

        return elemento;
    }

    // Función para mostrar modal con todos los eventos de un día
    function mostrarModalEventos(fecha, eventos) {
        const modal = document.createElement('div');
        modal.className = 'modal-eventos';
        
        const contenido = document.createElement('div');
        contenido.className = 'modal-contenido card';
        
        // Cabecera del modal
        const header = document.createElement('div');
        header.className = 'card-header d-flex justify-content-between align-items-center';
        
        const titulo = document.createElement('h5');
        titulo.className = 'mb-0';
        titulo.innerHTML = `<i class="fas fa-calendar-day"></i> Eventos para ${formatearFecha(fecha)}`;
        
        const cerrar = document.createElement('button');
        cerrar.className = 'close';
        cerrar.innerHTML = '&times;';
        cerrar.addEventListener('click', () => modal.remove());
        
        header.appendChild(titulo);
        header.appendChild(cerrar);
        contenido.appendChild(header);
        
        // Cuerpo del modal
        const body = document.createElement('div');
        body.className = 'card-body';
        
        if (eventos.length === 0) {
            body.textContent = 'No hay eventos para este día';
        } else {
            const lista = document.createElement('ul');
            lista.className = 'list-group list-group-flush';
            
            eventos.forEach(e => {
                const item = document.createElement('li');
                item.className = 'list-group-item';
                
                if (e.es_propio) {
                    item.classList.add('evento-propio');
                }
                
                const icono = document.createElement('i');
                icono.className = 'fas mr-2 ';
                
                if (e.title.includes('INICIO')) {
                    icono.classList.add('fa-play', 'text-success');
                } else if (e.title.includes('FIN')) {
                    icono.classList.add('fa-stop', 'text-danger');
                } else {
                    icono.classList.add('fa-exclamation-triangle', 'text-warning');
                }
                
                const texto = document.createElement('span');
                texto.textContent = e.title;
                
                item.appendChild(icono);
                item.appendChild(texto);
                
                if (e.url) {
                    item.style.cursor = 'pointer';
                    item.addEventListener('click', () => {
                        window.location.href = e.url;
                    });
                }
                
                lista.appendChild(item);
            });
            
            body.appendChild(lista);
        }
        
        contenido.appendChild(body);
        modal.appendChild(contenido);
        document.body.appendChild(modal);
        
        // Mostrar modal con animación
        setTimeout(() => modal.classList.add('show'), 10);
        
        // Cerrar al hacer clic fuera
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
                setTimeout(() => modal.remove(), 300);
            }
        });
    }

    // Función auxiliar para formatear fechas
    function formatearFecha(fechaStr) {
        const [anio, mes, dia] = fechaStr.split('-');
        return `${dia}/${mes}/${anio}`;
    }

    // Eventos para cambiar de año
    btnPrev.addEventListener('click', () => {
        anio--;
        anioActual.textContent = anio;
        renderCalendario(anio);
    });

    btnNext.addEventListener('click', () => {
        anio++;
        anioActual.textContent = anio;
        renderCalendario(anio);
    });

    // Renderizar calendario inicial
    renderCalendario(anio);
});