from django.urls import path
from alquiler.views.equipo_views import (
    listar_equipos, crear_equipo, editar_equipo, detalle_equipo,
    equipos_disponibles, cambiar_estado_equipo, equipos_por_estado,
    equipos_mas_alquilados, buscar_equipos, dashboard_admin,
    calendario_alquileres, actualizar_estados_masivo, exportar_equipos_csv
)

urlpatterns = [
    
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
    path('alquileres/calendario/', calendario_alquileres, name='calendario_alquileres'),
    path('equipos/actualizar-masivo/', actualizar_estados_masivo, name='actualizar_estados_masivo'),
    path('equipos/exportar-csv/', exportar_equipos_csv, name='exportar_equipos_csv'),
]


handler404 = 'alquiler.views.equipo_views.error_404_view'
