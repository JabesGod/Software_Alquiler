from django.shortcuts import render, redirect, get_object_or_404
from alquiler.models import Equipo, Alquiler, Cliente, Pago
from alquiler.forms.equipo_forms import EquipoForm
from django.db.models import Count
import csv
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from alquiler.models import Alquiler
from reportlab.pdfgen import canvas
from django.contrib import messages

def listar_equipos(request):
    equipos = Equipo.objects.all()
    return render(request, 'lista.html', {'equipos': equipos})

def crear_equipo(request):
    form = EquipoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_equipos')
    return render(request, 'crear.html', {'form': form})

def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    form = EquipoForm(request.POST or None, instance=equipo)
    if form.is_valid():
        form.save()
        return redirect('listar_equipos')
    return render(request, 'editar.html', {'form': form, 'equipo': equipo})

def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    historial = Alquiler.objects.filter(equipo=equipo)
    return render(request, 'detalle.html', {'equipo': equipo, 'historial': historial})

def equipos_disponibles(request):
    equipos = Equipo.objects.filter(estado='disponible')
    return render(request, 'lista.html', {'equipos': equipos})

def cambiar_estado_equipo(request, id, nuevo_estado):
    equipo = get_object_or_404(Equipo, id=id)
    equipo.estado = nuevo_estado
    equipo.save()
    return redirect('listar_equipos')


def equipos_por_estado(request, estado):
    equipos = Equipo.objects.filter(estado=estado)
    return render(request, 'lista.html', {'equipos': equipos})



def equipos_mas_alquilados(request):
    equipos = (
        Equipo.objects.annotate(total_alquileres=Count('alquileres'))
        .filter(total_alquileres__gt=0)
        .order_by('-total_alquileres')[:10]
    )

    print("Equipos más alquilados:", list(equipos))  # 🔥 Debug en consola

    labels = [f"{e.marca} {e.modelo}" for e in equipos]
    datos = [e.total_alquileres for e in equipos]

    print("Labels:", labels)  # 🔥 Debug en consola
    print("Datos:", datos)  # 🔥 Debug en consola

    return render(request, 'estadisticas.html', {
        'labels': labels,
        'datos': datos,
    })

def buscar_equipos(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    equipos = Equipo.objects.all()

    if query:
        equipos = equipos.filter
        (models.Q(marca__icontains=query) |
        models.Q(modelo__icontains=query) |
        models.Q(especificaciones__icontains=query) |
        models.Q(numero_serie__icontains=query))

    if estado:
        equipos = equipos.filter(estado=estado)

    return render(request, 'buscar.html', {'equipos': equipos, 'query': query})

def dashboard_admin(request):
    total_equipos = Equipo.objects.count()
    total_alquilados = Equipo.objects.filter(estado='alquilado').count()
    pagos_pendientes = Pago.objects.filter(estado_pago='pendiente').count()  # Ahora sí está importado
    clientes_verificados = Cliente.objects.filter(estado_verificacion='verificado').count()

    return render(request, 'dashboard.html', {
        'total_equipos': total_equipos,
        'total_alquilados': total_alquilados,
        'pagos_pendientes': pagos_pendientes,
        'clientes_verificados': clientes_verificados,
    })





def actualizar_estados_masivo(request):
    if request.method == 'POST':
        ids_equipos = request.POST.getlist('ids_equipos')
        nuevo_estado = request.POST.get('nuevo_estado')
        Equipo.objects.filter(id__in=ids_equipos).update(estado=nuevo_estado)
        return redirect('listar_equipos')
    equipos = Equipo.objects.all()
    return render(request, 'actualizar_masivo.html', {'equipos': equipos})


def exportar_equipos_csv(request):
    equipos = Equipo.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Marca', 'Modelo', 'Serie', 'Estado'])

    for eq in equipos:
        writer.writerow([eq.marca, eq.modelo, eq.numero_serie, eq.estado])

    return response


def error_404_view(request, exception):
    return render(request, '404.html', status=404)


def historial_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    historial = equipo.historial_alquileres()
    return render(request, 'historial_equipo.html', {
        'equipo': equipo,
        'historial': historial
    })

def proxima_disponibilidad(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    fecha_disponible = equipo.proxima_fecha_disponible()
    return render(request, 'proxima_disponibilidad.html', {
        'equipo': equipo,
        'fecha_disponible': fecha_disponible
    })

def exportar_equipos_json(request):
    equipos = Equipo.objects.all()
    data = [equipo.exportar_informacion() for equipo in equipos]
    return JsonResponse({'equipos': data}, safe=False)

def equipos_similares(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    similares = equipo.equipos_similares()
    return render(request, 'equipos_similares.html', {
        'equipo': equipo,
        'similares': similares
    })

def dashboard_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    datos = {
        'total_alquileres': equipo.total_alquileres(),
        'duracion_promedio_dias': equipo.duracion_promedio_alquiler(),
        'estado_actual': equipo.estado,
        'fecha_proxima_disponibilidad': equipo.proxima_fecha_disponible(),
    }
    return render(request, 'dashboard_equipo.html', {
        'equipo': equipo,
        'datos': datos
    })


def enviar_alertas_vencimiento():
    fecha_aviso = timezone.now().date() + timedelta(days=2)
    proximos_a_vencer = Alquiler.objects.filter(
        fecha_fin=fecha_aviso,
        estado_alquiler='activo'
    )

    if proximos_a_vencer.exists():
        print(f"Enviando alertas para alquileres que vencen el: {fecha_aviso}")
    else:
        print(f"No hay alquileres próximos a vencer para {fecha_aviso}")
        return

    for alquiler in proximos_a_vencer:
        asunto = '⚠️ Aviso: Vencimiento Próximo del Alquiler'
        mensaje = (f'Estimado {alquiler.cliente.nombre},\n\n'
                   f'El alquiler del equipo "{alquiler.equipo}" '
                   f'vence el día {alquiler.fecha_fin}.\n'
                   'Por favor, realice la devolución o renovación correspondiente.\n\n'
                   'Gracias,\nEquipo de soporte')

        try:
            send_mail(
                asunto,
                mensaje,
                'noreply@tusitio.com',  # Cambia esto por tu correo configurado
                [alquiler.cliente.email],
                fail_silently=False,
            )
            print(f"Alerta enviada exitosamente a {alquiler.cliente.email}")
        except Exception as e:
            print(f"Error al enviar correo a {alquiler.cliente.email}: {e}")


def ejecutar_alertas_vencimiento(request):
    enviar_alertas_vencimiento()
    messages.success(request, "Alertas enviadas correctamente.")
    return redirect('dashboard_admin')