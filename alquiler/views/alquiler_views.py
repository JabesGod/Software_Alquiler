from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Alquiler, DetalleAlquiler, Acta
from alquiler.forms.alquiler_forms import (
    AlquilerForm,
    DocumentosAlquilerForm,
    FirmarContratoForm,
    DetalleAlquilerFormSet,
    DetalleAlquilerForm,
    ConvertirReservaForm
)
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
import re
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
import uuid
from PIL import Image
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.safestring import mark_safe
from django.conf import settings
import os
from django.urls import reverse
from alquiler.utils import crear_pago_inicial  # Asegúrate de importar
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
import logging
logger = logging.getLogger(__name__)



@login_required
@permission_required('alquiler.view_alquiler', raise_exception=True)
def listar_alquileres(request):
    alquileres = Alquiler.objects.all().select_related('cliente').prefetch_related('detalles__equipo').order_by('-id')
    estado = request.GET.get('estado')
    cliente = request.GET.get('cliente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    buscador_factura = request.GET.get('buscador_factura')
    
    if estado:
        alquileres = alquileres.filter(estado_alquiler=estado)
    if cliente:
        alquileres = alquileres.filter(cliente__nombre__icontains=cliente)
    if fecha_inicio:
        alquileres = alquileres.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        alquileres = alquileres.filter(fecha_fin__lte=fecha_fin)
    if buscador_factura:
        alquileres = alquileres.filter(numero_factura__icontains=buscador_factura)  # 👈 Changed to numero_factura
    
    # Paginación
    paginator = Paginator(alquileres, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'alquileres': page_obj,
        'estados_alquiler': Alquiler.ESTADO_ALQUILER,
        'estado_seleccionado': estado,  # 👈 Don't forget to add this for the template fix
        'is_paginated': page_obj.has_other_pages(),
        'buscador_factura': buscador_factura
    }
    
    return render(request, 'lista_alquileres.html', context)

@login_required
@permission_required('alquiler.export_alquiler', raise_exception=True)
def generar_pdf_acta(alquiler, request):
    html = render_to_string('acta_entrega.html', {
        'alquiler': alquiler,
        'request': request
    })

    result = BytesIO()
    pisa_status = pisa.CreatePDF(
        html, dest=result, encoding='UTF-8',
        link_callback=lambda uri, _: request.build_absolute_uri(uri)
    )

    if pisa_status.err:
        raise Exception("El PDF no se pudo generar correctamente. Revisa el template HTML.")

    result.seek(0)
    return result.getvalue()

@login_required
@permission_required('alquiler.add_alquiler', raise_exception=True)
def crear_alquiler(request):
    equipos_disponibles = Equipo.objects.filter(cantidad_disponible__gt=0)

    DetalleAlquilerFormSet = inlineformset_factory(
        Alquiler,
        DetalleAlquiler,
        form=DetalleAlquilerForm,
        extra=1,
        can_delete=True,
        fields=['equipo', 'numeros_serie', 'periodo_alquiler', 'cantidad', 'precio_unitario']
    )

    if request.method == 'POST':
        alquiler = Alquiler(es_reserva=False)
        form = AlquilerForm(request.POST, instance=alquiler)
        formset = DetalleAlquilerFormSet(request.POST, prefix='detalles')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    alquiler = form.save(commit=False)
                    alquiler.estado_alquiler = 'activo'
                    alquiler.es_reserva = False

                    if not alquiler.numero_factura:
                        raise ValidationError("Debe ingresar un número de factura para alquileres activos")

                    alquiler.save()

                    for detalle in formset.save(commit=False):
                        detalle.alquiler = alquiler

                        if isinstance(detalle.numeros_serie, str):
                            try:
                                detalle.numeros_serie = json.loads(detalle.numeros_serie)
                            except json.JSONDecodeError:
                                detalle.numeros_serie = [s.strip() for s in detalle.numeros_serie.split(',') if s.strip()]

                        if not isinstance(detalle.numeros_serie, list):
                            detalle.numeros_serie = []

                        detalle.cantidad = len(detalle.numeros_serie)

                        if not detalle.precio_unitario:
                            periodo = detalle.periodo_alquiler
                            equipo = detalle.equipo
                            detalle.precio_unitario = getattr(equipo, f'precio_{periodo}', 0) or 0

                        detalle.save()
                        detalle.equipo.actualizar_disponibilidad()

                    alquiler.calcular_precio_total()

                    # ✅ Crear el pago inicial automáticamente
                    crear_pago_inicial(alquiler, aprobado_por=request.user if request.user.is_authenticated else None)

                    messages.success(request, "Alquiler creado exitosamente.")
                    return redirect(f"{reverse('alquiler:listar_alquileres')}?alquiler_id={alquiler.id}")

            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            for f in formset:
                for field, errors in f.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en equipo ({field}): {error}")
    else:
        alquiler = Alquiler(es_reserva=False)
        form = AlquilerForm(
            initial={
                'fecha_inicio': timezone.now().date(),
                'fecha_fin': (timezone.now() + timezone.timedelta(days=7)).date()
            },
            instance=alquiler
        )
        formset = DetalleAlquilerFormSet(prefix='detalles')

    return render(request, 'crear_alquiler.html', {
        'form': form,
        'formset': formset,
        'equipos_disponibles': equipos_disponibles
    })



@login_required
@permission_required('alquiler.change_alquiler', raise_exception=True)
def editar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    equipos_disponibles = Equipo.objects.filter(cantidad_disponible__gt=0)
    equipos_en_alquiler = Equipo.objects.filter(detallealquiler__alquiler=alquiler).distinct()
    equipos_disponibles = equipos_disponibles.union(equipos_en_alquiler)

    DetalleAlquilerFormSet = inlineformset_factory(
        Alquiler,
        DetalleAlquiler,
        form=DetalleAlquilerForm,
        extra=0,
        can_delete=True,
        fields=['equipo', 'numeros_serie', 'periodo_alquiler', 'cantidad', 'precio_unitario']
    )

    if request.method == 'POST':
        form = AlquilerForm(request.POST, instance=alquiler)
        formset = DetalleAlquilerFormSet(request.POST, instance=alquiler, prefix='detalles')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    alquiler_actualizado = form.save(commit=False)

                    if not alquiler_actualizado.es_reserva and not alquiler_actualizado.numero_factura:
                        raise ValidationError("Debe ingresar un número de factura para alquileres activos")
                    alquiler_actualizado.save()

                    detalles_existentes = list(alquiler.detalles.all())
                    detalles = formset.save(commit=False)

                    # Procesar eliminaciones
                    for detalle in formset.deleted_objects:
                        if detalle.numeros_serie:
                            series = []
                            if isinstance(detalle.numeros_serie, str):
                                try:
                                    series = json.loads(detalle.numeros_serie)
                                except json.JSONDecodeError:
                                    series = [s.strip() for s in detalle.numeros_serie.split(',') if s.strip()]
                            elif isinstance(detalle.numeros_serie, list):
                                series = detalle.numeros_serie

                            detalle.equipo.actualizar_disponibilidad()
                        detalle.delete()

                    # Procesar detalles nuevos/modificados
                    for detalle in detalles:
                        detalle.alquiler = alquiler_actualizado

                        if isinstance(detalle.numeros_serie, str):
                            try:
                                detalle.numeros_serie = json.loads(detalle.numeros_serie)
                            except json.JSONDecodeError:
                                detalle.numeros_serie = [s.strip() for s in detalle.numeros_serie.split(',') if s.strip()]
                        if not isinstance(detalle.numeros_serie, list):
                            detalle.numeros_serie = []

                        detalle.cantidad = len(detalle.numeros_serie)

                        if not detalle.precio_unitario:
                            periodo = detalle.periodo_alquiler
                            detalle.precio_unitario = getattr(detalle.equipo, f'precio_{periodo}', 0) or 0

                        detalle.save()

                    # Actualizar disponibilidad
                    equipos_afectados = set(d.equipo for d in detalles)
                    equipos_afectados.update(d.equipo for d in formset.deleted_objects)
                    for equipo in equipos_afectados:
                        equipo.actualizar_disponibilidad()

                    alquiler_actualizado.calcular_precio_total()

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'redirect_url': reverse('alquiler:listar_alquileres')
                        })

                    messages.success(request, "Alquiler actualizado exitosamente!")
                    return redirect('alquiler:listar_alquileres')

            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'errors': {'general': str(e)}
                    }, status=400)

                messages.error(request, f"Error al actualizar: {str(e)}")
                logger.error(f"Error al editar alquiler: {str(e)}", exc_info=True)

        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = error_list
                for f in formset:
                    for field, error_list in f.errors.items():
                        errors[f"{f.prefix}-{field}"] = error_list
                return JsonResponse({'success': False, 'errors': errors}, status=400)

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            for f in formset:
                for field, errors in f.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en equipo ({field}): {error}")
    else:
        form = AlquilerForm(instance=alquiler)
        formset = DetalleAlquilerFormSet(instance=alquiler, prefix='detalles')

    equipos_json = json.dumps([
        {
            "id": detalle.id,
            "equipoId": detalle.equipo.id,
            "equipoTexto": f"{detalle.equipo.marca} {detalle.equipo.modelo}",
            "series": detalle.numeros_serie if isinstance(detalle.numeros_serie, list) else [],
            "periodo": detalle.periodo_alquiler,
            "periodoTexto": detalle.get_periodo_alquiler_display(),
            "precioUnitario": float(detalle.precio_unitario),
            "formIndex": i
        }
        for i, detalle in enumerate(alquiler.detalles.all())
    ])

    return render(request, 'editar_alquiler.html', {
        'form': form,
        'formset': formset,
        'alquiler': alquiler,
        'equipos_disponibles': equipos_disponibles,
        'equipos_json': mark_safe(equipos_json)
    })




