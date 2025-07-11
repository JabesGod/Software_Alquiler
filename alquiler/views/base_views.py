from django.views.generic import ListView
from django.db.models import Q
from ..models import Equipo, Cliente, Alquiler, Pago, Contrato, Usuario
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
        
        # Búsqueda en Equipos (ampliada)
        equipos = Equipo.objects.filter(
            Q(marca__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(numero_serie__icontains=query) |
            Q(especificaciones__icontains=query) |
            Q(ubicacion__icontains=query) |
            Q(descripcion_larga__icontains=query)
        ).distinct()
        for equipo in equipos:
            equipo.tipo_resultado = 'Equipo'
            resultados.append(equipo)
        
        # Búsqueda en Clientes (ampliada)
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(telefono__icontains=query) |
            Q(direccion__icontains=query) |
            Q(ciudad__icontains=query) |
            Q(barrio__icontains=query) |
            Q(numero_documento__icontains=query) |
            Q(nit__icontains=query) |
            Q(nombre_empresa__icontains=query)
        ).distinct()
        for cliente in clientes:
            cliente.tipo_resultado = 'Cliente'
            resultados.append(cliente)
        
        # Búsqueda en Alquileres (ampliada)
        alquileres = Alquiler.objects.filter(
            Q(numero_factura__icontains=query) |
            Q(estado_alquiler__icontains=query) |
            Q(aprobado_por__icontains=query) |
            Q(cliente__nombre__icontains=query) |
            Q(equipo__marca__icontains=query) |
            Q(equipo__modelo__icontains=query)
        ).distinct()
        for alquiler in alquileres:
            alquiler.tipo_resultado = 'Alquiler'
            resultados.append(alquiler)
        
        # Búsqueda en Pagos
        pagos = Pago.objects.filter(
            Q(referencia_transaccion__icontains=query) |
            Q(metodo_pago__icontains=query) |
            Q(alquiler__numero_factura__icontains=query) |
            Q(alquiler__cliente__nombre__icontains=query)
        ).distinct()
        for pago in pagos:
            pago.tipo_resultado = 'Pago'
            resultados.append(pago)
        
        # Búsqueda en Usuarios
        usuarios = Usuario.objects.filter(
            Q(nombre_usuario__icontains=query) |
            Q(cliente__nombre__icontains=query) |
            Q(rol__nombre_rol__icontains=query)
        ).distinct()
        for usuario in usuarios:
            usuario.tipo_resultado = 'Usuario'
            resultados.append(usuario)
        
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
    
    # Búsqueda en Equipos (ampliada)
    equipos = Equipo.objects.filter(
        Q(marca__icontains=query) | 
        Q(modelo__icontains=query) |
        Q(numero_serie__icontains=query) |
        Q(ubicacion__icontains=query)
    )[:5]
    for equipo in equipos:
        sugerencias.append({
            'text': f"{equipo.marca} {equipo.modelo} (Equipo - {equipo.ubicacion})",
            'type': 'equipo',
            'url': f"/equipos/{equipo.id}/"
        })
    
    # Búsqueda en Clientes (ampliada)
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=query) |
        Q(email__icontains=query) |
        Q(telefono__icontains=query) |
        Q(numero_documento__icontains=query)
    )[:5]
    for cliente in clientes:
        sugerencias.append({
            'text': f"{cliente.nombre} (Cliente - {cliente.numero_documento})",
            'type': 'cliente',
            'url': f"/clientes/{cliente.id}/"
        })
    
    # Búsqueda en Alquileres (ampliada)
    alquileres = Alquiler.objects.filter(
        Q(numero_factura__icontains=query) |
        Q(cliente__nombre__icontains=query)
    )[:3]
    for alquiler in alquileres:
        sugerencias.append({
            'text': f"Alquiler #{alquiler.numero_factura} ({alquiler.cliente.nombre})",
            'type': 'alquiler',
            'url': f"/alquileres/{alquiler.id}/"
        })
    
    # Búsqueda en Pagos
    pagos = Pago.objects.filter(
        Q(referencia_transaccion__icontains=query) |
        Q(alquiler__numero_factura__icontains=query)
    )[:3]
    for pago in pagos:
        sugerencias.append({
            'text': f"Pago {pago.referencia_transaccion} (Alquiler #{pago.alquiler.numero_factura})",
            'type': 'pago',
            'url': f"/pagos/{pago.id}/"
        })
    
    return JsonResponse(sugerencias, safe=False)