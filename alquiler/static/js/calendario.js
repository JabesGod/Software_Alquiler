document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');

    // Obtiene los eventos desde el atributo data-events del elemento HTML
    const eventos = JSON.parse(calendarEl.getAttribute('data-eventos') || '[]');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        events: eventos
    });

    calendar.render();
});
