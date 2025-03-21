from django.urls import path
from alquiler.views.equipo_views import (
    listar_equipos, crear_equipo, editar_equipo, detalle_equipo, equipos_disponibles, cambiar_estado_equipo, equipos_por_estado
)

urlpatterns = [
    path('equipos/', listar_equipos, name='listar_equipos'),
    path('equipos/nuevo/', crear_equipo, name='crear_equipo'),
    path('equipos/<int:id>/editar/', editar_equipo, name='editar_equipo'),
    path('equipos/<int:id>/', detalle_equipo, name='detalle_equipo'),
    path('equipos-disponibles/', equipos_disponibles, name='equipos_disponibles'),
    path('equipos/<int:id>/estado/<str:nuevo_estado>/', cambiar_estado_equipo, name='cambiar_estado_equipo'),
    path('equipos/estado/<str:estado>/', equipos_por_estado, name='equipos_por_estado'),

]
