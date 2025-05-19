from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Alquiler
from ..forms import AlquilerForm, DocumentosAlquilerForm, FirmarContratoForm
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit
from django.core.mail import send_mail
import json
from django.core.serializers.json import DjangoJSONEncoder
from ..models import Equipo, Contrato
from xhtml2pdf import pisa
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.timezone import now
import base64

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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="acta_entrega_{alquiler.id}.pdf"'

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)

    response.write(result.getvalue())
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
    eventos = []

    for alquiler in alquileres:
        eventos.append({
            "title": f"{alquiler.equipo.marca} {alquiler.equipo.modelo} - {alquiler.cliente.nombre} - INICIO",
            "start": alquiler.fecha_inicio.strftime("%Y-%m-%d"),
            "color": "#28a745",
            "url": f"/alquileres/{alquiler.id}/detalle/"
        })
        eventos.append({
            "title": f"{alquiler.equipo.marca} {alquiler.equipo.modelo} - {alquiler.cliente.nombre} - FIN",
            "start": alquiler.fecha_fin.strftime("%Y-%m-%d"),
            "color": "#dc3545",
            "url": f"/alquileres/{alquiler.id}/detalle/"
        })

    eventos_json = json.dumps(eventos)
    return render(request, "calendario.html", {"eventos_json": eventos_json})

def cancelar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    if alquiler.estado_alquiler != 'cancelado':
        alquiler.estado_alquiler = 'cancelado'
        alquiler.equipo.estado = 'disponible'
        alquiler.equipo.save()
        alquiler.save()
        messages.warning(request, "Alquiler cancelado.")
    else:
        messages.info(request, "Este alquiler ya estaba cancelado.")
    return redirect('listar_alquileres')

def reservar_alquiler(request):
    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        if form.is_valid():
            alquiler = form.save(commit=False)
            alquiler.estado_alquiler = 'reservado'
            alquiler.equipo.estado = 'reservado'
            alquiler.equipo.save()
            alquiler.save()
            messages.success(request, "Reserva realizada exitosamente.")
            return redirect('listar_alquileres')
    else:
        form = AlquilerForm()
    return render(request, 'reservar_alquiler.html', {'form': form})

def generar_acta_devolucion(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    html = render_to_string('acta_devolucion.html', {'alquiler': alquiler})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="acta_devolucion_{alquiler.id}.pdf"'

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)

    response.write(result.getvalue())
    return response


def crear_contrato(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)

    if hasattr(alquiler, 'contrato'):
        messages.warning(request, "Este alquiler ya tiene un contrato generado.")
        return redirect('detalle_alquiler', id=alquiler.id)

    terminos = f"""
    Contrato de alquiler entre {alquiler.cliente.nombre} y la empresa.
    Equipo: {alquiler.equipo.marca} {alquiler.equipo.modelo} (Serie: {alquiler.equipo.numero_serie})
    Desde {alquiler.fecha_inicio} hasta {alquiler.fecha_fin}.
    Precio total: ${alquiler.precio_total}.
    """

    # 1. Crear contrato primero
    contrato = Contrato.objects.create(
        alquiler=alquiler,
        terminos_contrato=terminos,
    )

    # 2. Renderizar HTML con contrato ya existente
    html = render_to_string('contrato_pdf.html', {
        'alquiler': alquiler,
        'contrato': contrato,
        'terminos': terminos,
        'fecha': now().date()
    })

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse("Error al generar contrato PDF", status=500)

    # 3. Guardar PDF en el contrato ya creado
    pdf_content = ContentFile(result.getvalue())
    nombre_archivo = f"contrato_alquiler_{alquiler.id}.pdf"
    contrato.documento_contrato.save(nombre_archivo, pdf_content)
    contrato.save()

    messages.success(request, "Contrato generado correctamente.")
    return redirect('detalle_alquiler', id=alquiler.id)


def firmar_contrato(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    contrato = getattr(alquiler, 'contrato', None)

    if not contrato:
        messages.error(request, "Este alquiler no tiene contrato generado.")
        return redirect('detalle_alquiler', id=alquiler.id)

    if request.method == 'POST':
        # Depuración - imprimir los datos recibidos
        print("POST recibido:", request.POST)
        print("FILES recibidos:", request.FILES)
        
        # Imagen subida
        firma_file = request.FILES.get('firma_imagen')

        # Firma desde canvas
        firma_data = request.POST.get('firma_data')
        
        print("Firma data:", "Recibida" if firma_data else "No recibida")

        if firma_file:
            contrato.firma_cliente = firma_file
            contrato.fecha_firma = timezone.now().date()
            contrato.save()
            messages.success(request, "Firma subida correctamente.")
            return redirect('detalle_alquiler', id=alquiler.id)

        elif firma_data and "base64" in firma_data:
            try:
                format, imgstr = firma_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f"firma_{alquiler.id}.{ext}")

                contrato.firma_cliente = data
                contrato.fecha_firma = timezone.now().date()
                contrato.save()
                messages.success(request, "Firma dibujada guardada correctamente.")
                return redirect('detalle_alquiler', id=alquiler.id)
            except Exception as e:
                print("Error al procesar firma:", str(e))
                messages.error(request, f"Error al procesar la firma: {str(e)}")
                return redirect('firmar_contrato', id=alquiler.id)
        else:
            messages.error(request, "Por favor, dibuja o sube una firma.")
            return redirect('firmar_contrato', id=alquiler.id)

    return render(request, 'firmar_contrato.html', {'alquiler': alquiler})

def renovar_contrato(request, id):
    alquiler_original = get_object_or_404(Alquiler, id=id)

    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        if form.is_valid():
            nuevo_alquiler = form.save(commit=False)
            nuevo_alquiler.estado_alquiler = 'activo'
            nuevo_alquiler.equipo = alquiler_original.equipo
            nuevo_alquiler.cliente = alquiler_original.cliente
            nuevo_alquiler.save()

            messages.success(request, "Alquiler renovado correctamente.")
            return redirect('crear_contrato', id=nuevo_alquiler.id)
    else:
        form = AlquilerForm(initial={
            'fecha_inicio': alquiler_original.fecha_fin,
            'fecha_fin': alquiler_original.fecha_fin,  # puedes dejar igual o +X días
            'precio_total': alquiler_original.precio_total,
        })

    return render(request, 'renovar_contrato.html', {
        'form': form,
        'alquiler_anterior': alquiler_original
    })

def eliminar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)

    if request.method == 'POST':
        alquiler.delete()
        messages.success(request, "Alquiler eliminado correctamente.")
        return redirect('listar_alquileres')

    return render(request, 'eliminar_alquiler.html', {'alquiler': alquiler})