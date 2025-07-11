from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from ..forms.usuario_forms import RegistroForm,UsuarioEditForm,CambiarContrasenaForm
from ..models import Rol, Usuario, UserAuditLog
from django.contrib.auth import login
from django.db.models import Count
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.views.decorators.http import require_GET
import json
from django.db.models import Max
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = Usuario(
                nombre_usuario=form.cleaned_data['nombre_usuario']
            )
            usuario.set_password(form.cleaned_data['password1'])
            usuario.save()
            
            messages.success(request, '¡Registro exitoso! Por favor inicia sesión.')
            return redirect('inicio_sesion')  # Redirige a login en lugar de autenticar
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistroForm()
    
    return render(request, 'inicio_sesion.html', {
        'form_type': 'registro',
        'form': form
    })

def inicio_sesion(request):
    if request.user.is_authenticated:
        return redirect('pagina_principal')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.nombre_usuario}')
            return redirect('pagina_principal')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'inicio_sesion.html', {
        'form_type': 'inicio',
        'authenticated': False
    })

@login_required
def pagina_principal(request):
    return render(request, 'inicio.html', {
        'user': request.user
    })

@login_required
def salir_sesion(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('inicio_sesion')


@login_required
def vista_inicio(request):
    return render(request, 'inicio.html')

@staff_member_required
def asignar_rol(request, usuario_id):
    usuario = Usuario.objects.get(id=usuario_id)
    roles = Rol.objects.all()

    if request.method == 'POST':
        rol_id = request.POST.get('rol')
        rol = Rol.objects.get(id=rol_id)
        usuario.rol = rol
        usuario.save()
        messages.success(request, 'Rol asignado correctamente')
        return redirect('lista_usuarios')

    return render(request, 'asignar_rol.html', {
        'usuario': usuario,
        'roles': roles
    })


@staff_member_required
def lista_usuarios(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    rol_id = request.GET.get('rol', '')
    
    usuarios = Usuario.objects.all().order_by('nombre_usuario')
    
    if query:
        usuarios = usuarios.filter(nombre_usuario__icontains=query)
    
    if estado:
        usuarios = usuarios.filter(is_active=(estado == 'activo'))
    
    if rol_id:
        usuarios = usuarios.filter(rol_id=rol_id)
    
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    roles = Rol.objects.all()
    
    return render(request, 'lista_usuarios.html', {
        'page_obj': page_obj,
        'roles': roles,
        'query': query,
        'estado_seleccionado': estado,
        'rol_seleccionado': int(rol_id) if rol_id else ''
    })

@staff_member_required
def detalle_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'detalle_usuario.html', {'usuario': usuario})

@staff_member_required
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado correctamente')
            
            # Si el usuario editado es el mismo que está logueado
            if usuario.id == request.user.id:
                update_session_auth_hash(request, usuario)
                messages.info(request, 'Tus datos de sesión han sido actualizados')
            
            return redirect('detalle_usuario', usuario_id=usuario.id)
    else:
        form = UsuarioEditForm(instance=usuario)
    
    return render(request, 'editar_usuario.html', {
        'form': form,
        'usuario': usuario
    })

@staff_member_required
def cambiar_contrasena(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        form = CambiarContrasenaForm(request.POST)
        if form.is_valid():
            usuario.password = make_password(form.cleaned_data['nueva_contrasena'])
            usuario.save()
            
            # Si el usuario editado es el mismo que está logueado
            if usuario.id == request.user.id:
                update_session_auth_hash(request, usuario)
                messages.info(request, 'Tu contraseña ha sido cambiada y tu sesión ha sido actualizada')
            else:
                messages.success(request, 'Contraseña cambiada correctamente')
            
            return redirect('detalle_usuario', usuario_id=usuario.id)
    else:
        form = CambiarContrasenaForm()
    
    return render(request, 'cambiar_contrasena.html', {
        'form': form,
        'usuario': usuario
    })

@staff_member_required
def cambiar_estado_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # No permitir desactivarse a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes desactivar tu propia cuenta')
        return redirect('lista_usuarios')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    action = "activado" if usuario.is_active else "desactivado"
    messages.success(request, f'Usuario {usuario.nombre_usuario} {action} correctamente')
    return redirect('lista_usuarios')

@staff_member_required
def confirmar_eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # No permitir eliminarse a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta')
        return redirect('lista_usuarios')
    
    return render(request, 'confirmar_eliminar.html', {'usuario': usuario})

@staff_member_required
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propia cuenta')
        return redirect('lista_usuarios')
    
    nombre_usuario = usuario.nombre_usuario
    usuario.delete()
    
    logger.info(f"Usuario {nombre_usuario} eliminado por {request.user.nombre_usuario}")
    messages.success(request, f'Usuario {nombre_usuario} eliminado correctamente')
    return redirect('lista_usuarios')

@staff_member_required
@require_GET
def auditoria_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    # 1. Filtrar logs del usuario con búsqueda si existe
    query = request.GET.get('q', '')
    logs = UserAuditLog.objects.filter(user=usuario)
    
    if query:
        logs = logs.filter(
            Q(action__icontains=query) | 
            Q(details__icontains=query) |
            Q(ip_address__icontains=query)
        )
    
    logs = logs.order_by('-timestamp')[:100]  # Limitar a 100 registros
    
    # 2. Estadísticas para el gráfico (últimos 6 meses)
    six_months_ago = datetime.now() - timedelta(days=180)
    
    # Consulta compatible con múltiples bases de datos
    stats = UserAuditLog.objects.filter(
        user=usuario,
        timestamp__gte=six_months_ago
    ).annotate(
        month=TruncMonth('timestamp')
    ).values('month', 'status').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Preparar datos para el gráfico
    months = []
    success_data = []
    failed_data = []
    
    current_month = six_months_ago.replace(day=1)
    while current_month <= datetime.now():
        month_str = current_month.strftime('%b %Y')
        months.append(month_str)
        
        # Buscar datos para este mes
        month_stats = [s for s in stats if s['month'].month == current_month.month and s['month'].year == current_month.year]
        
        success = next((s['count'] for s in month_stats if s['status'] == 'success'), 0)
        failed = next((s['count'] for s in month_stats if s['status'] == 'failed'), 0)
        
        success_data.append(success)
        failed_data.append(failed)
        
        # Avanzar al siguiente mes
        if current_month.month == 12:
            current_month = current_month.replace(year=current_month.year+1, month=1)
        else:
            current_month = current_month.replace(month=current_month.month+1)
    
    # 3. Dispositivos conocidos
    devices = UserAuditLog.objects.filter(
        user=usuario,
        user_agent__isnull=False
    ).values('user_agent', 'ip_address').annotate(
        last_used=Max('timestamp'),
        count=Count('id')
    ).order_by('-last_used')[:5]
    
    return render(request, 'auditoria_usuario.html', {
        'usuario': usuario,
        'logs': logs,
        'devices': devices,
        'stats_data': {
            'months': months,
            'success': success_data,
            'failed': failed_data
        },
        'query': query  # Para mantener el valor de búsqueda
    })