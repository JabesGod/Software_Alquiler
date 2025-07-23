from django.views.generic import ListView
from django.db.models import Q
from ..models import Equipo, Cliente, Alquiler, Pago, Contrato, Usuario
from django.http import JsonResponse
from django.conf.urls.static import static
from django.urls import reverse
from django.core.exceptions import FieldError
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator



class BusquedaGlobalView(ListView):
    template_name = 'resultados_busqueda.html'
    context_object_name = 'resultados'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip().lower()
        if not query:
            return []
        
        resultados = []
        
        # Configuración de modelos para búsqueda
        modelos_busqueda = [
            {
                'model': Equipo,
                'fields': [
                    ('marca', 3.0),
                    ('sku', 3.0),
                    ('modelo', 3.0),
                    ('numero_serie', 2.5),
                    ('ubicacion', 2.0),
                    ('descripcion_larga', 1.5),
                    ('especificaciones', 1.5)
                ],
                'tipo': 'Equipo',
                'imagen_field': 'fotos',  # Relación con FotoEquipo
                'get_imagen': lambda obj: obj.obtener_foto_principal()
            },
            {
                'model': Cliente,
                'fields': [
                    ('nombre', 3.0),
                    ('numero_documento', 2.5),
                    ('nit', 2.5),
                    ('nombre_empresa', 2.0),
                    ('email', 1.5),
                    ('telefono', 1.5),
                    ('direccion', 1.0),
                    ('ciudad', 1.0),
                    ('barrio', 1.0)
                ],
                'tipo': 'Cliente',
                'imagen_field': 'foto',
                'get_imagen': lambda obj: obj.foto.url if obj.foto else static('img/user-default.png')
            },
            {
                'model': Alquiler,
                'fields': [
                    ('numero_factura', 3.0),
                    ('estado_alquiler', 2.0),
                    ('aprobado_por', 1.5),
                    ('cliente__nombre', 2.0),
                    ('detalles__equipo__marca', 1.5),  # Relación a través de DetalleAlquiler
                    ('detalles__equipo__modelo', 1.5)   # Relación a través de DetalleAlquiler
                ],
                'tipo': 'Alquiler',
                'imagen_field': None,
                'get_imagen': lambda obj: None
            },
            {
                'model': Pago,
                'fields': [
                    ('referencia_transaccion', 3.0),
                    ('metodo_pago', 2.0),
                    ('alquiler__numero_factura', 2.0),
                    ('alquiler__cliente__nombre', 1.5)
                ],
                'tipo': 'Pago',
                'imagen_field': None,
                'get_imagen': lambda obj: None
            },
            {
                'model': Usuario,
                'fields': [
                    ('nombre_usuario', 3.0),
                    ('cliente__nombre', 2.0),
                    ('rol__nombre_rol', 1.5)
                ],
                'tipo': 'Usuario',
                'imagen_field': None,
                'get_imagen': lambda obj: None
            }
        ]

        for config in modelos_busqueda:
            q_objects = Q()
            for field, weight in config['fields']:
                try:
                    q_objects |= Q(**{f"{field}__icontains": query})
                except FieldError:
                    continue  # Si el campo no existe, lo saltamos
            
            # Usamos distinct() para evitar duplicados
            resultados_modelo = config['model'].objects.filter(q_objects).distinct()
            
            for resultado in resultados_modelo:
                # Calcular puntaje de relevancia
                resultado.puntaje_relevancia = 0
                for field, weight in config['fields']:
                    try:
                        # Manejo de campos relacionados
                        parts = field.split('__')
                        attr = resultado
                        for part in parts:
                            if part:  # Ignorar partes vacías
                                attr = getattr(attr, part, None)
                                if attr is None:
                                    break
                        
                        if attr and query in str(attr).lower():
                            resultado.puntaje_relevancia += weight
                    except (AttributeError, FieldError):
                        continue
                
                resultado.tipo_resultado = config['tipo']
                
                # Añadir URL de imagen
                resultado.imagen_url = config['get_imagen'](resultado)
                
                resultados.append(resultado)
        
        # Ordenar por puntaje de relevancia descendente
        return sorted(resultados, key=lambda x: x.puntaje_relevancia, reverse=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query
        
        # Estadísticas de búsqueda
        tipos_resultados = set(r.tipo_resultado for r in context['resultados'])
        context['tipos_resultados'] = tipos_resultados
        
        # Sugerencia de búsqueda relacionada
        if len(context['resultados']) > 0:
            context['sugerencia_relacionada'] = self._generar_sugerencia_relacionada(query)
        
        return context
    
    def _generar_sugerencia_relacionada(self, query):
        sugerencias = {
            'equipo': f"Ver todos los equipos relacionados con '{query}'",
            'cliente': f"Ver clientes similares a '{query}'",
            'alquiler': f"Buscar alquileres para '{query}'"
        }
        return sugerencias.get(query.lower(), f"Resultados para '{query}'")
    

@login_required
def sugerencias_busqueda(request):
    query = request.GET.get('q', '').strip().lower()
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    sugerencias = []
    
    # Configuración de modelos para sugerencias
    modelos_sugerencias = [
        {
            'model': Equipo,
            'fields': ['marca', 'modelo', 'numero_serie', 'ubicacion'],
            'display': lambda obj: f"{obj.marca} {obj.modelo}",
            'subtext': lambda obj: f"Equipo - {obj.ubicacion}",
            'type': 'equipo',
            'url': lambda obj: reverse('detalle_equipo', args=[obj.id]),
            'imagen': lambda obj: obj.obtener_foto_principal()
        },
        {
            'model': Cliente,
            'fields': ['nombre', 'email', 'telefono', 'numero_documento'],
            'display': lambda obj: obj.nombre,
            'subtext': lambda obj: f"Cliente - {obj.numero_documento}",
            'type': 'cliente',
            'url': lambda obj: reverse('detalle_cliente', args=[obj.id]),
            'imagen': lambda obj: obj.foto.url if obj.foto else static('img/user-default.png')
        },
        {
            'model': Alquiler,
            'fields': ['numero_factura', 'cliente__nombre'],
            'display': lambda obj: f"Alquiler #{obj.numero_factura}",
            'subtext': lambda obj: f"Cliente: {obj.cliente.nombre}",
            'type': 'alquiler',
            'url': lambda obj: reverse('detalle_alquiler', args=[obj.id]),
            'imagen': None
        },
        {
            'model': Pago,
            'fields': ['referencia_transaccion', 'alquiler__numero_factura'],
            'display': lambda obj: f"Pago {obj.referencia_transaccion}",
            'subtext': lambda obj: f"Alquiler #{obj.alquiler.numero_factura}",
            'type': 'pago',
            'url': lambda obj: reverse('detalle_pago', args=[obj.id]),
            'imagen': None
        }
    ]
    
    for config in modelos_sugerencias:
        q_objects = Q()
        for field in config['fields']:
            try:
                q_objects |= Q(**{f"{field}__icontains": query})
            except FieldError:
                continue
        
        objetos = config['model'].objects.filter(q_objects).distinct()[:5]
        
        for obj in objetos:
            sugerencia = {
                'text': config['display'](obj),
                'subtext': config['subtext'](obj),
                'type': config['type'],
                'url': config['url'](obj),
                'highlight': query
            }
            
            if config['imagen']:
                imagen = config['imagen'](obj)
                if imagen:
                    sugerencia['imagen'] = request.build_absolute_uri(imagen)
            
            sugerencias.append(sugerencia)
    
    # Ordenar sugerencias por relevancia (texto más corto primero como aproximación)
    sugerencias.sort(key=lambda x: len(x['text']))
    
    # Añadir sugerencias genéricas si hay pocos resultados
    if len(sugerencias) < 5:
        terminos_comunes = {
            'equipo': ['marca', 'modelo', 'serie', 'ubicacion'],
            'cliente': ['nombre', 'documento', 'teléfono', 'email'],
            'alquiler': ['factura', 'estado', 'fecha', 'cliente']
        }
        
        for tipo, campos in terminos_comunes.items():
            for campo in campos:
                if query in campo:
                    sugerencias.append({
                        'text': f"Buscar {tipo} por {campo}",
                        'subtext': f"Sugerencia de búsqueda",
                        'type': 'sugerencia',
                        'url': reverse('busqueda') + f"?q={tipo}:{campo}",
                        'imagen': request.build_absolute_uri(static('img/search-suggestion.png'))
                    })
                    break  # Solo una sugerencia por tipo
    
    return JsonResponse(sugerencias[:10], safe=False)  # Limitar a 10 sugerencias