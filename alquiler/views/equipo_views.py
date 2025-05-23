from django.shortcuts import render, redirect, get_object_or_404
from alquiler.models import Equipo, Alquiler, Cliente, Pago
from alquiler.forms.equipo_forms import EquipoForm
import csv
from django.db import models
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db.models import Count, Max
from ..models import Equipo, Alquiler, FotoEquipo
from ..forms import EquipoForm, FotoEquipoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.forms.models import inlineformset_factory
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render
import json
import xlsxwriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.db.models import Sum, Count, Avg, Max, F, Q, ExpressionWrapper, FloatField
from django.db.models.functions import ExtractMonth, ExtractYear, TruncMonth
from datetime import datetime
from decimal import Decimal

def listar_equipos(request):
    equipos = Equipo.objects.all()
    form = EquipoForm() if request.user.is_staff else None
    return render(request, 'lista.html', {'equipos': equipos, 'form': form})


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
    
    if not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar equipos.')
        return redirect('detalle_equipo', pk=equipo.pk)

    FotoEquipoFormSet = inlineformset_factory(
        Equipo, 
        FotoEquipo, 
        form=FotoEquipoForm, 
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        form = EquipoForm(request.POST, request.FILES, instance=equipo)
        formset = FotoEquipoFormSet(request.POST, request.FILES, instance=equipo)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            # Asegurar que solo haya una foto principal
            fotos_principales = equipo.fotos.filter(es_principal=True)
            if fotos_principales.count() > 1:
                ultima_principal = fotos_principales.order_by('-id').first()
                equipo.fotos.exclude(id=ultima_principal.id).update(es_principal=False)
            
            messages.success(request, f'Equipo {equipo} actualizado exitosamente!')
            return redirect('detalle_equipo', id=equipo.id)
    else:
        form = EquipoForm(instance=equipo)
        formset = FotoEquipoFormSet(instance=equipo)
    
    return render(request, 'editar.html', {
        'form': form,
        'formset': formset,
        'equipo': equipo,
        'titulo': f'Editar {equipo.marca} {equipo.modelo}'
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
        
        if not ids_equipos:
            messages.error(request, "Debes seleccionar al menos un equipo")
            return redirect('actualizar_estados_masivo')
        
        if not nuevo_estado:
            messages.error(request, "Debes seleccionar un estado válido")
            return redirect('actualizar_estados_masivo')
        
        # Validar que el estado sea uno de los permitidos
        estados_validos = [estado[0] for estado in Equipo.ESTADOS]
        if nuevo_estado not in estados_validos:
            messages.error(request, "Estado seleccionado no válido")
            return redirect('actualizar_estados_masivo')
        
        # Actualizar los equipos seleccionados
        equipos_actualizados = Equipo.objects.filter(id__in=ids_equipos)
        count = equipos_actualizados.update(estado=nuevo_estado)
        
        messages.success(request, f"Se actualizaron {count} equipos correctamente")
        return redirect('listar_equipos')
    
    # Obtener todos los equipos y los estados disponibles
    equipos = Equipo.objects.all().order_by('marca', 'modelo')
    estados = Equipo.ESTADOS  # Esto obtiene las tuplas (valor, nombre) de los estados
    
    return render(request, 'actualizar_masivo.html', {
        'equipos': equipos,
        'estados': estados  # Pasar los estados al template
    })


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
    # Obtener parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    marca = request.GET.get('tipo_equipo')
    agrupar_por = request.GET.get('agrupar_por', 'equipo')  # equipo o mes

    # Filtros para Equipo (relación con Alquileres)
    filtros_equipos = Q(alquileres__isnull=False)
    if fecha_inicio and fecha_fin:
        filtros_equipos &= Q(alquileres__fecha_inicio__gte=fecha_inicio, alquileres__fecha_fin__lte=fecha_fin)
    if marca:
        filtros_equipos &= Q(marca__iexact=marca)

    # Filtros para Alquiler directamente
    filtros_alquiler = Q()
    if fecha_inicio and fecha_fin:
        filtros_alquiler &= Q(fecha_inicio__gte=fecha_inicio, fecha_fin__lte=fecha_fin)

    # Redirigir si se agrupa por mes
    if agrupar_por == 'mes':
        return estadisticas_por_mes(request, filtros_alquiler)

    # Obtener los 10 equipos más alquilados
    equipos = (
        Equipo.objects.annotate(
            total_alquileres=Count('alquileres', filter=filtros_equipos),
            ingresos_generados=Coalesce(Sum('alquileres__precio_total', filter=filtros_equipos), Decimal('0.00')),
            precio_promedio=Coalesce(Avg('alquileres__precio_total', filter=filtros_equipos), Decimal('0.00')),
            ultimo_alquiler_fecha=Max('alquileres__fecha_inicio', filter=filtros_equipos)
        )
        .filter(total_alquileres__gt=0)
        .order_by('-total_alquileres')[:10]
    )

    total_equipos = Equipo.objects.count()
    total_alquileres = Alquiler.objects.filter(filtros_alquiler).count()
    total_clientes = Cliente.objects.filter(alquileres__in=Alquiler.objects.filter(filtros_alquiler)).distinct().count()
    ingresos_totales = Alquiler.objects.filter(filtros_alquiler).aggregate(
        total=Sum('precio_total')
    )['total'] or Decimal('0.00')

    marcas = Equipo.objects.values_list('marca', flat=True).distinct().order_by('marca')

    # Añadir datos personalizados a cada equipo
    for equipo in equipos:
        # Clientes frecuentes por equipo
        cliente_filtros = Q(equipo=equipo)
        if fecha_inicio and fecha_fin:
            cliente_filtros &= Q(fecha_inicio__gte=fecha_inicio, fecha_fin__lte=fecha_fin)

        clientes = (
            Alquiler.objects
            .filter(cliente_filtros)
            .values('cliente__id', 'cliente__nombre')
            .annotate(total=Count('cliente'))
            .order_by('-total')[:3]
        )
        equipo.clientes_frecuentes = [c['cliente__nombre'] for c in clientes]

        # Último alquiler
        equipo.ultimo_alquiler = (
            Alquiler.objects
            .filter(equipo=equipo)
            .order_by('-fecha_inicio')
            .first()
        )

    # Datos para gráficos
    labels = [f"{e.marca} {e.modelo}" for e in equipos]
    datos_alquileres = [e.total_alquileres for e in equipos]
    datos_ingresos = [float(e.ingresos_generados) for e in equipos]

    labels_json = json.dumps(labels)
    datos_alquileres_json = json.dumps(datos_alquileres)
    datos_ingresos_json = json.dumps(datos_ingresos)

    # Exportaciones
    if 'export' in request.GET:
        if request.GET['export'] == 'excel':
            return exportar_a_excel(equipos, labels, datos_alquileres, datos_ingresos)
        elif request.GET['export'] == 'pdf':
            return exportar_a_pdf(equipos, labels, datos_alquileres, datos_ingresos,
                                  total_equipos, total_alquileres, total_clientes, ingresos_totales)

    # Renderizar plantilla
    return render(request, 'estadisticas.html', {
        'labels': labels_json,
        'datos': datos_alquileres_json,
        'ingresos_equipos': datos_ingresos_json,
        'equipos': equipos,
        'total_equipos': total_equipos,
        'total_alquileres': total_alquileres,
        'total_clientes': total_clientes,
        'ingresos_totales': ingresos_totales,
        'marcas': marcas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'marca_seleccionada': marca,
        'agrupar_por': agrupar_por
    })

def estadisticas_por_mes(request, filtros_base):
    # Obtener alquileres agrupados por mes
    alquileres_por_mes = (
        Alquiler.objects
        .filter(filtros_base)
        .annotate(
            mes=ExtractMonth('fecha_inicio'),
            año=ExtractYear('fecha_inicio')
        )
        .values('mes', 'año')
        .annotate(
            total=Count('id'),
            ingresos=Sum('precio_total')
        )
        .order_by('año', 'mes')
    )
    
    # Preparar datos para los gráficos
    meses = [
        'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'
    ]
    
    labels = []
    datos_alquileres = []
    datos_ingresos = []
    
    for dato in alquileres_por_mes:
        labels.append(f"{meses[dato['mes']-1]} {dato['año']}")
        datos_alquileres.append(dato['total'])
        datos_ingresos.append(float(dato['ingresos']))
    
    # Obtener estadísticas generales
    total_equipos = Equipo.objects.count()
    total_alquileres = sum(datos_alquileres)
    total_clientes = Cliente.objects.filter(alquileres__in=Alquiler.objects.filter(filtros_base)).distinct().count()
    ingresos_totales = sum(datos_ingresos)
    
    # Obtener marcas para el filtro
    marcas = Equipo.objects.values_list('marca', flat=True).distinct().order_by('marca')
    
    # Serializar datos para JavaScript
    labels_json = json.dumps(labels)
    datos_alquileres_json = json.dumps(datos_alquileres)
    datos_ingresos_json = json.dumps(datos_ingresos)
    
    # Manejar exportación
    if 'export' in request.GET:
        if request.GET['export'] == 'excel':
            return exportar_a_excel_mensual(labels, datos_alquileres, datos_ingresos)
        elif request.GET['export'] == 'pdf':
            return exportar_a_pdf_mensual(labels, datos_alquileres, datos_ingresos, 
                                        total_equipos, total_alquileres, total_clientes, ingresos_totales)
    
    return render(request, 'estadisticas.html', {
        'labels': labels_json,
        'datos': datos_alquileres_json,
        'ingresos_equipos': datos_ingresos_json,
        'equipos': [],  # No mostramos tabla de equipos en vista mensual
        'total_equipos': total_equipos,
        'total_alquileres': total_alquileres,
        'total_clientes': total_clientes,
        'ingresos_totales': ingresos_totales,
        'marcas': marcas,
        'fecha_inicio': request.GET.get('fecha_inicio'),
        'fecha_fin': request.GET.get('fecha_fin'),
        'marca_seleccionada': request.GET.get('tipo_equipo'),
        'agrupar_por': 'mes',
        'vista_mensual': True
    })

def exportar_a_excel(equipos, labels, datos_alquileres, datos_ingresos):
    output = io.BytesIO()
    
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Estadísticas')
    
    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#3498db',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    data_format = workbook.add_format({
        'border': 1,
        'align': 'left'
    })
    
    number_format = workbook.add_format({
        'border': 1,
        'num_format': '#,##0'
    })
    
    currency_format = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00'
    })
    
    # Escribir encabezados
    worksheet.write_row(0, 0, [
        'Equipo', 'Total Alquileres', 'Ingresos Generados', 
        'Precio Promedio', 'Disponibilidad', 'Clientes Frecuentes'
    ], header_format)
    
    # Escribir datos
    for row_num, equipo in enumerate(equipos, start=1):
        clientes_frecuentes = ', '.join(equipo.clientes_frecuentes) if equipo.clientes_frecuentes else 'N/A'
        
        worksheet.write(row_num, 0, f"{equipo.marca} {equipo.modelo}", data_format)
        worksheet.write_number(row_num, 1, equipo.total_alquileres, number_format)
        worksheet.write_number(row_num, 2, float(equipo.ingresos_generados), currency_format)
        worksheet.write_number(row_num, 3, float(equipo.precio_promedio), currency_format)
        worksheet.write(row_num, 4, f"{equipo.cantidad_disponible}/{equipo.cantidad_total}", data_format)
        worksheet.write(row_num, 5, clientes_frecuentes, data_format)
    
    # Añadir gráficos al Excel
    chart_sheet = workbook.add_worksheet('Gráficos')
    
    # Gráfico de barras para alquileres
    chart_alquileres = workbook.add_chart({'type': 'column'})
    chart_alquileres.add_series({
        'name': 'Total Alquileres',
        'categories': f'=Estadísticas!$A$2:$A${len(equipos)+1}',
        'values': f'=Estadísticas!$B$2:$B${len(equipos)+1}',
        'data_labels': {'value': True},
        'fill': {'color': '#3498db'}
    })
    chart_alquileres.set_title({'name': 'Equipos más alquilados'})
    chart_alquileres.set_x_axis({'name': 'Equipos'})
    chart_alquileres.set_y_axis({'name': 'Número de alquileres'})
    chart_sheet.insert_chart('B2', chart_alquileres, {'x_offset': 25, 'y_offset': 10})
    
    # Gráfico de barras para ingresos
    chart_ingresos = workbook.add_chart({'type': 'column'})
    chart_ingresos.add_series({
        'name': 'Ingresos Generados',
        'categories': f'=Estadísticas!$A$2:$A${len(equipos)+1}',
        'values': f'=Estadísticas!$C$2:$C${len(equipos)+1}',
        'data_labels': {'value': True, 'num_format': '$#,##0.00'},
        'fill': {'color': '#2ecc71'}
    })
    chart_ingresos.set_title({'name': 'Ingresos por equipo'})
    chart_ingresos.set_x_axis({'name': 'Equipos'})
    chart_ingresos.set_y_axis({'name': 'Ingresos ($)'})
    chart_sheet.insert_chart('B20', chart_ingresos, {'x_offset': 25, 'y_offset': 10})
    
    # Ajustar anchos de columna
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 18)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 40)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=estadisticas_alquileres.xlsx'
    return response