@login_required
@permission_required('alquiler.add_alquiler', raise_exception=True)
def reservar_alquiler(request):
    equipos_disponibles = Equipo.objects.filter(cantidad_disponible__gt=0)
    DetalleAlquilerFormSet = inlineformset_factory(
        Alquiler, 
        DetalleAlquiler, 
        form=DetalleAlquilerForm,
        extra=1,
        can_delete=True,
        fields=['equipo', 'numeros_serie', 'periodo_alquiler', 'cantidad', 'precio_unitario']
    )

    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        form.instance.es_reserva = True
        formset = DetalleAlquilerFormSet(request.POST, prefix='detalles')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    alquiler = form.save(commit=False)
                    alquiler.estado_alquiler = 'reservado'
                    alquiler.es_reserva = True
                    alquiler.numero_factura = None  # Forzar a None para reservas
                    alquiler.save()
                    
                    # Procesar detalles
                    for detalle in formset.save(commit=False):
                        detalle.alquiler = alquiler
                        
                        if isinstance(detalle.numeros_serie, str):
                            try:
                                detalle.numeros_serie = json.loads(detalle.numeros_serie)
                            except json.JSONDecodeError:
                                detalle.numeros_serie = [s.strip() for s in detalle.numeros_serie.split(',') if s.strip()]
                        
                        if not isinstance(detalle.numeros_serie, list):
                            detalle.numeros_serie = []
                        
                        detalle.cantidad = len(detalle.numeros_serie)
                        
                        if not detalle.precio_unitario or str(detalle.precio_unitario).strip() == '':
                            periodo = detalle.periodo_alquiler
                            equipo = detalle.equipo
                            detalle.precio_unitario = getattr(equipo, f'precio_{periodo}', 0) or 0
                        
                        detalle.save()
                        detalle.equipo.estado = 'reservado'
                        detalle.equipo.save()
                    
                    messages.success(request, "Reserva creada exitosamente!")
                    return HttpResponseRedirect(f"{reverse('alquiler:listar_alquileres')}?alquiler_id={alquiler.id}")



            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
            
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error en equipo ({field}): {error}")
    else:
        form = AlquilerForm(initial={
            'fecha_inicio': timezone.now().date(),
            'fecha_fin': (timezone.now() + timezone.timedelta(days=7)).date()
        })
        # Ocultar campo de número de factura para reservas
        form.fields['numero_factura'].widget = forms.HiddenInput()
        form.initial['numero_factura'] = None
        
        formset = DetalleAlquilerFormSet(prefix='detalles')

    return render(request, 'reservar_alquiler.html', {
        'form': form,
        'formset': formset,
        'equipos_disponibles': equipos_disponibles
    })


