from django.views.generic import ListView
from django.db.models import Q
from ..models import Equipo, Cliente, Alquiler
from django.http import JsonResponse

class BusquedaGlobalView(ListView):
    template_name = 'resultados_busqueda.html'
    context_object_name = 'resultados'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return []
        
        resultados = []
        
        # Buscar en Equipos (usando marca y modelo en lugar de nombre)
        equipos = Equipo.objects.filter(
            Q(marca__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(numero_serie__icontains=query) |
            Q(especificaciones__icontains=query)
        ).distinct()
        for equipo in equipos:
            equipo.tipo_resultado = 'Equipo'
            resultados.append(equipo)
        
        # Buscar en Clientes
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(telefono__icontains=query)
        ).distinct()
        for cliente in clientes:
            cliente.tipo_resultado = 'Cliente'
            resultados.append(cliente)
        
        # Buscar en Alquileres
        alquileres = Alquiler.objects.filter(
            Q(id__icontains=query) |
            Q(estado_alquiler__icontains=query)
        ).distinct()
        for alquiler in alquileres:
            alquiler.tipo_resultado = 'Alquiler'
            resultados.append(alquiler)
        
        return sorted(resultados, key=lambda x: x.tipo_resultado)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


def sugerencias_busqueda(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 3:
        return JsonResponse([], safe=False)
    
    sugerencias = []
    
    # Buscar en Equipos
    equipos = Equipo.objects.filter(
        Q(marca__icontains=query) | 
        Q(modelo__icontains=query) |
        Q(numero_serie__icontains=query)
    )[:5]
    for equipo in equipos:
        sugerencias.append({
            'text': f"{equipo.marca} {equipo.modelo} (Equipo - {equipo.numero_serie})",
            'type': 'equipo'
        })
    
    # Buscar en Clientes
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=query) |
        Q(email__icontains=query)
    )[:5]
    for cliente in clientes:
        sugerencias.append({
            'text': f"{cliente.nombre} (Cliente - {cliente.email})",
            'type': 'cliente'
        })
    
    # Buscar en Alquileres
    alquileres = Alquiler.objects.filter(
        Q(id__icontains=query)
    )[:3]
    for alquiler in alquileres:
        sugerencias.append({
            'text': f"Alquiler #{alquiler.id} ({alquiler.estado_alquiler})",
            'type': 'alquiler'
        })
    
    return JsonResponse(sugerencias, safe=False)