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

    function renderCalendario(anio) {
        contenedor.innerHTML = '';
        const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

        for (let mes = 0; mes < 12; mes++) {
            const fecha = new Date(anio, mes, 1);
            const diasEnMes = new Date(anio, mes + 1, 0).getDate();
            const primerDia = fecha.getDay();

            const tarjeta = document.createElement('div');
            tarjeta.classList.add('mes');

            const titulo = document.createElement('div');
            titulo.classList.add('titulo-mes');
            titulo.textContent = meses[mes];
            tarjeta.appendChild(titulo);

            const tabla = document.createElement('table');
            const cabecera = document.createElement('thead');
            const filaCabecera = document.createElement('tr');

            ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa', 'Do'].forEach(dia => {
                const th = document.createElement('th');
                th.textContent = dia;
                filaCabecera.appendChild(th);
            });

            cabecera.appendChild(filaCabecera);
            tabla.appendChild(cabecera);

            const cuerpo = document.createElement('tbody');
            let fila = document.createElement('tr');
            let diaSemana = (primerDia + 6) % 7;

            for (let i = 0; i < diaSemana; i++) {
                fila.appendChild(document.createElement('td'));
            }

            for (let dia = 1; dia <= diasEnMes; dia++) {
                if (fila.children.length === 7) {
                    cuerpo.appendChild(fila);
                    fila = document.createElement('tr');
                }

                const celda = document.createElement('td');
                celda.classList.add('celda-dia');
                celda.innerHTML = `<div class="numero-dia">${dia}</div>`;

                const fechaActual = `${anio}-${String(mes + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
                const eventosDia = eventos.filter(e => e.start === fechaActual);

                eventosDia.forEach(e => {
                    const evento = document.createElement('div');
                    evento.classList.add('evento');
                    evento.textContent = e.title;
                    evento.style.backgroundColor = e.color;
                    evento.title = e.title;
                    if (e.url) {
                        evento.addEventListener('click', () => window.location.href = e.url);
                        evento.classList.add('evento-clickable');
                    }
                    celda.appendChild(evento);
                });

                fila.appendChild(celda);
            }

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

    renderCalendario(anio);
});
