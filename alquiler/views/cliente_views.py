from django.shortcuts import render, redirect
from alquiler.models import Cliente
from alquiler.forms.cliente_forms import ClienteForm  

def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'alquiler/cliente/lista.html', {'clientes': clientes})

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    return render(request, 'alquiler/cliente/crear.html', {'form': form})