def exportar_a_excel_mensual(labels, datos_alquileres, datos_ingresos):
    output = io.BytesIO()
    
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Estadísticas Mensuales')
    
    # Formatos
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#3498db',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'border': 1,
        'num_format': '#,##0',
        'align': 'center'
    })
    
    currency_format = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00',
        'align': 'center'
    })
    
    # Escribir encabezados
    worksheet.write_row(0, 0, [
        'Mes', 'Total Alquileres', 'Ingresos Generados'
    ], header_format)
    
    # Escribir datos
    for row_num, (mes, alquileres, ingresos) in enumerate(zip(labels, datos_alquileres, datos_ingresos), start=1):
        worksheet.write(row_num, 0, mes)
        worksheet.write_number(row_num, 1, alquileres, number_format)
        worksheet.write_number(row_num, 2, ingresos, currency_format)
    
    # Añadir gráficos al Excel
    chart_sheet = workbook.add_worksheet('Gráficos')
    
    # Gráfico de barras para alquileres
    chart_alquileres = workbook.add_chart({'type': 'column'})
    chart_alquileres.add_series({
        'name': 'Total Alquileres',
        'categories': f'=Estadísticas Mensuales!$A$2:$A${len(labels)+1}',
        'values': f'=Estadísticas Mensuales!$B$2:$B${len(labels)+1}',
        'data_labels': {'value': True},
        'fill': {'color': '#3498db'}
    })
    chart_alquileres.set_title({'name': 'Alquileres por mes'})
    chart_alquileres.set_x_axis({'name': 'Mes'})
    chart_alquileres.set_y_axis({'name': 'Número de alquileres'})
    chart_sheet.insert_chart('B2', chart_alquileres, {'x_offset': 25, 'y_offset': 10})
    
    # Gráfico de barras para ingresos
    chart_ingresos = workbook.add_chart({'type': 'column'})
    chart_ingresos.add_series({
        'name': 'Ingresos Generados',
        'categories': f'=Estadísticas Mensuales!$A$2:$A${len(labels)+1}',
        'values': f'=Estadísticas Mensuales!$C$2:$C${len(labels)+1}',
        'data_labels': {'value': True, 'num_format': '$#,##0.00'},
        'fill': {'color': '#2ecc71'}
    })
    chart_ingresos.set_title({'name': 'Ingresos por mes'})
    chart_ingresos.set_x_axis({'name': 'Mes'})
    chart_ingresos.set_y_axis({'name': 'Ingresos ($)'})
    chart_sheet.insert_chart('B20', chart_ingresos, {'x_offset': 25, 'y_offset': 10})
    
    # Ajustar anchos de columna
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 18)
    worksheet.set_column('C:C', 20)
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=estadisticas_mensuales.xlsx'
    return response

