from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
import csv
import json
from ..models import Pago, Alquiler, Cliente
from ..forms import FiltroPagosForm, PagoForm, PagoParcialForm
from django.contrib import messages
from ..serializers import PagoSerializer, PagoDetalleSerializer
from ..utils import enviar_notificacion_pago
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models import Count, Sum

@login_required
@permission_required('alquiler.view_pago', raise_exception=True)
def listar_pagos(request):
    pagos = Pago.objects.select_related('alquiler', 'alquiler__cliente')
    
    # Filtros mejorados
    alquiler_id = request.GET.get('alquiler_id')
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if alquiler_id and alquiler_id.isdigit():
        pagos = pagos.filter(alquiler_id=int(alquiler_id))
    if estado:
        pagos = pagos.filter(estado_pago=estado)
    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)
    if fecha_fin:
        pagos = pagos.filter(fecha_pago__lte=fecha_fin)
    
    # Calcular totales
    total_pagado = pagos.filter(estado_pago='pagado').aggregate(
        Sum('monto'))['monto__sum'] or 0
    pagos_pendientes = pagos.filter(estado_pago='pendiente').count()
    pagos_vencidos = pagos.filter(
        estado_pago__in=['pendiente', 'parcial'],
        fecha_vencimiento__lt=timezone.now().date()
    ).count()
    pagos_parciales = pagos.filter(estado_pago='parcial').count()
    
    return render(request, 'lista_pagos.html', {
        'pagos': pagos,
        'total_pagado': total_pagado,
        'pagos_pendientes': pagos_pendientes,
        'pagos_vencidos': pagos_vencidos,
        'pagos_parciales': pagos_parciales,
        'estados_pago': Pago.ESTADO_PAGO
    })

@login_required
@permission_required('alquiler.view_pago', raise_exception=True)
@login_required
def pagos_vencidos(request):
    hoy = timezone.now().date()
    pagos = Pago.objects.filter(
        estado_pago__in=['pendiente', 'parcial'],
        fecha_vencimiento__lt=hoy
    ).order_by('fecha_vencimiento')
    
    total_vencido = pagos.aggregate(total=Sum('monto'))['total'] or 0
    
    return render(request, 'pagos_vencidos.html', {
        'pagos': pagos,
        'total_vencido': total_vencido,
        'titulo': 'Pagos Vencidos'
    })


@login_required
@permission_required('alquiler.change_pago', raise_exception=True)
def cambiar_estado_pago(request, pago_id, nuevo_estado):
    pago = get_object_or_404(Pago, id=pago_id)
    
    if nuevo_estado in dict(Pago.ESTADO_PAGO):
        pago.estado_pago = nuevo_estado
        pago.aprobado_por = request.user
        pago.save()
        
        # Verificar si completa el alquiler
        verificar_estado_pago_alquiler(pago.alquiler)
        
        messages.success(request, f'Estado del pago actualizado a {pago.get_estado_pago_display()}')
    else:
        messages.error(request, 'Estado inválido')
    
    return redirect('detalle_pago', pago_id=pago.id)

@login_required
@permission_required('alquiler.view_pago', raise_exception=True)
def pagos_proximos_vencer(request):
    hoy = timezone.now().date()
    fecha_limite = hoy + timedelta(days=3)  # Próximos 3 días
    
    pagos = Pago.objects.filter(
        estado_pago__in=['pendiente', 'parcial'],
        fecha_vencimiento__range=[hoy, fecha_limite]
    ).order_by('fecha_vencimiento')
    
    return render(request, 'pagos_proximos.html', {
        'pagos': pagos,
        'titulo': 'Pagos Próximos a Vencer'
    })

@login_required
@permission_required('alquiler.view_pago', raise_exception=True)
def detalle_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    
    if hasattr(pago.aprobado_por, 'get_full_name') and pago.aprobado_por.get_full_name():
        nombre_aprobador = pago.aprobado_por.get_full_name()
    elif hasattr(pago.aprobado_por, 'email'):
        nombre_aprobador = pago.aprobado_por.email
    else:
        nombre_aprobador = str(pago.aprobado_por)

    context = {
        'pago': pago,
        'alquiler': pago.alquiler,
        'cliente': pago.alquiler.cliente,
        'nombre_aprobador': nombre_aprobador,
    }
    return render(request, 'detalle_pago.html', context)


