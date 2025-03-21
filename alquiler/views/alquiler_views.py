from django.shortcuts import render, redirect
from alquiler.models import Alquiler
from alquiler.forms.alquiler_forms import AlquilerForm

def crear_alquiler(request):
    if request.method == 'POST':
        form = AlquilerForm(request.POST)
        if form.is_valid():
            alquiler = form.save(commit=False)
            alquiler.estado_alquiler = 'activo'
            alquiler.save()

            # Cambiar estado del equipo alquilado
            equipo = alquiler.equipo
            equipo.estado = 'alquilado'
            equipo.save()

            return redirect('listar_alquileres')
    else:
        form = AlquilerForm()
    return render(request, 'alquiler/alquiler/crear.html', {'form': form})