@login_required
@permission_required('alquiler.change_alquiler', raise_exception=True)
def aprobar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    
    if alquiler.estado_alquiler in ['reservado', 'pendiente_aprobacion']:
        try:
            with transaction.atomic():
                alquiler.estado_alquiler = 'activo'
                alquiler.es_reserva = False
                alquiler.aprobado_por = str(request.user)
                
                # Generar número de factura solo al aprobar reserva
                if not alquiler.numero_factura:
                    last = Alquiler.objects.filter(es_reserva=False).order_by('-fecha_creacion').first()
                    last_number = 0

                if last and last.numero_factura:
        # Buscar número con regex: FACT-0042 o FACT0042
                    match = re.search(r'FACT[-]?(\d+)', last.numero_factura)
                    if match:
                        last_number = int(match.group(1))

                alquiler.numero_factura = f"FACT-{last_number + 1:04d}"
                alquiler.save()
                
                # Actualizar estado de equipos y calcular precios...
                
                messages.success(request, "Reserva aprobada y convertida a alquiler activo exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al aprobar la reserva: {str(e)}")
    else:
        messages.warning(request, "Solo se pueden aprobar reservas pendientes.")
    
    return redirect('alquiler:listar_alquileres')


@login_required
@permission_required('alquiler.view_equipo', raise_exception=True)
def series_disponibles(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    series = equipo.numeros_serie_lista()
    
    return JsonResponse({
        'series': series,
        'precio_dia': float(equipo.precio_dia),
        'precio_semana': float(equipo.precio_semana or 0),
        'precio_mes': float(equipo.precio_mes or 0),
        'precio_trimestre': float(equipo.precio_trimestre or 0),
        'precio_semestre': float(equipo.precio_semestre or 0),
        'precio_anio': float(equipo.precio_anio or 0),
        'cantidad_disponible': equipo.cantidad_disponible
    })

@login_required
@permission_required('alquiler.change_alquiler', raise_exception=True)
def finalizar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    alquiler.estado_alquiler = 'finalizado'
    alquiler.save()

    for detalle in alquiler.detalles.all():
        detalle.equipo.estado = 'disponible'
        detalle.equipo.save()

    messages.success(request, "Alquiler finalizado exitosamente.")
    return redirect('alquiler:listar_alquileres')

@login_required
@permission_required('alquiler.change_alquiler', raise_exception=True)
def renovar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    if request.method == 'POST':
        nueva_fecha_fin = request.POST.get('nueva_fecha_fin')
        alquiler.fecha_fin = nueva_fecha_fin
        alquiler.renovacion = True
        alquiler.save()
        messages.success(request, "Alquiler renovado exitosamente.")
        return redirect('alquiler:listar_alquileres')
    return render(request, 'renovar_alquiler.html', {'alquiler': alquiler})


@login_required
@permission_required('alquiler.view_acta', raise_exception=True)
def generar_acta_entrega(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    
    # Renderizar template con el contexto necesario
    html = render_to_string('acta_entrega.html', {
        'alquiler': alquiler,
        'request': request  # Pasar el request para construir URLs absolutas
    })
    
    # Crear respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="acta_entrega_{alquiler.id}.pdf"'
    
    # Convertir HTML a PDF
    result = BytesIO()
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='UTF-8',
        link_callback=lambda uri, _: request.build_absolute_uri(uri))
    
    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    
    return response

@login_required
@permission_required('alquiler.view_acta', raise_exception=True)
def generar_acta_devolucion(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    
    # Renderizar template
    html = render_to_string('acta_devolucion.html', {
        'alquiler': alquiler,
        'fecha_actual': timezone.now().date(),
        'request': request
    })
    
    # Generar PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html,
        dest=pdf_buffer,
        encoding='UTF-8',
        link_callback=lambda uri, _: request.build_absolute_uri(uri)
    )
    
    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)
    
    # Guardar el acta en el historial
    from django.core.files.base import ContentFile
    pdf_content = ContentFile(pdf_buffer.getvalue())
    
    acta = Acta.objects.create(
        alquiler=alquiler,
        tipo='devolucion'
    )
    acta.archivo.save(f'acta_devolucion_{alquiler.id}_{timezone.now().date()}.pdf', pdf_content)
    
    # Preparar respuesta para descarga
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="acta_devolucion_{alquiler.id}.pdf"'
    return response


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

