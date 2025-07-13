from django.shortcuts import render, redirect, get_object_or_404
from ..models import Cliente, Alquiler, Pago
from ..forms import ClienteForm, PagoForm
from django.db.models import Count
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required,permission_required


def es_admin(user):
    return user.is_authenticated and user.is_staff  # o user.is_superuser

@login_required
@permission_required('alquiler.view_cliente', raise_exception=True)
def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})


def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')
        else:
            print("Errores de formulario:", form.errors)  # <--- Agrega esto
    else:
        form = ClienteForm()

    return render(request, 'crear_cliente.html', {'form': form})


# Editar cliente existente
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    form = ClienteForm(request.POST or None, request.FILES or None, instance=cliente)
    if form.is_valid():
        form.save()
        return redirect('listar_clientes')
    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente})

# Detalle del cliente con historial completo
def detalle_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    historial_alquileres = Alquiler.objects.filter(cliente=cliente)
    pagos_pendientes = Pago.objects.filter(alquiler__cliente=cliente, estado_pago='pendiente')

    context = {
        'cliente': cliente,
        'historial_alquileres': historial_alquileres,
        'pagos_pendientes': pagos_pendientes
    }
    return render(request, 'detalle_cliente.html', context)

# Cambiar estado de verificación
def cambiar_estado_verificacion(request, id, nuevo_estado):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.estado_verificacion = nuevo_estado
    cliente.save()
    return redirect('detalle_cliente', id=id)

# Bloquear cliente
def bloquear_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.estado_verificacion = 'rechazado'
    cliente.save()
    return redirect('detalle_cliente', id=id)

def clientes_morosos(request):
    # Ejecutar la actualización primero
    actualizar_morosidad_clientes()
    
    # Obtener solo clientes marcados como morosos
    clientes = Cliente.objects.filter(moroso=True).order_by('-dias_mora')
    
    return render(request, 'clientes_morosos.html', {
        'clientes': clientes,
        'hoy': timezone.now().date()
    })

@login_required
def marcar_como_moroso(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        cliente.moroso = True
        cliente.fecha_marcado_moroso = timezone.now().date()
        cliente.save()
        
        messages.warning(request, f'{cliente.nombre} ha sido marcado como moroso')
        return redirect('detalle_cliente', cliente_id=cliente.id)
    
    return render(request, 'confirmar_moroso.html', {'cliente': cliente})

def actualizar_morosidad_clientes():
    # Obtener clientes con pagos pendientes por más de X días
    fecha_limite = timezone.now().date() - timedelta(days=15)  # 15 días de gracia
    
    clientes_morosos = Cliente.objects.filter(
        alquileres__pagos__estado_pago='pendiente',
        alquileres__fecha_vencimiento__lte=timezone.now()

    ).distinct()
    
    for cliente in clientes_morosos:
        # Calcular días de mora (usando el pago más atrasado)
        pago_mas_atrasado = cliente.pagos.filter(
            estado_pago='pendiente'
        ).order_by('fecha_vencimiento').first()
        
        if pago_mas_atrasado:
            dias_mora = (timezone.now().date() - pago_mas_atrasado.fecha_vencimiento).days
            deuda_total = sum(
                p.monto for p in cliente.pagos.filter(estado_pago='pendiente')
            )
            
            cliente.moroso = True
            cliente.dias_mora = dias_mora
            cliente.deuda_total = deuda_total
            cliente.fecha_marcado_moroso = timezone.now().date()
            cliente.save()

def validar_documentos_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    documentos_completos = cliente.documento_rut and cliente.documento_cedula

    if documentos_completos:
        cliente.estado_verificacion = 'verificado'
        cliente.save()
        messages.success(request, "Cliente validado correctamente.")
    else:
        messages.error(request, "Faltan documentos por subir.")

    return redirect('detalle_cliente', id=id)



def registrar_pago_parcial(request, id_alquiler):
    alquiler = get_object_or_404(Alquiler, id=id_alquiler)

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.alquiler = alquiler
            pago.estado_pago = 'parcial'
            pago.save()
            messages.success(request, "Pago parcial registrado.")
            return redirect('detalle_cliente', id=alquiler.cliente.id)
    else:
        form = PagoForm()

    return render(request, 'registrar_pago_parcial.html', {
        'form': form, 'alquiler': alquiler
    })

