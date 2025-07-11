document.addEventListener('DOMContentLoaded', function () {
    const contenedor = document.getElementById('calendarioContainer');
    const anioActual = document.getElementById('anioActual');
    const btnPrev = document.getElementById('anioAnterior');
    const btnNext = document.getElementById('anioSiguiente');

    let anio = new Date().getFullYear();
    anioActual.textContent = anio;

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

    // Configuración
    const maxEventosVisibles = 2; // Máximo de eventos visibles por día
    const diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];
    const nombresMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    function renderCalendario(anio) {
        contenedor.innerHTML = '';
        
        for (let mes = 0; mes < 12; mes++) {
            const fecha = new Date(anio, mes, 1);
            const diasEnMes = new Date(anio, mes + 1, 0).getDate();
            const primerDia = fecha.getDay();

            // Crear elemento del mes
            const tarjeta = document.createElement('div');
            tarjeta.classList.add('mes');

            // Título del mes
            const titulo = document.createElement('div');
            titulo.classList.add('titulo-mes');
            titulo.textContent = nombresMeses[mes];
            tarjeta.appendChild(titulo);

            // Crear tabla del mes
            const tabla = document.createElement('table');
            
            // Cabecera con días de la semana
            const cabecera = document.createElement('thead');
            const filaCabecera = document.createElement('tr');
            
            diasSemana.forEach(dia => {
                const th = document.createElement('th');
                th.textContent = dia;
                filaCabecera.appendChild(th);
            });

            cabecera.appendChild(filaCabecera);
            tabla.appendChild(cabecera);

            // Cuerpo del calendario
            const cuerpo = document.createElement('tbody');
            let fila = document.createElement('tr');
            let diaSemana = (primerDia + 6) % 7; // Ajuste para que la semana empiece en Lunes

            // Celdas vacías para días del mes anterior
            for (let i = 0; i < diaSemana; i++) {
                fila.appendChild(document.createElement('td'));
            }

            // Días del mes actual
            for (let dia = 1; dia <= diasEnMes; dia++) {
                if (fila.children.length === 7) {
                    cuerpo.appendChild(fila);
                    fila = document.createElement('tr');
                }

                const celda = document.createElement('td');
                celda.classList.add('celda-dia');
                
                // Resaltar el día actual
                const hoy = new Date();
                if (dia === hoy.getDate() && mes === hoy.getMonth() && anio === hoy.getFullYear()) {
                    celda.classList.add('hoy');
                }
                
                // Número del día
                celda.innerHTML = `<div class="numero-dia">${dia}</div>`;

                // Formatear fecha para comparación (YYYY-MM-DD)
                const fechaActual = `${anio}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
                
                // Filtrar eventos para este día
                const eventosDia = eventos.filter(e => e.start === fechaActual);
                const totalEventos = eventosDia.length;
                const eventosMostrar = eventosDia.slice(0, maxEventosVisibles);

                // Mostrar eventos visibles
                eventosMostrar.forEach(e => {
                    const evento = crearElementoEvento(e);
                    celda.appendChild(evento);
                });

                // Mostrar indicador si hay más eventos
                if (totalEventos > maxEventosVisibles) {
                    const masEventos = document.createElement('div');
                    masEventos.classList.add('mas-eventos');
                    masEventos.textContent = `+${totalEventos - maxEventosVisibles} más`;
                    masEventos.addEventListener('click', (e) => {
                        e.stopPropagation();
                        mostrarModalEventos(fechaActual, eventosDia);
                    });
                    celda.appendChild(masEventos);
                }

                // Marcar día si tiene eventos
                if (totalEventos > 0) {
                    celda.classList.add('dia-con-eventos');
                }

                fila.appendChild(celda);
            }

            // Completar la última fila con celdas vacías si es necesario
            if (fila.children.length > 0) {
                while (fila.children.length < 7) {
                    fila.appendChild(document.createElement('td'));
                }
                cuerpo.appendChild(fila);
            }

            tabla.appendChild(cuerpo);
            tarjeta.appendChild(tabla);
            contenedor.appendChild(tarjeta);
        }
    }

    // Función para crear un elemento de evento
    function crearElementoEvento(evento) {
        const elemento = document.createElement('div');
        elemento.classList.add('evento');
        
        // Determinar icono según tipo de evento
        const icono = document.createElement('i');
        if (evento.title.includes('INICIO')) {
            icono.className = 'fas fa-play';
        } else if (evento.title.includes('FIN')) {
            icono.className = 'fas fa-stop';
        } else {
            icono.className = 'fas fa-calendar-day';
        }
        
        // Texto del evento (mostrar solo información clave)
        const texto = document.createElement('span');
        const partesTitulo = evento.title.split(' - ');
        texto.textContent = partesTitulo.slice(0, 2).join(' - '); // Muestra solo marca/modelo y cliente
        
        elemento.appendChild(icono);
        elemento.appendChild(document.createTextNode(' ')); // Espacio
        elemento.appendChild(texto);
        elemento.style.backgroundColor = evento.color;
        elemento.title = evento.title; // Para el tooltip
        
        // Hacer clickable si tiene URL
        if (evento.url) {
            elemento.addEventListener('click', (e) => {
                e.stopPropagation();
                window.location.href = evento.url;
            });
            elemento.classList.add('evento-clickable');
        }
        
        return elemento;
    }

    // Función para mostrar el modal con todos los eventos de un día
    function mostrarModalEventos(fecha, eventos) {
        const modal = document.createElement('div');
        modal.className = 'modal-eventos';
        
        const contenido = document.createElement('div');
        contenido.className = 'modal-contenido';
        
        // Título con la fecha
        const titulo = document.createElement('h3');
        titulo.textContent = `Eventos para ${formatearFecha(fecha)}`;
        contenido.appendChild(titulo);
        
        // Lista de eventos
        const lista = document.createElement('ul');
        lista.style.listStyle = 'none';
        lista.style.padding = '0';
        
        eventos.forEach(e => {
            const item = document.createElement('li');
            item.style.marginBottom = '8px';
            item.style.padding = '8px';
            item.style.borderRadius = '4px';
            item.style.backgroundColor = `${e.color}40`; // Añade transparencia
            item.style.borderLeft = `3px solid ${e.color}`;
            
            // Icono según tipo de evento
            const icono = document.createElement('i');
            if (e.title.includes('INICIO')) {
                icono.className = 'fas fa-play mr-2';
            } else if (e.title.includes('FIN')) {
                icono.className = 'fas fa-stop mr-2';
            } else {
                icono.className = 'fas fa-calendar-day mr-2';
            }
            
            // Texto completo del evento
            const texto = document.createElement('span');
            texto.textContent = e.title;
            
            item.appendChild(icono);
            item.appendChild(texto);
            
            // Hacer clickable si tiene URL
            if (e.url) {
                item.style.cursor = 'pointer';
                item.addEventListener('click', () => window.location.href = e.url);
            }
            
            lista.appendChild(item);
        });
        
        contenido.appendChild(lista);
        
        // Botón para cerrar
        const cerrar = document.createElement('span');
        cerrar.className = 'cerrar-modal';
        cerrar.innerHTML = '&times;';
        cerrar.addEventListener('click', () => document.body.removeChild(modal));
        contenido.appendChild(cerrar);
        
        modal.appendChild(contenido);
        
        // Cerrar al hacer clic fuera del contenido
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        document.body.appendChild(modal);
        modal.style.display = 'flex';
    }

    // Función auxiliar para formatear fechas
    function formatearFecha(fechaStr) {
        const [anio, mes, dia] = fechaStr.split('-');
        return `${dia}/${mes}/${anio}`;
    }

    // Renderizar calendario inicial
    renderCalendario(anio);
});


