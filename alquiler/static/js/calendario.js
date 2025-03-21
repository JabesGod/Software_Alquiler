// calendario.js
document.addEventListener('DOMContentLoaded', function () {
    const calendarEl = document.getElementById('calendar');

    const eventos = JSON.parse(calendarEl.getAttribute('data-eventos'));

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        events: eventos,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        navLinks: true,
        editable: false,
        selectable: true
    });

    calendar.render();
});