@login_required
@permission_required('alquiler.view_alquiler', raise_exception=True)
def detalle_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    
    # Obtener historial de actas (usando el modelo unificado)
    historial_entregas = Acta.objects.filter(
        alquiler=alquiler, 
        tipo='entrega'
    ).order_by('-fecha_creacion')[:3]
    
    historial_devoluciones = Acta.objects.filter(
        alquiler=alquiler, 
        tipo='devolucion'
    ).order_by('-fecha_creacion')[:3]
    
    # Obtener historial de contratos
    historial_contratos = Contrato.objects.filter(
    alquiler=alquiler
    ).order_by('-fecha_contratacion')[:3]

    
    context = {
        'alquiler': alquiler,
        'historial_entregas': historial_entregas,
        'historial_devoluciones': historial_devoluciones,
        'historial_contratos': historial_contratos,
    }
    
    return render(request, 'detalle_alquiler.html', context)

@login_required
@permission_required('alquiler.view_alquiler', raise_exception=True)
def calendario_alquileres(request):
    alquileres = Alquiler.objects.filter(estado_alquiler='activo').prefetch_related('detalles__equipo')
    eventos = []

    for alquiler in alquileres:
        # Obtener resumen de equipos del alquiler
        equipos = [f"{detalle.equipo.marca} {detalle.equipo.modelo}" for detalle in alquiler.detalles.all()]
        equipos_str = " | ".join(equipos) if equipos else "Sin equipos"

        eventos.append({
            "title": f"{equipos_str} - {alquiler.cliente.nombre} - INICIO",
            "start": alquiler.fecha_inicio.strftime("%Y-%m-%d"),
            "color": "#28a745",
            "url": f"/alquileres/{alquiler.id}/detalle/"
        })

        eventos.append({
            "title": f"{equipos_str} - {alquiler.cliente.nombre} - FIN",
            "start": alquiler.fecha_fin.strftime("%Y-%m-%d"),
            "color": "#dc3545",
            "url": f"/alquileres/{alquiler.id}/detalle/"
        })

        # Evento de aviso por vencer (3 días antes)
        fecha_aviso = alquiler.fecha_fin - timedelta(days=3)
        eventos.append({
            "title": f"{equipos_str} - {alquiler.cliente.nombre} - POR VENCER",
            "start": fecha_aviso.strftime("%Y-%m-%d"),
            "color": "#ffc107",
            "url": f"/alquileres/{alquiler.id}/detalle/"
        })

    eventos_json = json.dumps(eventos)
    return render(request, "calendario.html", {
        "eventos_json": eventos_json,
        "current_year": datetime.now().year
    })

