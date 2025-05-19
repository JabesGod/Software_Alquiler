document.addEventListener('DOMContentLoaded', function() {
  // 1. Manejo de pestañas
  const tabs = document.querySelectorAll('.auth-tab');
  const forms = document.querySelectorAll('.auth-form');
  
  // Configurar listeners para cambiar entre pestañas
  tabs.forEach(tab => {
      tab.addEventListener('click', function(e) {
          e.preventDefault(); // Prevenir comportamiento por defecto
          
          // Cambiar pestaña activa
          tabs.forEach(t => t.classList.remove('active'));
          this.classList.add('active');
          
          // Mostrar el formulario correspondiente
          const formType = this.dataset.tab;
          forms.forEach(form => {
              form.classList.remove('active');
              if (form.id === formType + '-form') {
                  form.classList.add('active');
              }
          });
      });
  });
  
  // 2. Funcionalidad para mostrar/ocultar contraseñas
  document.querySelectorAll('.toggle-password').forEach(toggle => {
      toggle.addEventListener('click', function() {
          const passwordField = this.previousElementSibling;
          if (passwordField.type === 'password') {
              passwordField.type = 'text';
              this.textContent = '🔒';
          } else {
              passwordField.type = 'password';
              this.textContent = '👁️';
          }
      });
  });
  
  // 3. Validación básica de formularios
  const registerForm = document.getElementById('registro-form');
  if (registerForm) {
      registerForm.addEventListener('submit', function(e) {
          const password1 = document.getElementById('id_password1').value;
          const password2 = document.getElementById('id_password2').value;
          
          if (password1 !== password2) {
              e.preventDefault(); // Detener el envío del formulario
              alert('Las contraseñas no coinciden');
          }
      });
  }
  
  // 4. Si hay errores en el formulario, asegúrate de que se muestre el formulario correcto
  if (document.querySelector('.error-message') && document.getElementById('registro-form')) {
      // Activar la pestaña de registro si hay errores en ese formulario
      tabs.forEach(tab => {
          tab.classList.remove('active');
          if (tab.dataset.tab === 'registro') {
              tab.classList.add('active');
          }
      });
      
      // Mostrar el formulario de registro
      forms.forEach(form => {
          form.classList.remove('active');
          if (form.id === 'registro-form') {
              form.classList.add('active');
          }
      });
  }
});