from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from alquiler.views.equipo_views import (
    listar_equipos, crear_equipo, editar_equipo, detalle_equipo,
    equipos_disponibles, cambiar_estado_equipo, equipos_por_estado,
    equipos_mas_alquilados, dashboard_admin,
    actualizar_estados_masivo, exportar_equipos_csv,
    historial_equipo, proxima_disponibilidad,
    ejecutar_alertas_vencimiento, eliminar_equipo
)
from alquiler.views.cliente_views import (
listar_clientes, crear_cliente, editar_cliente, detalle_cliente,
cambiar_estado_verificacion, bloquear_cliente,clientes_morosos,validar_documentos_cliente,
registrar_pago_parcial

)
from alquiler.views.alquiler_views import (
listar_alquileres,crear_alquiler,finalizar_alquiler, renovar_alquiler,
subir_documentos_alquiler, generar_acta_entrega, aprobar_alquiler,calendario_alquileres,
detalle_alquiler, cancelar_alquiler,reservar_alquiler,generar_acta_devolucion, crear_contrato, firmar_contrato,
renovar_contrato,eliminar_alquiler

)

from alquiler.views.pago_views import (
    RegistrarPagoView, RegistrarPagoParcialView,
    PagosPendientesView, GenerarFacturaView, PasarelaPagoView,
    TotalPagadoAlquilerView
)

from alquiler.views.usuario_views import(
    registro_usuario,salir_sesion,asignar_rol, inicio_sesion, pagina_principal
)

from alquiler.views.base_views import(
    BusquedaGlobalView, sugerencias_busqueda
)
urlpatterns = [
    path('admin/', admin.site.urls),
    #Buscador
    path('buscar/', BusquedaGlobalView.as_view(), name='busqueda_global'),
    path('buscar/sugerencias/', sugerencias_busqueda, name='sugerencias_busqueda'),

    # Urls de Equipos
    path('equipos/', listar_equipos, name='listar_equipos'),
    path('equipos/nuevo/', crear_equipo, name='crear_equipo'),
    path('equipos/<int:id>/', detalle_equipo, name='detalle_equipo'),
    path('equipos/<int:id>/editar/', editar_equipo, name='editar_equipo'),
    path('equipos/<int:pk>/eliminar/', eliminar_equipo, name='eliminar_equipo'),
    path('equipos-disponibles/', equipos_disponibles, name='equipos_disponibles'),
    path('equipos/<int:id>/estado/<str:nuevo_estado>/', cambiar_estado_equipo, name='cambiar_estado_equipo'),
    path('equipos/estado/<str:estado>/', equipos_por_estado, name='equipos_por_estado'),
    path('equipos/estadisticas/', equipos_mas_alquilados, name='equipos_mas_alquilados'),
    path('equipos/exportar-csv/', exportar_equipos_csv, name='exportar_equipos_csv'),
    path('equipos/<int:id>/historial/', historial_equipo, name='historial_equipo'),
    path('dashboard/', dashboard_admin, name='dashboard_admin'),
    path('equipos/actualizar-masivo/', actualizar_estados_masivo, name='actualizar_estados_masivo'),
    path('equipos/<int:id>/proxima-disponibilidad/', proxima_disponibilidad, name='proxima_disponibilidad'),
    path('alertas/vencimiento/manual/', ejecutar_alertas_vencimiento, name='enviar_alertas_vencimiento'),
    #Urls clientes
    path('clientes/', listar_clientes, name='listar_clientes'),
    path('clientes/crear/', crear_cliente, name='crear_cliente'),
    path('clientes/<int:id>/editar/', editar_cliente, name='editar_cliente'),
    path('clientes/<int:id>/', detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:id>/verificar/<str:nuevo_estado>/', cambiar_estado_verificacion, name='cambiar_estado_verificacion'),
    path('clientes/<int:id>/bloquear/',bloquear_cliente, name='bloquear_cliente'),
    path('clientes-morosos/', clientes_morosos, name='clientes_morosos'),
    path('clientes/<int:id>/validar-documentos/', validar_documentos_cliente, name='validar_documentos_cliente'),
    #Urls Alquileres
    path('alquiler/<int:id_alquiler>/pago-parcial/', registrar_pago_parcial, name='registrar_pago_parcial'),
    path('alquileres/', listar_alquileres, name='listar_alquileres'),
    path('alquileres/crear/', crear_alquiler, name='crear_alquiler'),
    path('alquileres/<int:id>/finalizar/', finalizar_alquiler, name='finalizar_alquiler'),
    path('alquileres/<int:id>/renovar/', renovar_alquiler, name='renovar_alquiler'),
    path('alquileres/<int:id>/subir-documentos/', subir_documentos_alquiler, name='subir_documentos_alquiler'),
    path('alquileres/<int:id>/acta-entrega/', generar_acta_entrega, name='generar_acta_entrega'),
    path('alquileres/<int:id>/aprobar/', aprobar_alquiler, name='aprobar_alquiler'),
    path('alquileres/calendario/', calendario_alquileres, name='calendario_alquileres'),
    path('alquileres/<int:id>/detalle/', detalle_alquiler, name='detalle_alquiler'),
    path('alquileres/<int:id>/cancelar/', cancelar_alquiler, name='cancelar_alquiler'),
    path('alquileres/reservar/', reservar_alquiler, name='reservar_alquiler'),
    path('alquileres/<int:id>/acta-devolucion/', generar_acta_devolucion, name='generar_acta_devolucion'),
    path('alquileres/<int:id>/crear-contrato/', crear_contrato, name='crear_contrato'),
    path('alquileres/<int:id>/firmar-contrato/', firmar_contrato, name='firmar_contrato'),
    path('alquileres/<int:id>/renovar-contrato/', renovar_contrato, name='renovar_contrato'),
    path('alquileres/<int:id>/eliminar/', eliminar_alquiler, name='eliminar_alquiler'),
    #Urls Pago
    path('registrar/', RegistrarPagoView.as_view(), name='registrar_pago'),
    path('registrar-parcial/', RegistrarPagoParcialView.as_view(), name='registrar_pago_parcial'),
    path('pendientes/<int:id_cliente>/', PagosPendientesView.as_view(), name='pagos_pendientes'),
    path('factura/<int:id_pago>/', GenerarFacturaView.as_view(), name='generar_factura'),
    path('pasarela/', PasarelaPagoView.as_view(), name='pasarela_pago'),
    path('total-pagado/<int:id_alquiler>/', TotalPagadoAlquilerView.as_view(), name='total_pagado_alquiler'),
    #Urls Usuario
    path('', inicio_sesion, name='inicio_sesion'),
    path('registro/', registro_usuario, name='registro'),
    path('salir/', salir_sesion, name='salir'),
    path('asignar-rol/<int:usuario_id>/', asignar_rol, name='asignar_rol'),
    path('inicio/', pagina_principal, name='pagina_principal'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manejo personalizado de errores
handler404 = 'alquiler.views.equipo_views.error_404_view'