@login_required
@permission_required('alquiler.change_alquiler', raise_exception=True)
def cancelar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    if alquiler.estado_alquiler != 'cancelado':
        alquiler.estado_alquiler = 'cancelado'
        alquiler.save()

        for detalle in alquiler.detalles.all():
            detalle.equipo.estado = 'disponible'
            detalle.equipo.save()

        messages.warning(request, "Alquiler cancelado.")
    else:
        messages.info(request, "Este alquiler ya estaba cancelado.")
    return redirect('alquiler:listar_alquileres')

@login_required
@permission_required('alquiler.add_contrato', raise_exception=True)
def crear_contrato(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)

    if hasattr(alquiler, 'contrato'):
        messages.warning(request, "Este alquiler ya tiene un contrato generado.")
        return redirect('alquiler:detalle_alquiler', id=alquiler.id)

    if not alquiler.detalles.exists():
        messages.error(request, "No hay equipos asociados a este alquiler.")
        return redirect('alquiler:detalle_alquiler', id=alquiler.id)

    # Validar que el alquiler tenga un número de factura
    if not alquiler.numero_factura:
        messages.error(request, "No se puede crear el contrato: el número de factura está vacío.")
        return redirect('alquiler:detalle_alquiler', id=alquiler.id)

    contrato = Contrato.objects.create(alquiler=alquiler)
    messages.success(request, "Contrato creado correctamente. Ahora debe ser firmado.")
    return redirect('alquiler:firmar_contrato', id=alquiler.id)


