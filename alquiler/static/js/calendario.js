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
    const maxEventosVisibles = 2;
    const diasSemana = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'];
    const nombresMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

    // Función para obtener el prefijo actual de la URL
    function getCurrentPrefix() {
        const currentPath = window.location.pathname;
        
        if (currentPath.startsWith('/guanabanazo')) {
            return '/guanabanazo';
        } else if (currentPath.startsWith('/gramabana20')) {
            return '/gramabana20';
        } else if (currentPath.startsWith('/v1')) {
            return '/v1';
        }
        
        return '';
    }

    // Función para construir URLs con el prefijo correcto
    function buildUrl(url) {
        if (!url) return '';
        
        if (url.startsWith('http')) {
            return url; // URL absoluta (externa)
        }
        
        const prefix = getCurrentPrefix();
        const normalizedUrl = url.replace(/^\/*/, ''); // Eliminar barras iniciales
        
        return `${prefix}/${normalizedUrl}`;
    }

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
            let diaSemana = (primerDia + 6) % 7;

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

                // Número del día
                celda.innerHTML = `<div class="numero-dia">${dia}</div>`;

                // Contenedor para eventos
                const eventosContainer = document.createElement('div');
                eventosContainer.classList.add('eventos-container');
                celda.appendChild(eventosContainer);

                // Resaltar día actual
                const hoy = new Date();
                if (dia === hoy.getDate() && mes === hoy.getMonth() && anio === hoy.getFullYear()) {
                    celda.classList.add('hoy');
                }

                const fechaActual = `${anio}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
                const eventosDia = eventos.filter(e => e.start === fechaActual);
                const totalEventos = eventosDia.length;
                const eventosMostrar = eventosDia.slice(0, maxEventosVisibles);

                // Mostrar eventos visibles
                eventosMostrar.forEach(e => {
                    const evento = document.createElement('div');
                    evento.classList.add('evento');

                    // Determinar tipo de evento
                    if (e.title.includes('INICIO')) {
                        evento.classList.add('evento-inicio');
                        evento.innerHTML = `<i class="fas fa-play"></i><span>${e.title.split(' - ')[0]}</span>`;
                    } else if (e.title.includes('FIN')) {
                        evento.classList.add('evento-fin');
                        evento.innerHTML = `<i class="fas fa-stop"></i><span>${e.title.split(' - ')[0]}</span>`;
                    } else {
                        evento.classList.add('evento-aviso');
                        evento.innerHTML = `<i class="fas fa-exclamation"></i><span>${e.title.split(' - ')[0]}</span>`;
                    }

                    evento.title = e.title; // Tooltip con info completa

                    // Verificar que la URL existe y es válida antes de asignar el evento click
                    if (e.url && typeof e.url === 'string' && e.url.trim() !== '') {
                        evento.style.cursor = 'pointer';
                        evento.addEventListener('click', (ev) => {
                            ev.stopPropagation();
                            window.location.href = buildUrl(e.url);
                        });
                    } else {
                        evento.style.cursor = 'default';
                    }

                    eventosContainer.appendChild(evento);
                });

                // Mostrar indicador si hay más eventos
                if (totalEventos > maxEventosVisibles) {
                    const masEventos = document.createElement('div');
                    masEventos.classList.add('mas-eventos');
                    masEventos.textContent = `+${totalEventos - maxEventosVisibles}`;
                    masEventos.addEventListener('click', (e) => {
                        e.stopPropagation();
                        mostrarModalEventos(fechaActual, eventosDia);
                    });
                    eventosContainer.appendChild(masEventos);
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

    function mostrarModalEventos(fecha, eventos) {
        const modal = document.createElement('div');
        modal.className = 'modal-eventos active';
        
        const contenido = document.createElement('div');
        contenido.className = 'modal-contenido';
        
        // Título con la fecha
        const titulo = document.createElement('h3');
        titulo.className = 'modal-titulo';
        titulo.innerHTML = `<i class="fas fa-calendar-day"></i>Eventos para ${formatearFecha(fecha)}`;
        contenido.appendChild(titulo);
        
        // Lista de eventos
        const lista = document.createElement('ul');
        lista.className = 'lista-eventos';
        
        eventos.forEach(e => {
            const item = document.createElement('li');
            
            if (e.title.includes('INICIO')) {
                item.className = 'evento-item evento-inicio-item';
                item.innerHTML = `<i class="fas fa-play"></i><span>${e.title}</span>`;
            } else if (e.title.includes('FIN')) {
                item.className = 'evento-item evento-fin-item';
                item.innerHTML = `<i class="fas fa-stop"></i><span>${e.title}</span>`;
            } else {
                item.className = 'evento-item evento-aviso-item';
                item.innerHTML = `<i class="fas fa-exclamation-triangle"></i><span>${e.title}</span>`;
            }
            
            // Manejo de URLs con prefijo dinámico
            if (e.url && typeof e.url === 'string' && e.url.trim() !== '') {
                item.style.cursor = 'pointer';
                item.addEventListener('click', () => {
                    window.location.href = buildUrl(e.url);
                });
            }
            
            lista.appendChild(item);
        });
        
        contenido.appendChild(lista);
        
        // Botón para cerrar
        const cerrar = document.createElement('span');
        cerrar.className = 'cerrar-modal';
        cerrar.innerHTML = '&times;';
        cerrar.addEventListener('click', () => {
            modal.classList.remove('active');
            setTimeout(() => {
                document.body.removeChild(modal);
            }, 300);
        });
        contenido.appendChild(cerrar);
        
        modal.appendChild(contenido);
        
        // Cerrar al hacer clic fuera del contenido
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                setTimeout(() => {
                    document.body.removeChild(modal);
                }, 300);
            }
        });
        
        document.body.appendChild(modal);
        
        // Forzar reflow para activar la transición
        setTimeout(() => {
            modal.style.display = 'flex';
        }, 10);
    }

    function formatearFecha(fechaStr) {
        const [anio, mes, dia] = fechaStr.split('-');
        return `${dia}/${mes}/${anio}`;
    }

    // Renderizar calendario inicial
    renderCalendario(anio);
});