from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from ..forms.usuario_forms import RegistroForm
from ..models import Rol, Usuario
from django.contrib.auth import login



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