@login_required
@permission_required('alquiler.change_contrato', raise_exception=True)
def firmar_contrato(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)
    contrato = get_object_or_404(Contrato, alquiler=alquiler)

    if request.method == 'POST':
        firma_file = request.FILES.get('firma_imagen')
        firma_data = request.POST.get('firma_data')
        firma_representante_file = request.FILES.get('firma_representante_imagen')
        firma_representante_data = request.POST.get('firma_representante_data')
        print(f"Firma data recibida: {firma_data is not None}")  # Debug
        print(f"Firma representante data recibida: {firma_representante_data is not None}")  # D
        # Validación básica de firmas
        if not (firma_file or firma_data):
            messages.error(request, "Debe proporcionar la firma del arrendatario")
            return render(request, 'firmar_contrato.html', {'alquiler': alquiler, 'contrato': contrato})

        if not (firma_representante_file or firma_representante_data):
            messages.error(request, "Debe proporcionar la firma del arrendador")
            return render(request, 'firmar_contrato.html', {'alquiler': alquiler, 'contrato': contrato})

        try:
            # Procesar firma del cliente (arrendatario)
            if firma_file:
                # Redimensionar imagen antes de guardar
                img = Image.open(firma_file)
                
                # Convertir a RGBA si es PNG para mantener transparencia
                if img.format == 'PNG':
                    img = img.convert('RGBA')
                    background = Image.new('RGBA', img.size, (255, 255, 255))
                    img = Image.alpha_composite(background, img)
                    img = img.convert('RGB')
                
                # Redimensionar manteniendo relación de aspecto
                img.thumbnail((300, 150), Image.LANCZOS)
                
                # Guardar imagen optimizada
                output = BytesIO()
                img.save(output, format='PNG', quality=90)
                output.seek(0)
                
                contrato.firma_cliente.save(
                    f"firma_cliente_{alquiler.id}.png", 
                    ContentFile(output.read()), 
                    save=False
                )
                
            elif firma_data and "base64" in firma_data:
                # Procesar firma dibujada
                format, imgstr = firma_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Decodificar imagen base64
                img_data = base64.b64decode(imgstr)
                img = Image.open(BytesIO(img_data))
                
                # Crear fondo blanco para firmas transparentes
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Redimensionar
                img.thumbnail((300, 150), Image.LANCZOS)
                
                # Guardar
                output = BytesIO()
                img.save(output, format='PNG', quality=90)
                output.seek(0)
                
                contrato.firma_cliente.save(
                    f"firma_cliente_dibujada_{alquiler.id}.png",
                    ContentFile(output.read()),
                    save=False
                )

            # Procesar firma del representante (arrendador)
            if firma_representante_file:
                # Redimensionar imagen antes de guardar
                img = Image.open(firma_representante_file)
                
                # Manejar transparencia para PNG
                if img.format == 'PNG':
                    img = img.convert('RGBA')
                    background = Image.new('RGBA', img.size, (255, 255, 255))
                    img = Image.alpha_composite(background, img)
                    img = img.convert('RGB')
                
                # Redimensionar
                img.thumbnail((300, 150), Image.LANCZOS)
                
                # Guardar
                output = BytesIO()
                img.save(output, format='PNG', quality=90)
                output.seek(0)
                
                contrato.firma_representante.save(
                    f"firma_representante_{alquiler.id}.png",
                    ContentFile(output.read()),
                    save=False
                )
                
            elif firma_representante_data and "base64" in firma_representante_data:
                # Procesar firma dibujada
                format, imgstr = firma_representante_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Decodificar imagen base64
                img_data = base64.b64decode(imgstr)
                img = Image.open(BytesIO(img_data))
                
                # Crear fondo blanco para firmas transparentes
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Redimensionar
                img.thumbnail((300, 150), Image.LANCZOS)
                
                # Guardar
                output = BytesIO()
                img.save(output, format='PNG', quality=90)
                output.seek(0)
                
                contrato.firma_representante.save(
                    f"firma_representante_dibujada_{alquiler.id}.png",
                    ContentFile(output.read()),
                    save=False
                )

            # Actualizar fecha de firma
            contrato.fecha_firma = timezone.now().date()
            contrato.save()

            # Generar documento PDF con las firmas
            if contrato.generar_documento_contrato():
                messages.success(request, "¡Contrato firmado y generado correctamente!")
                return redirect('alquiler:detalle_alquiler', id=alquiler.id)
            else:
                messages.error(request, "Error al generar el documento PDF del contrato")
                return render(request, 'firmar_contrato.html', {'alquiler': alquiler, 'contrato': contrato})

        except Exception as e:
            messages.error(request, f"Error al procesar las firmas: {str(e)}")
            return render(request, 'firmar_contrato.html', {'alquiler': alquiler, 'contrato': contrato})

    # GET request - mostrar formulario de firma
    return render(request, 'firmar_contrato.html', {
        'alquiler': alquiler,
        'contrato': contrato
    })

