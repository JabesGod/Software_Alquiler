from django.shortcuts import render, redirect, get_object_or_404
from ..models import Cliente, Alquiler, Pago
from ..forms import ClienteForm, PagoForm
from django.db.models import Count
from django.contrib import messages


# Listado general de clientes
def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})

# Crear nuevo cliente
def crear_cliente(request):
    form = ClienteForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('listar_clientes')
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
    clientes = Cliente.objects.filter(
        alquiler__pago__estado_pago='pendiente'
    ).distinct()

    return render(request, 'clientes_morosos.html', {'clientes': clientes})

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

    return render(request, 'clientes/registrar_pago_parcial.html', {
        'form': form, 'alquiler': alquiler
    })
