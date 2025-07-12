from django.urls import path, include
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
    ejecutar_alertas_vencimiento, eliminar_equipo, pagos_pendientes_admin
)
from alquiler.views.cliente_views import (
listar_clientes, crear_cliente, editar_cliente, detalle_cliente,
cambiar_estado_verificacion, bloquear_cliente,clientes_morosos,validar_documentos_cliente,
registrar_pago_parcial

)

from alquiler.views.alquiler_views import (
listar_alquileres,crear_alquiler,finalizar_alquiler, renovar_alquiler,
generar_acta_entrega, aprobar_alquiler,calendario_alquileres,
detalle_alquiler, cancelar_alquiler,reservar_alquiler,generar_acta_devolucion, crear_contrato, firmar_contrato,
renovar_contrato,eliminar_alquiler, series_disponibles, editar_alquiler
)

from alquiler.views.pago_views import (
    RegistrarPagoView,
    PagosPendientesView, GenerarFacturaView, PasarelaPagoView, PagosAlquilerView, RegistrarPagoParcialView, 
    PagoDetalleView,ProcesarPagoPasarelaView, TotalPagadoAlquilerView, listar_pagos, editar_pago,verificar_estado_pago_alquiler, enviar_notificacion_pago,
    registrar_pago, detalle_pago,generar_factura_pdf, pagos_vencidos, pagos_proximos_vencer, cambiar_estado_pago, eliminar_pago, reportes_pagos, pagos_parciales, registrar_pago_contra_obligacion
)

from alquiler.views.usuario_views import(
    registro_usuario,salir_sesion,asignar_rol, inicio_sesion, pagina_principal, lista_usuarios,editar_usuario,eliminar_usuario,cambiar_estado_usuario,
    cambiar_contrasena, confirmar_eliminar_usuario, detalle_usuario, auditoria_usuario, activar_cuenta,crear_rol,lista_roles,editar_rol,eliminar_rol

)

from alquiler.views.base_views import(
    BusquedaGlobalView, sugerencias_busqueda
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('alquiler.api_urls')),
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
    path('pagos/pendientes/', pagos_pendientes_admin, name='pagos_pendientes_admin'),
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
    path('equipos/<int:equipo_id>/series-disponibles/', series_disponibles, name='series_disponibles'),
    path('alquileres/<int:id>/finalizar/', finalizar_alquiler, name='finalizar_alquiler'),
    path('alquileres/reservar/', reservar_alquiler, name='reservar_alquiler'),
    path('alquileres/<int:id>/cancelar/', cancelar_alquiler, name='cancelar_alquiler'),
    path('alquileres/<int:id>/aprobar/', aprobar_alquiler, name='aprobar_alquiler'),
    path('alquileres/<int:id>/renovar/', renovar_alquiler, name='renovar_alquiler'),
    path('alquileres/<int:id>/detalle/', detalle_alquiler, name='detalle_alquiler'),
    path('alquileres/calendario/', calendario_alquileres, name='calendario_alquileres'),
    path('alquileres/<int:id>/editar/', editar_alquiler, name='editar_alquiler'),
    path('alquileres/<int:id>/firmar-contrato/', firmar_contrato, name='firmar_contrato'),
    path('alquileres/<int:id>/renovar-contrato/', renovar_contrato, name='renovar_contrato'),
    path('alquileres/<int:id>/eliminar/', eliminar_alquiler, name='eliminar_alquiler'),
    #incompletas
    path('alquileres/<int:id>/acta-entrega/', generar_acta_entrega, name='generar_acta_entrega'),
    path('alquileres/<int:id>/acta-devolucion/', generar_acta_devolucion, name='generar_acta_devolucion'),
    path('alquileres/<int:id>/crear-contrato/', crear_contrato, name='crear_contrato'),
    #Pagos
    path('pagos/', listar_pagos, name='lista_pagos'),
    path('pagos/registrar/', registrar_pago, name='registrar_pago'),
    path('pagos/<int:pago_id>/', detalle_pago, name='detalle_pago'),
    path('pagos/<int:pago_id>/editar/', editar_pago, name='editar_pago'),  # Nueva URL
    path('pagos/<int:pago_id>/factura/', generar_factura_pdf, name='generar_factura_pdf'),
    path('pagos/vencidos/', pagos_vencidos, name='pagos_vencidos'),
    path('pagos/proximos/', pagos_proximos_vencer, name='pagos_proximos'),
    path('pagos/<int:pago_id>/cambiar-estado/<str:nuevo_estado>/', cambiar_estado_pago, name='cambiar_estado_pago'),
    path('pagos/<int:pago_id>/eliminar/', eliminar_pago, name='eliminar_pago'),
    path('pagos/reportes/', reportes_pagos, name='reportes_pagos'),
    path('pagos/parciales/', pagos_parciales, name='pagos_parciales'),
    path('pagos/<int:pago_id>/registrar/', registrar_pago_contra_obligacion, name='registrar_pago_contra_obligacion'),
    #Urls Usuario
    path('', inicio_sesion, name='inicio_sesion'),
    path('registro/', registro_usuario, name='registro'),
    path('salir/', salir_sesion, name='salir'),
    path('inicio/', pagina_principal, name='pagina_principal'),
    path('usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/editar/<int:usuario_id>/', editar_usuario, name='editar_usuario'),
    path('usuarios/cambiar-estado/<int:usuario_id>/', cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('usuarios/cambiar-contrasena/<int:usuario_id>/', cambiar_contrasena, name='cambiar_contrasena'),
    path('usuarios/eliminar/<int:usuario_id>/', confirmar_eliminar_usuario, name='confirmar_eliminar_usuario'),
    path('usuarios/eliminar-confirmado/<int:usuario_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('usuarios/detalle/<int:usuario_id>/', detalle_usuario, name='detalle_usuario'),
    path('usuarios/auditoria/<int:usuario_id>/', auditoria_usuario, name='auditoria_usuario'),
    path('activar/<uidb64>/<token>/', activar_cuenta, name='activar_cuenta'),
    #Roles
    path('roles/', lista_roles, name='lista_roles'),
    path('roles/crear/', crear_rol, name='crear_rol'),
    path('roles/editar/<int:rol_id>/', editar_rol, name='editar_rol'),
    path('roles/eliminar/<int:rol_id>/', eliminar_rol, name='eliminar_rol'),
    
    # Asignación de roles a usuarios
    path('usuarios/<int:usuario_id>/asignar-rol/', asignar_rol, name='asignar_rol'),

]


    



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manejo personalizado de errores
handler404 = 'alquiler.views.equipo_views.error_404_view'
