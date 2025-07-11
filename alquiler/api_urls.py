from django.urls import path
from alquiler.views.pago_views import (
    RegistrarPagoView,
    RegistrarPagoParcialView,
    PagosAlquilerView,
    PagoDetalleView,
    PagosPendientesView,
    GenerarFacturaView,
    PasarelaPagoView,
    ProcesarPagoPasarelaView,
    TotalPagadoAlquilerView
)

urlpatterns = [
    path('pagos/registrar/', RegistrarPagoView.as_view(), name='registrar_pago'),
    path('pagos/parcial/', RegistrarPagoParcialView.as_view(), name='registrar_pago_parcial'),
    path('pagos/alquiler/<int:alquiler_id>/', PagosAlquilerView.as_view(), name='pagos_alquiler'),
    path('pagos/<int:pago_id>/', PagoDetalleView.as_view(), name='detalle_pago'),
    path('pagos/pendientes/', PagosPendientesView.as_view(), name='pagos_pendientes'),
    path('pagos/<int:pago_id>/factura/', GenerarFacturaView.as_view(), name='generar_factura'),
    path('pasarela/iniciar/', PasarelaPagoView.as_view(), name='pasarela_pago'),
    path('pasarela/procesar/', ProcesarPagoPasarelaView.as_view(), name='procesar_pago'),
    path('pagos/total/<int:alquiler_id>/', TotalPagadoAlquilerView.as_view(), name='total_pagado_alquiler'),
]
