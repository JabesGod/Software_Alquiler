from django.shortcuts import render, redirect, get_object_or_404
from alquiler.models import Equipo, Alquiler, Cliente, Pago
from alquiler.forms.equipo_forms import EquipoForm
import csv
from django.http import HttpResponse
from django.db import models
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.db.models import Count, Max
from ..models import Equipo, Alquiler
import json
from ..forms import EquipoForm, FotoEquipoFormSet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST


def listar_equipos(request):
    equipos = Equipo.objects.all()
    return render(request, 'lista.html', {'equipos': equipos})


def crear_equipo(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('listar_equipos')

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                equipo = form.save()
                messages.success(request, f'Equipo {equipo.marca} {equipo.modelo} creado exitosamente!')
                return redirect('detalle_equipo', id=equipo.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar el equipo: {str(e)}')
                # Reconstruir el formulario con los datos ingresados
                form = EquipoForm(request.POST, request.FILES)
    else:
        form = EquipoForm()
    
    return render(request, 'crear.html', {
        'form': form,
        'titulo': 'Crear Nuevo Equipo'
    })

def editar_equipo(request, id):
    equipo = get_object_or_404(Equipo, pk=id)
    
    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        formset = FotoEquipoFormSet(request.POST, request.FILES, instance=equipo)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Asegurar que solo haya una foto principal
            fotos_principales = equipo.fotos.filter(es_principal=True)
            if fotos_principales.count() > 1:
                # Mantener solo la más reciente como principal
                ultima_principal = fotos_principales.order_by('-id').first()
                equipo.fotos.exclude(id=ultima_principal.id).update(es_principal=False)
            
            messages.success(request, f'Equipo {equipo} actualizado exitosamente!')
            return redirect('detalle_equipo', pk=equipo.pk)
    else:
        form = EquipoForm(instance=equipo)
        formset = FotoEquipoFormSet(instance=equipo)
    
    return render(request, 'editar.html', {
        'form': form,
        'formset': formset,
        'equipo': equipo,
        'titulo': f'Editar Equipo: {equipo}'
    })

@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_equipo(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    
    try:
        # Eliminar también las fotos asociadas
        equipo.fotos.all().delete()
        equipo.delete()
        messages.success(request, f'El equipo {equipo.marca} {equipo.modelo} ha sido eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el equipo: {str(e)}')
    
    return redirect('listar_equipos')

def detalle_equipo(request, id):
    equipo = get_object_or_404(Equipo, id=id)
    historial = Alquiler.objects.filter(equipo=equipo).order_by('-fecha_inicio')[:5]
    
    # Obtener equipos similares (misma categoría o etiqueta)
    equipos_similares = Equipo.objects.filter(
        estado=equipo.estado
    ).exclude(id=equipo.id)[:8]  # Limitar a 8 resultados
    
    if 'quick-view' in request.path:
        return render(request, 'quick_view.html', {
            'equipo': equipo,
            'historial': historial
        })
    
    return render(request, 'detalle.html', {
        'equipo': equipo,
        'historial': historial,
        'equipos_similares': equipos_similares
    })

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
    fecha_aviso = timezone.now().date() + timedelta(days=3)
    proximos_a_vencer = Alquiler.objects.filter(
        fecha_fin=fecha_aviso,
        estado_alquiler='activo'
    )

    if not proximos_a_vencer.exists():
        print(f"📭 No hay alquileres por vencer en 3 días ({fecha_aviso})")
        return

    print(f"📨 Enviando alertas de vencimiento para: {fecha_aviso}")

    for alquiler in proximos_a_vencer:
        asunto = '⚠️ Aviso: Su alquiler vence en 3 días'
        mensaje = (
            f'Estimado/a {alquiler.cliente.nombre},\n\n'
            f'Le informamos que el alquiler del equipo "{alquiler.equipo}" '
            f'vencerá el día {alquiler.fecha_fin}.\n\n'
            'Por favor, realice la renovación o devolución del equipo a tiempo.\n\n'
            'Gracias,\nEquipo de Soporte'
        )

        try:
            send_mail(
                asunto,
                mensaje,
                'noreply@tusitio.com',  # asegúrate de tenerlo configurado en settings.py
                [alquiler.cliente.email],
                fail_silently=False,
            )
            print(f"✅ Alerta enviada a: {alquiler.cliente.email}")
        except Exception as e:
            print(f"❌ Error al enviar a {alquiler.cliente.email}: {e}")

def ejecutar_alertas_vencimiento(request):
    enviar_alertas_vencimiento()
    messages.success(request, "Se han procesado las alertas de vencimiento (3 días antes).")
    return redirect('dashboard_admin')  # cambia al nombre de tu vista de inicio

def equipos_mas_alquilados(request):
    # Obtener los 10 equipos más alquilados con información adicional
    equipos = (
        Equipo.objects.annotate(
            total_alquileres=Count('alquileres'),
            ultimo_alquiler_fecha=Max('alquileres__fecha_inicio')
        )
        .filter(total_alquileres__gt=0)
        .order_by('-total_alquileres')[:10]
    )
    
    # Obtener clientes frecuentes para cada equipo
    for equipo in equipos:
        # Obtenemos los 3 clientes que más han alquilado este equipo
        clientes = (
            Alquiler.objects
            .filter(equipo=equipo)
            .values('cliente__id', 'cliente__nombre')
            .annotate(total=Count('cliente'))
            .order_by('-total')[:3]
        )
        equipo.clientes_frecuentes = [c['cliente__nombre'] for c in clientes]
        
        # Obtenemos el último alquiler completo (si existe)
        ultimo_alquiler = Alquiler.objects.filter(equipo=equipo).order_by('-fecha_inicio').first()
        equipo.ultimo_alquiler = ultimo_alquiler
    
    # Preparar datos para el gráfico - CORREGIDO
    labels = [f"{e.marca} {e.modelo} (ID: {e.id})" for e in equipos]
    datos = [e.total_alquileres for e in equipos]
    
    # Serializa correctamente los datos para JavaScript
    labels_json = json.dumps(labels)
    datos_json = json.dumps(datos)
    
    return render(request, 'estadisticas.html', {
        'labels': labels_json,
        'datos': datos_json,
        'equipos': equipos
    })