def exportar_a_pdf(equipos, labels, datos_alquileres, datos_ingresos, 
                  total_equipos, total_alquileres, total_clientes, ingresos_totales):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estadisticas_alquileres.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    elements.append(Paragraph("Estadísticas de Alquileres", styles['Title']))
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Resumen estadístico
    resumen_data = [
        ["Total Equipos", total_equipos],
        ["Total Alquileres", total_alquileres],
        ["Clientes Activos", total_clientes],
        ["Ingresos Totales", f"${ingresos_totales:,.2f}"]
    ]
    
    resumen_table = Table(resumen_data, colWidths=[200, 100])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))
    elements.append(resumen_table)
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Tabla de equipos
    if equipos:
        elements.append(Paragraph("Detalle por Equipo", styles['Heading2']))
        
        equipo_data = [["Equipo", "Alquileres", "Ingresos", "Precio Prom.", "Disponibilidad"]]
        
        for equipo in equipos:
            equipo_data.append([
                f"{equipo.marca} {equipo.modelo}",
                equipo.total_alquileres,
                f"${equipo.ingresos_generados:,.2f}",
                f"${equipo.precio_promedio:,.2f}",
                f"{equipo.cantidad_disponible}/{equipo.cantidad_total}"
            ])
        
        equipo_table = Table(equipo_data, colWidths=[180, 80, 90, 80, 100])
        equipo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        elements.append(equipo_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

def exportar_a_pdf_mensual(labels, datos_alquileres, datos_ingresos, 
                          total_equipos, total_alquileres, total_clientes, ingresos_totales):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="estadisticas_mensuales.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    elements.append(Paragraph("Estadísticas Mensuales de Alquileres", styles['Title']))
    elements.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Resumen estadístico
    resumen_data = [
        ["Total Equipos", total_equipos],
        ["Total Alquileres", total_alquileres],
        ["Clientes Activos", total_clientes],
        ["Ingresos Totales", f"${ingresos_totales:,.2f}"]
    ]
    
    resumen_table = Table(resumen_data, colWidths=[200, 100])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))
    elements.append(resumen_table)
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Tabla mensual
    elements.append(Paragraph("Detalle Mensual", styles['Heading2']))
    
    mensual_data = [["Mes", "Alquileres", "Ingresos"]]
    
    for mes, alquileres, ingresos in zip(labels, datos_alquileres, datos_ingresos):
        mensual_data.append([
            mes,
            alquileres,
            f"${ingresos:,.2f}"
        ])
    
    mensual_table = Table(mensual_data, colWidths=[120, 100, 120])
    mensual_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))
    elements.append(mensual_table)
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response