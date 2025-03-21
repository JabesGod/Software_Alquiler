from django.shortcuts import render, redirect, get_object_or_404
from alquiler.models import Equipo, Alquiler
from alquiler.forms.equipo_forms import EquipoForm
from django.db.models import Count

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
    equipos = Equipo.objects.annotate(total_alquileres=Count('alquiler')).order_by('-total_alquileres')[:10]
    return render(request, 'alquiler/equipo/top_alquilados.html', {'equipos': equipos})