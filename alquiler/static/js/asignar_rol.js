
document.addEventListener('DOMContentLoaded', function() {
    const roleSelect = document.getElementById('rol');
    const roleDescription = document.getElementById('role-description-content');
    const rolePermissions = document.getElementById('role-permissions-content');
    
    // Datos de roles (precargados en el template)
    const rolesData = {
        {% for rol in roles %}
        '{{ rol.id }}': {
            description: `{{ rol.descripcion|default:"No hay descripción disponible" }}`,
            permissions: [
                {% for permiso in rol.permisos.all %}
                '{{ permiso.name }}',
                {% endfor %}
            ]
        },
        {% endfor %}
    };
    
    roleSelect.addEventListener('change', function() {
        const selectedRoleId = this.value;
        
        if (selectedRoleId && rolesData[selectedRoleId]) {
            const role = rolesData[selectedRoleId];
            
            // Actualizar descripción
            roleDescription.innerHTML = `<p>${role.description}</p>`;
            
            // Actualizar permisos
            if (role.permissions.length > 0) {
                let permissionsHTML = '<div class="permissions-list">';
                role.permissions.forEach(perm => {
                    permissionsHTML += `<span class="badge badge-secondary">${perm}</span>`;
                });
                permissionsHTML += '</div>';
                rolePermissions.innerHTML = permissionsHTML;
            } else {
                rolePermissions.innerHTML = '<p class="text-muted">Este rol no tiene permisos asignados</p>';
            }
        } else {
            roleDescription.innerHTML = '<p class="text-muted">Seleccione un rol para ver su descripción</p>';
            rolePermissions.innerHTML = '<p class="text-muted">Seleccione un rol para ver sus permisos</p>';
        }
    });
});