@login_required
@permission_required('alquiler.change_contrato', raise_exception=True)
def renovar_contrato(request, id):
    alquiler_original = get_object_or_404(Alquiler, id=id)

    # Verificar contrato existente
    if not hasattr(alquiler_original, 'contrato'):
        messages.error(request, "El alquiler original no tiene contrato asociado.")
        return redirect('alquiler:detalle_alquiler', id=alquiler_original.id)

    if alquiler_original.estado_alquiler not in ['activo', 'finalizado']:
        messages.error(request, "Solo se pueden renovar alquileres activos o finalizados.")
        return redirect('alquiler:detalle_alquiler', id=alquiler_original.id)

    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    nuevo_alquiler = form.save(commit=False)
                    nuevo_alquiler.estado_alquiler = 'activo'
                    nuevo_alquiler.cliente = alquiler_original.cliente
                    nuevo_alquiler.renovacion = True
                    nuevo_alquiler.es_reserva = False  # Asegurar que no sea reserva

                    # Obtener nombre del usuario
                    user = request.user
                    nombre = f"{getattr(user, 'nombre', '')} {getattr(user, 'apellido', '')}".strip()
                    if not nombre:
                        nombre = getattr(user, 'nombre_usuario', '') or user.username
                    nuevo_alquiler.aprobado_por = nombre

                    # Tomar número de factura ingresado manualmente
                    nuevo_alquiler.numero_factura = form.cleaned_data.get('numero_factura')
                    if not nuevo_alquiler.numero_factura:
                        raise ValidationError("Debe ingresar un número de factura.")

                    # Guardar primero el alquiler para obtener ID
                    nuevo_alquiler.save()

                    # Copiar los detalles del alquiler anterior
                    for detalle in alquiler_original.detalles.all():
                        DetalleAlquiler.objects.create(
                            alquiler=nuevo_alquiler,
                            equipo=detalle.equipo,
                            numeros_serie=detalle.numeros_serie,
                            periodo_alquiler=detalle.periodo_alquiler,
                            cantidad=detalle.cantidad,
                            precio_unitario=detalle.precio_unitario
                        )
                        detalle.equipo.actualizar_disponibilidad()

                    # Clonar el contrato
                    contrato_original = alquiler_original.contrato
                    nuevo_contrato = Contrato.objects.create(
                        alquiler=nuevo_alquiler,
                        terminos_contrato=contrato_original.terminos_contrato,
                        fecha_contratacion=timezone.now().date()
                    )

                    # Generar el PDF del contrato con los datos actualizados
                    nuevo_contrato.generar_documento_contrato()

                    # Finalizar el alquiler anterior si aún está activo
                    if alquiler_original.estado_alquiler == 'activo':
                        alquiler_original.estado_alquiler = 'finalizado'
                        alquiler_original.save()

                    messages.success(request, "Contrato renovado correctamente. Ahora debe ser firmado.")
                    return redirect('alquiler:firmar_contrato', id=nuevo_alquiler.id)

            except Exception as e:
                messages.error(request, f"Error al renovar el contrato: {str(e)}")
                logger.error(f"Error renovando contrato: {str(e)}", exc_info=True)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        fecha_inicio = alquiler_original.fecha_fin
        fecha_fin = fecha_inicio + timedelta(days=30)
        if fecha_inicio < timezone.now().date():
            fecha_inicio = timezone.now().date()
            fecha_fin = fecha_inicio + timedelta(days=30)

        form = AlquilerForm(initial={
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'observaciones': f"Renovación del alquiler #{alquiler_original.id}",
            'renovacion': True
        })
        form.fields['cliente'].widget = forms.HiddenInput()
        form.fields['cliente'].required = False
        form.fields['numero_factura'].required = True
        form.fields['numero_factura'].widget = forms.TextInput(attrs={'class': 'form-control'})

    context = {
        'form': form,
        'alquiler_anterior': alquiler_original,
        'contrato_original': alquiler_original.contrato,
        'detalles_originales': alquiler_original.detalles.all(),
        'cliente_original': alquiler_original.cliente
    }

    return render(request, 'renovar_contrato.html', context)

@login_required
@permission_required('alquiler.delete_alquiler', raise_exception=True)
def eliminar_alquiler(request, id):
    alquiler = get_object_or_404(Alquiler, id=id)

    if request.method == 'POST':
        alquiler.delete()
        messages.success(request, "Alquiler eliminado correctamente.")
        return redirect('alquiler:listar_alquileres')

    return render(request, 'eliminar_alquiler.html', {'alquiler': alquiler})