@login_required
@permission_required('alquiler.add_pago', raise_exception=True)
def registrar_pago(request):
    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.aprobado_por = request.user
            pago.save()
            
            # Actualizar estado del alquiler si es necesario
            if pago.estado_pago == 'pagado':
                pago.alquiler.estado_alquiler = 'finalizado'
                pago.alquiler.save()
            
            return redirect('detalle_pago', pago_id=pago.id)
    else:
        form = PagoForm()
    
    return render(request, 'registrar_pago.html', {'form': form})

@login_required
@permission_required('alquiler.change_pago', raise_exception=True)
def editar_pago(request, pago_id):
    print(f"===> Ingresando a editar_pago con ID: {pago_id}")
    pago = get_object_or_404(Pago, id=pago_id)
    print(f"Pago obtenido: {pago}")

    if request.method == 'POST':
        print("Método: POST")
        form = PagoForm(request.POST, request.FILES, instance=pago)
        if form.is_valid():
            print("Formulario válido")
            pago = form.save(commit=False)
            pago.aprobado_por = request.user
            print(f"Pago aprobado por: {pago.aprobado_por}")

            total_pagado = pago.alquiler.pagos.exclude(id=pago.id).aggregate(
                total=Sum('monto')
            )['total'] or Decimal('0.00')
            print(f"Total pagado antes del nuevo pago: {total_pagado}")
            total_pagado += pago.monto
            print(f"Total pagado incluyendo el nuevo monto: {total_pagado}")
            print(f"Precio total del alquiler: {pago.alquiler.precio_total}")

            if total_pagado >= pago.alquiler.precio_total:
                pago.estado_pago = 'pagado'
                pago.alquiler.estado_alquiler = 'finalizado'
                pago.alquiler.save()
                print("Pago completo. Alquiler finalizado.")
            else:
                pago.estado_pago = 'parcial'
                print("Pago parcial.")

            pago.save()
            print(f"Pago actualizado y guardado: {pago}")
            messages.success(request, 'Pago actualizado correctamente')
            return redirect('detalle_pago', pago_id=pago.id)
        else:
            print("Formulario inválido")
            print("Errores del formulario:", form.errors)
    else:
        print("Método: GET")
        form = PagoForm(instance=pago)
    
    context = {
        'form': form,
        'pago': pago,
        'titulo': f'Editar Pago #{pago.id}'
    }
    return render(request, 'editar_pago.html', context)


@login_required
@permission_required('alquiler.delete_pago', raise_exception=True)
def eliminar_pago(request, pago_id):
    print(f"===> Entrando a eliminar_pago con ID: {pago_id}")
    pago = get_object_or_404(Pago, id=pago_id)
    print(f"Pago obtenido: {pago}")

    if request.method == 'POST':
        print("Método: POST - eliminando pago...")
        pago.delete()
        print(f"Pago #{pago_id} eliminado.")
        messages.success(request, f'Pago #{pago_id} eliminado correctamente.')
        return redirect('lista_pagos')
    
    print("Método: GET - mostrando plantilla de confirmación")
    context = {
        'pago': pago,
        'titulo': f'Confirmar eliminación del Pago #{pago.id}'
    }
    return render(request, 'eliminar_pago.html', context)



