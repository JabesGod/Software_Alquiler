document.addEventListener('DOMContentLoaded', function () {
    console.log("📅 Cargando el calendario...");

    const calendarEl = document.getElementById('calendar');

    if (!calendarEl) {
        console.error("⚠️ Elemento #calendar no encontrado en el DOM.");
        return;
    }

    let eventos = [];
    try {
        eventos = JSON.parse(calendarEl.getAttribute('data-eventos'));
        console.log("✅ Eventos cargados correctamente:", eventos);
    } catch (error) {
        console.error("❌ Error al cargar eventos:", error);
    }

    if (eventos.length === 0) {
        console.warn("⚠️ No hay eventos para mostrar en el calendario.");
    }

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'es',
        events: eventos,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        eventClick: function(info) {
            if (info.event.url) {
                window.location.href = info.event.url;
                info.jsEvent.preventDefault();
            }
        }
    });

    console.log("📆 Renderizando calendario...");
    calendar.render();
    console.log("✅ Calendario renderizado exitosamente.");
});