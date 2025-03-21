from django.urls import path
from alquiler.views.equipo_views import (
    listar_equipos, crear_equipo, editar_equipo, detalle_equipo,
    equipos_disponibles, cambiar_estado_equipo, equipos_por_estado,
    equipos_mas_alquilados, buscar_equipos, dashboard_admin,
    actualizar_estados_masivo, exportar_equipos_csv,
    historial_equipo, proxima_disponibilidad, equipos_similares, dashboard_equipo,
    ejecutar_alertas_vencimiento
)
from alquiler.views.cliente_views import (
   listar_clientes, crear_cliente, editar_cliente, detalle_cliente,
   cambiar_estado_verificacion, bloquear_cliente,clientes_morosos,validar_documentos_cliente,
   registrar_pago_parcial

)
from alquiler.views.alquiler_views import (
   listar_alquileres,crear_alquiler,finalizar_alquiler, renovar_alquiler,
   subir_documentos_alquiler, generar_acta_entrega, aprobar_alquiler,calendario_alquileres,
   detalle_alquiler

)
urlpatterns = [
    # Urls de Equipos
    path('equipos/', listar_equipos, name='listar_equipos'),
    path('equipos/nuevo/', crear_equipo, name='crear_equipo'),
    path('equipos/<int:id>/editar/', editar_equipo, name='editar_equipo'),
    path('equipos/<int:id>/', detalle_equipo, name='detalle_equipo'),
    path('equipos-disponibles/', equipos_disponibles, name='equipos_disponibles'),
    path('equipos/<int:id>/estado/<str:nuevo_estado>/', cambiar_estado_equipo, name='cambiar_estado_equipo'),
    path('equipos/estado/<str:estado>/', equipos_por_estado, name='equipos_por_estado'),
    path('equipos/estadisticas/', equipos_mas_alquilados, name='equipos_mas_alquilados'),
    path('equipos/buscar/', buscar_equipos, name='buscar_equipos'),
    path('dashboard/', dashboard_admin, name='dashboard_admin'),
    path('equipos/actualizar-masivo/', actualizar_estados_masivo, name='actualizar_estados_masivo'),
    path('equipos/exportar-csv/', exportar_equipos_csv, name='exportar_equipos_csv'),
    path('equipos/<int:id>/historial/', historial_equipo, name='historial_equipo'),
    path('equipos/<int:id>/proxima-disponibilidad/', proxima_disponibilidad, name='proxima_disponibilidad'),
    path('equipos/<int:id>/similares/', equipos_similares, name='equipos_similares'),
    path('equipos/<int:id>/dashboard/', dashboard_equipo, name='dashboard_equipo'),
    path('ejecutar-alertas/', ejecutar_alertas_vencimiento, name='ejecutar_alertas_vencimiento'),
    #Urls clientes
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/crear/', crear_cliente, name='crear_cliente'),
    path('clientes/<int:id>/editar/', editar_cliente, name='editar_cliente'),
    path('clientes/<int:id>/', detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:id>/verificar/<str:nuevo_estado>/', cambiar_estado_verificacion, name='cambiar_estado_verificacion'),
    path('clientes/<int:id>/bloquear/',bloquear_cliente, name='bloquear_cliente'),
    path('clientes-morosos/', clientes_morosos, name='clientes_morosos'),
    path('clientes/<int:id>/validar-documentos/', validar_documentos_cliente, name='validar_documentos_cliente'),
    path('alquiler/<int:id_alquiler>/pago-parcial/', registrar_pago_parcial, name='registrar_pago_parcial'),
    #Urls Alquileres
    path('alquileres/', listar_alquileres, name='listar_alquileres'),
    path('alquileres/crear/', crear_alquiler, name='crear_alquiler'),
    path('alquileres/<int:id>/finalizar/', finalizar_alquiler, name='finalizar_alquiler'),
    path('alquileres/<int:id>/renovar/', renovar_alquiler, name='renovar_alquiler'),
    path('alquileres/<int:id>/subir-documentos/', subir_documentos_alquiler, name='subir_documentos_alquiler'),
    path('alquileres/<int:id>/acta-entrega/', generar_acta_entrega, name='generar_acta_entrega'),
    path('alquileres/<int:id>/aprobar/', aprobar_alquiler, name='aprobar_alquiler'),
    path('alquileres/calendario/', calendario_alquileres, name='calendario_alquileres'),
    path('alquileres/<int:id>/detalle/', detalle_alquiler, name='detalle_alquiler'),

]

# Manejo personalizado de errores
handler404 = 'alquiler.views.equipo_views.error_404_view'