@login_required
@permission_required('alquiler.view_factura', raise_exception=True)
def generar_factura_pdf(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    
    # Renderizar template
    template = get_template('factura_pdf.html')
    context = {
        'pago': pago,
        'alquiler': pago.alquiler,
        'cliente': pago.alquiler.cliente,
        'fecha': timezone.now().date(),
    }
    html = template.render(context)
    
    # Crear PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        pago.factura_generada = True
        pago.save()
        
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{pago.id}.pdf"'
        return response
    
    return HttpResponse("Error al generar el PDF", status=400)

# Funciones de utilidad
def verificar_morosidad_cliente(cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    pagos_vencidos = Pago.objects.filter(
        alquiler__cliente=cliente,
        estado_pago__in=['pendiente', 'parcial'],
        fecha_vencimiento__lt=timezone.now().date()
    ).exists()
    
    if pagos_vencidos:
        cliente.estado_verificacion = 'rechazado'
        cliente.moroso = True
        cliente.fecha_marcado_moroso = timezone.now().date()
        cliente.save()
        return True
    return False


@login_required
@permission_required('alquiler.view_pago', raise_exception=True)
def pagos_parciales(request):
    # Obtener solo pagos parciales
    pagos = Pago.objects.filter(estado_pago='parcial').order_by('-fecha_pago')
    
    # Calcular total parcial
    total_parcial = pagos.aggregate(total=Sum('monto'))['total'] or 0
    
    # Calcular saldo pendiente promedio
    saldos = []
    for pago in pagos:
        saldos.append(float(pago.alquiler.saldo_pendiente))
    
    saldo_promedio = sum(saldos) / len(saldos) if saldos else 0
    
    context = {
        'pagos': pagos,
        'total_parcial': total_parcial,
        'saldo_promedio': round(saldo_promedio, 2),
    }
    
    return render(request, 'pagos_parciales.html', context)

@login_required
@permission_required('alquiler.add_pago', raise_exception=True)
def registrar_pago_parcial(request):
    if request.method == 'POST':
        form = PagoParcialForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.estado_pago = 'parcial'  # Forzar estado parcial
            pago.save()
            
            messages.success(request, f'Pago parcial #{pago.id} registrado correctamente.')
            return redirect('detalle_pago', pago_id=pago.id)
    else:
        # Si viene con alquiler_id en los parámetros GET
        alquiler_id = request.GET.get('alquiler_id')
        initial = {}
        
        if alquiler_id:
            try:
                alquiler = Alquiler.objects.get(id=alquiler_id)
                initial = {
                    'alquiler': alquiler,
                    'monto': alquiler.saldo_pendiente * Decimal('0.5'),  # Sugerir 50% del saldo
                }
            except Alquiler.DoesNotExist:
                messages.error(request, 'El alquiler especificado no existe.')
        
        form = PagoParcialForm(initial=initial)
    
    context = {
        'form': form,
        'alquiler': Alquiler.objects.get(id=initial.get('alquiler')) if initial.get('alquiler') else None,
    }
    
    return render(request, 'registrar_pago_parcial.html', context)


@login_required
@permission_required('alquiler.view_pago', raise_exception=True)
def reportes_pagos(request):
    # Obtener todos los pagos inicialmente
    pagos = Pago.objects.all().order_by('-fecha_pago')
    
    # Configurar fechas por defecto (últimos 30 días)
    fecha_inicio_default = timezone.now().date() - timedelta(days=30)
    fecha_fin_default = timezone.now().date()
    
    # Procesar filtros del formulario
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    estado = request.GET.get('estado', '')
    metodo_pago = request.GET.get('metodo_pago', '')
    
    # Aplicar filtros
    if fecha_inicio:
        pagos = pagos.filter(fecha_pago__gte=fecha_inicio)
    else:
        fecha_inicio = fecha_inicio_default
        
    if fecha_fin:
        pagos = pagos.filter(fecha_pago__lte=fecha_fin)
    else:
        fecha_fin = fecha_fin_default
        
    if estado:
        pagos = pagos.filter(estado_pago=estado)
        
    if metodo_pago:
        pagos = pagos.filter(metodo_pago=metodo_pago)
    
    # Exportar a CSV si se solicita
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_pagos.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Fecha', 'Cliente', 'Alquiler', 'Monto', 
            'Método de Pago', 'Estado', 'Referencia'
        ])
        
        for pago in pagos:
            writer.writerow([
                pago.id,
                pago.fecha_pago.strftime('%d/%m/%Y'),
                pago.alquiler.cliente.nombre,
                pago.alquiler.id,
                pago.monto,
                pago.get_metodo_pago_display(),
                pago.get_estado_pago_display(),
                pago.referencia_transaccion or ''
            ])
        
        return response
    
    # Calcular totales y resúmenes
    total_pagado = pagos.aggregate(total=Sum('monto'))['total'] or 0
    total_pagos = pagos.count()
    promedio_pago = total_pagado / total_pagos if total_pagos > 0 else 0
    
    # Resumen por estado
    resumen_estados = pagos.values('estado_pago').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Resumen por método de pago
    resumen_metodos = pagos.values('metodo_pago').annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Obtener opciones para filtros
    estados = Pago.ESTADO_PAGO
    metodos_pago = Pago.METODOS
    
    context = {
        'pagos': pagos[:100],  # Limitar para la vista previa
        'total_pagado': total_pagado,
        'total_pagos': total_pagos,
        'promedio_pago': round(promedio_pago, 2),
        'resumen_estados': resumen_estados,
        'resumen_metodos': resumen_metodos,
        'estados': estados,
        'metodos_pago': metodos_pago,
        'fecha_inicio_default': fecha_inicio_default.strftime('%Y-%m-%d'),
        'fecha_fin_default': fecha_fin_default.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'reportes_pagos.html', context)

