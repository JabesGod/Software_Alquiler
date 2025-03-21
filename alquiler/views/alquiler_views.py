from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Alquiler
from ..forms import AlquilerForm, DocumentosAlquilerForm
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit
from django.core.mail import send_mail
import json
from django.core.serializers.json import DjangoJSONEncoder

# Listar alquileres
def listar_alquileres(request):
    alquileres = Alquiler.objects.all()
    return render(request, 'lista_alquileres.html', {'alquileres': alquileres})

# Crear alquiler
def crear_alquiler(request):
    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        if form.is_valid():
            alquiler = form.save(commit=False)
            alquiler.estado_alquiler = 'activo'
            alquiler.save()
            alquiler.equipo.estado = 'alquilado'
            alquiler.equipo.save()
            messages.success(request, "Alquiler registrado exitosamente.")
            return redirect('listar_alquileres')
    else:
        form = AlquilerForm()
    return render(request, 'crear_alquiler.html', {'form': form})

# Finalizar alquiler
def finalizar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    alquiler.estado_alquiler = 'finalizado'
    alquiler.save()
    alquiler.equipo.estado = 'disponible'
    alquiler.equipo.save()
    messages.success(request, "Alquiler finalizado exitosamente.")
    return redirect('listar_alquileres')

# Renovar alquiler
def renovar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    if request.method == 'POST':
        nueva_fecha_fin = request.POST.get('nueva_fecha_fin')
        alquiler.fecha_fin = nueva_fecha_fin
        alquiler.renovacion = True
        alquiler.save()
        messages.success(request, "Alquiler renovado exitosamente.")
        return redirect('listar_alquileres')
    return render(request, 'renovar_alquiler.html', {'alquiler': alquiler})

# Cargar documentos del alquiler
def subir_documentos_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    if request.method == 'POST':
        form = DocumentosAlquilerForm(request.POST, request.FILES, instance=alquiler)
        if form.is_valid():
            form.save()
            messages.success(request, "Documentos subidos correctamente.")
            return redirect('listar_alquileres')
    else:
        form = DocumentosAlquilerForm(instance=alquiler)
    return render(request, 'subir_documentos.html', {'form': form, 'alquiler': alquiler})


def generar_acta_entrega(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    html = render_to_string('acta_entrega.html', {'alquiler': alquiler})
    pdf = pdfkit.from_string(html, False)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="acta_entrega_{alquiler.id}.pdf"'

    return response

def aprobar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    alquiler.aprobado_por = request.user.username
    alquiler.save()
    messages.success(request, "Alquiler aprobado correctamente.")
    return redirect('listar_alquileres')



def alertas_devoluciones_proximas():
    proximos = Alquiler.objects.filter(
        fecha_fin=timezone.now().date() + timedelta(days=1),
        estado_alquiler='activo'
    )

    for alquiler in proximos:
        send_mail(
            'Recordatorio: Devolución próxima del equipo',
            f'Hola {alquiler.cliente.nombre}, recuerda devolver el equipo {alquiler.equipo} mañana ({alquiler.fecha_fin}).',
            'no-reply@tuempresa.com',
            [alquiler.cliente.email],
            fail_silently=False,
        )


def detalle_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    return render(request, 'detalle_alquiler.html', {'alquiler': alquiler})

def calendario_alquileres(request):
    alquileres = Alquiler.objects.filter(estado_alquiler='activo')
    
    eventos = [
        {
            "title": f"{alquiler.equipo.marca} {alquiler.equipo.modelo} - {alquiler.cliente.nombre}",
            "start": alquiler.fecha_inicio.strftime("%Y-%m-%d"),
            "end": alquiler.fecha_fin.strftime("%Y-%m-%d"),
            "color": "#28a745" if alquiler.estado_alquiler == "activo" else "#dc3545",
            "url": f"/alquileres/{alquiler.id}/detalle/"
        }
        for alquiler in alquileres
    ]

    return render(request, "calendario.html", {"eventos_json": json.dumps(eventos)})