def verificar_estado_pago_alquiler(alquiler):
    total_pagado = alquiler.pagos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    
    if total_pagado >= alquiler.precio_total:
        alquiler.estado_alquiler = 'finalizado'
        alquiler.save()
        # Actualizar todos los pagos parciales a 'pagado'
        alquiler.pagos.filter(estado_pago='parcial').update(estado_pago='pagado')
        return True
    return False

@login_required
@permission_required('alquiler.change_pago', raise_exception=True)
def registrar_pago_contra_obligacion(request, pago_id):
    pago_obligacion = get_object_or_404(Pago, id=pago_id)
    
    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear el nuevo pago
            nuevo_pago = form.save(commit=False)
            nuevo_pago.aprobado_por = request.user
            
            # Actualizar la obligación original
            if pago_obligacion.monto == nuevo_pago.monto:
                # Pago completo - actualizar la obligación existente
                pago_obligacion.metodo_pago = nuevo_pago.metodo_pago
                pago_obligacion.referencia_transaccion = nuevo_pago.referencia_transaccion
                pago_obligacion.comprobante_pago = nuevo_pago.comprobante_pago
                pago_obligacion.notas = nuevo_pago.notas
                pago_obligacion.estado_pago = 'pagado' if nuevo_pago.estado_pago == 'pagado' else 'parcial'
                pago_obligacion.aprobado_por = request.user
                pago_obligacion.save()
                
                messages.success(request, 'Pago registrado correctamente actualizando la obligación existente')
                return redirect('detalle_pago', pago_id=pago_obligacion.id)
            else:
                # Pago parcial - crear nuevo registro y ajustar obligación
                pago_obligacion.monto -= nuevo_pago.monto
                if pago_obligacion.monto > 0:
                    pago_obligacion.estado_pago = 'parcial'
                pago_obligacion.save()
                
                nuevo_pago.alquiler = pago_obligacion.alquiler
                nuevo_pago.save()
                
                messages.success(request, 'Pago parcial registrado correctamente')
                return redirect('detalle_pago', pago_id=nuevo_pago.id)
    else:
        form = PagoForm(initial={
            'alquiler': pago_obligacion.alquiler,
            'monto': pago_obligacion.monto,
        })
    
    context = {
        'form': form,
        'pago_obligacion': pago_obligacion,
        'titulo': f'Registrar Pago para Obligación #{pago_obligacion.id}'
    }
    return render(request, 'registrar_pago_contra_obligacion.html', context)

class RegistrarPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Registra un nuevo pago para un alquiler.
        Puede ser un pago completo o parcial.
        """
        serializer = PagoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        alquiler = get_object_or_404(Alquiler, id=serializer.validated_data['alquiler_id'])
        monto = Decimal(serializer.validated_data['monto'])
        
        # Validar que el monto no exceda el saldo pendiente
        saldo_pendiente = alquiler.saldo_pendiente
        if monto > saldo_pendiente + Decimal('0.01'):  # Tolerancia para decimales
            return Response(
                {"error": f"El monto excede el saldo pendiente (${saldo_pendiente})"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Determinar estado del pago
        estado_pago = 'pagado' if monto >= saldo_pendiente else 'parcial'

        try:
            pago = Pago.objects.create(
                alquiler=alquiler,
                monto=monto,
                metodo_pago=serializer.validated_data['metodo_pago'],
                estado_pago=estado_pago,
                referencia_transaccion=serializer.validated_data.get('referencia_transaccion', ''),
                aprobado_por=request.user,
                fecha_vencimiento=timezone.now().date() + timedelta(days=15)  # 15 días para pagar
            )

            # Actualizar estado del alquiler si está completamente pagado
            if estado_pago == 'pagado':
                alquiler.estado_alquiler = 'finalizado'
                alquiler.save()
                # Marcar todos los pagos parciales como completados
                alquiler.pagos.filter(estado_pago='parcial').update(estado_pago='pagado')

            # Enviar notificación
            enviar_notificacion_pago(pago, request.user)

            return Response(PagoDetalleSerializer(pago).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Error al registrar el pago: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PagosAlquilerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, alquiler_id):
        """
        Obtiene todos los pagos de un alquiler específico
        """
        alquiler = get_object_or_404(Alquiler, id=alquiler_id)
        pagos = alquiler.pagos.all().order_by('-fecha_pago')
        serializer = PagoDetalleSerializer(pagos, many=True)
        
        data = {
            'pagos': serializer.data,
            'total_pagado': alquiler.total_pagado,
            'saldo_pendiente': alquiler.saldo_pendiente,
            'porcentaje_pagado': alquiler.porcentaje_pagado
        }
        
        return Response(data)


class PagoDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pago_id):
        """
        Obtiene los detalles de un pago específico
        """
        pago = get_object_or_404(Pago, id=pago_id)
        serializer = PagoDetalleSerializer(pago)
        return Response(serializer.data)

    def put(self, request, pago_id):
        """
        Actualiza un pago (por ejemplo, para aprobación/rechazo)
        """
        pago = get_object_or_404(Pago, id=pago_id)
        
        # Solo permitir actualizar ciertos campos
        data = request.data.copy()
        allowed_fields = ['estado_pago', 'referencia_transaccion', 'comprobante_pago', 'notas']
        for field in list(data.keys()):
            if field not in allowed_fields:
                data.pop(field)
        
        serializer = PagoDetalleSerializer(pago, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(aprobado_por=request.user)
        
        # Si se rechaza el pago, verificar si el cliente debe ser marcado como moroso
        if serializer.validated_data.get('estado_pago') == 'rechazado':
            verificar_morosidad_cliente(pago.alquiler.cliente.id)
        
        return Response(serializer.data)


class PagosPendientesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Lista todos los pagos pendientes con filtros opcionales
        """
        queryset = Pago.objects.filter(estado_pago__in=['pendiente', 'parcial'])
        
        # Filtros
        cliente_id = request.query_params.get('cliente_id')
        alquiler_id = request.query_params.get('alquiler_id')
        fecha_vencimiento = request.query_params.get('fecha_vencimiento')
        
        if cliente_id:
            queryset = queryset.filter(alquiler__cliente__id=cliente_id)
        if alquiler_id:
            queryset = queryset.filter(alquiler__id=alquiler_id)
        if fecha_vencimiento:
            queryset = queryset.filter(fecha_vencimiento=fecha_vencimiento)
        
        serializer = PagoDetalleSerializer(queryset.order_by('fecha_vencimiento'), many=True)
        return Response(serializer.data)


class GenerarFacturaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pago_id):
        """
        Genera una factura para un pago específico
        """
        pago = get_object_or_404(Pago, id=pago_id)
        
        # Aquí iría la lógica real para generar el PDF de la factura
        # Por ahora simulamos la generación
        factura_data = {
            "numero_factura": f"FACT-{pago.id:05d}",
            "fecha": timezone.now().date().strftime("%Y-%m-%d"),
            "cliente": pago.alquiler.cliente.nombre,
            "monto": pago.monto,
            "metodo_pago": pago.get_metodo_pago_display(),
            "referencia": pago.referencia_transaccion or "N/A"
        }
        
        pago.factura_generada = True
        pago.save()
        
        return Response({
            "mensaje": "Factura generada exitosamente",
            "factura": factura_data,
            "descarga_url": f"/api/pagos/{pago.id}/factura/pdf/"  # URL ficticia para descarga
        })


class PasarelaPagoView(APIView):
    def post(self, request):
        """
        Inicia un pago a través de una pasarela de pago externa
        """
        alquiler_id = request.data.get('alquiler_id')
        monto = request.data.get('monto')
        
        if not alquiler_id or not monto:
            return Response(
                {"error": "Se requieren alquiler_id y monto"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        alquiler = get_object_or_404(Alquiler, id=alquiler_id)
        
        # Validar que el monto no exceda el saldo pendiente
        if Decimal(monto) > alquiler.saldo_pendiente:
            return Response(
                {"error": f"El monto excede el saldo pendiente (${alquiler.saldo_pendiente})"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulación de integración con pasarela de pago
        # En producción, aquí se haría la conexión real con PayPal, Stripe, etc.
        payment_data = {
            "payment_id": f"pay_{timezone.now().timestamp()}",
            "status": "created",
            "approval_url": f"https://pasarela-pago.example.com/pay?amount={monto}&alquiler={alquiler_id}",
            "monto": monto,
            "moneda": "COP",
            "fecha_expiracion": (timezone.now() + timedelta(minutes=30)).isoformat()
        }
        
        # Guardar temporalmente la información del pago pendiente
        request.session['pending_payment'] = json.dumps({
            "alquiler_id": alquiler_id,
            "monto": monto,
            "payment_data": payment_data
        })
        
        return Response(payment_data)


class ProcesarPagoPasarelaView(APIView):
    def get(self, request):
        """
        Callback para procesar la respuesta de la pasarela de pago
        """
        payment_status = request.query_params.get('status')
        payment_id = request.query_params.get('payment_id')
        
        if not payment_status or not payment_id:
            return Response(
                {"error": "Faltan parámetros en la URL"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Recuperar datos del pago pendiente
        pending_payment = request.session.get('pending_payment')
        if not pending_payment:
            return Response(
                {"error": "No se encontró información del pago pendiente"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        payment_data = json.loads(pending_payment)
        alquiler = get_object_or_404(Alquiler, id=payment_data['alquiler_id'])
        
        if payment_status == 'approved':
            # Registrar el pago exitoso
            pago = Pago.objects.create(
                alquiler=alquiler,
                monto=payment_data['monto'],
                metodo_pago='tarjeta',  # o el método correspondiente
                estado_pago='pagado',
                referencia_transaccion=payment_id,
                fecha_vencimiento=timezone.now().date()
            )
            
            # Actualizar estado del alquiler si corresponde
            if alquiler.saldo_pendiente <= 0:
                alquiler.estado_alquiler = 'finalizado'
                alquiler.save()
            
            # Limpiar sesión
            del request.session['pending_payment']
            
            return Response({
                "status": "success",
                "message": "Pago registrado exitosamente",
                "pago_id": pago.id
            })
        
        return Response({
            "status": "error",
            "message": f"El pago no fue aprobado. Estado: {payment_status}"
        }, status=status.HTTP_400_BAD_REQUEST)


class RegistrarPagoParcialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Registra un pago parcial para un alquiler"""
        serializer = PagoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        alquiler = get_object_or_404(Alquiler, id=serializer.validated_data['alquiler_id'])
        monto = Decimal(serializer.validated_data['monto'])

        # Validar que el monto no exceda el saldo pendiente
        saldo_pendiente = alquiler.saldo_pendiente
        if monto >= saldo_pendiente:
            return Response(
                {"error": "Este endpoint es solo para pagos parciales. Use RegistrarPagoView para pagos completos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pago = Pago.objects.create(
                alquiler=alquiler,
                monto=monto,
                metodo_pago=serializer.validated_data['metodo_pago'],
                estado_pago='parcial',
                referencia_transaccion=serializer.validated_data.get('referencia_transaccion', ''),
                aprobado_por=request.user,
                fecha_vencimiento=timezone.now().date() + timedelta(days=15)
            )
            enviar_notificacion_pago(pago, request.user)
            return Response(PagoDetalleSerializer(pago).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Error al registrar el pago parcial: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class TotalPagadoAlquilerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, alquiler_id):
        """
        Obtiene el total pagado para un alquiler específico
        """
        alquiler = get_object_or_404(Alquiler, id=alquiler_id)
        
        # Calcular el total pagado sumando todos los pagos aprobados
        total_pagado = alquiler.pagos.filter(
            estado_pago__in=['pagado', 'parcial']
        ).aggregate(
            total=Sum('monto')
        )['total'] or Decimal('0.00')

        # Obtener el porcentaje pagado
        porcentaje_pagado = (total_pagado / alquiler.precio_total * 100) if alquiler.precio_total > 0 else 0

        return Response({
            'alquiler_id': alquiler.id,
            'total_pagado': total_pagado,
            'saldo_pendiente': alquiler.precio_total - total_pagado,
            'porcentaje_pagado': round(float(porcentaje_pagado), 2),
            'moneda': 'COP'  # Puedes hacer esto configurable
        })        