document.addEventListener('DOMContentLoaded', function() {
  // 1. Enhanced Tab Switching
  const tabs = document.querySelectorAll('.tab');
  const forms = document.querySelectorAll('.form');

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      if (!this.classList.contains('active')) {
        // Animate tab switch
        tabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        forms.forEach(form => {
          form.classList.remove('active');
          form.style.opacity = '0';
          form.style.transform = 'translateY(10px)';
        });

        const tabName = this.getAttribute('data-tab');
        const targetForm = document.getElementById(`${tabName}-form`);

        setTimeout(() => {
          targetForm.classList.add('active');
          targetForm.style.opacity = '1';
          targetForm.style.transform = 'translateY(0)';
        }, 10);
      }
    });
  });

  // 2. Password Toggle for all password fields
  document.querySelectorAll('.input-group input[type="password"]').forEach(input => {
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'toggle-pw';
    toggle.textContent = '👁️';
    toggle.setAttribute('aria-label', 'Mostrar contraseña');

    input.parentNode.appendChild(toggle);

    toggle.addEventListener('click', function() {
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      this.textContent = isPassword ? '👁️‍🗨️' : '👁️';

      // Animation
      this.style.transform = 'translateY(-50%) scale(1.3)';
      setTimeout(() => {
        this.style.transform = 'translateY(-50%) scale(1)';
      }, 200);
    });
  });

  // 3. Enhanced Password Validation
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    const password1 = registerForm.querySelector('[name="password1"]');
    const password2 = registerForm.querySelector('[name="password2"]');

    function validatePasswords() {
      if (password1.value !== password2.value && password2.value.length > 0) {
        password2.style.borderColor = 'var(--error-color)'; // Usar variable actualizada
        password2.style.boxShadow = '0 0 0 3px rgba(255, 71, 87, 0.2)';
        return false;
      } else {
        // Usar variables actualizadas para success y default border
        password2.style.borderColor = password2.value.length > 0 ? 'var(--success-color)' : 'var(--border-color-light)';
        password2.style.boxShadow = password2.value.length > 0 ? '0 0 0 3px rgba(0, 168, 89, 0.2)' : 'none';
        return true;
      }
    }

    password1.addEventListener('input', validatePasswords);
    password2.addEventListener('input', validatePasswords);

    registerForm.addEventListener('submit', function(e) {
      if (!validatePasswords()) {
        e.preventDefault();
        password2.style.animation = 'shake 0.5s';
        setTimeout(() => password2.style.animation = '', 500);
      }
    });
  }

  // 4. Auto-hide messages after 5 seconds
  const messages = document.querySelector('.messages');
  if (messages) {
    setTimeout(() => {
      messages.style.opacity = '0';
      setTimeout(() => {
        messages.style.display = 'none';
      }, 300);
    }, 5000);
  }

  // 5. Improved Button Loading State
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
      const btn = this.querySelector('.btn');
      if (btn) {
        btn.disabled = true;
        const originalText = btn.textContent;
        btn.innerHTML = `
          <span class="spinner"></span>
          <span class="btn-text">${originalText}</span>
        `;
      }
    });
  });

  // 6. Dynamic placeholders for floating labels
  document.querySelectorAll('.input-group input').forEach(input => {
    if (!input.placeholder) {
      input.placeholder = ' ';
    }
  });

  // Dynamic spinner styles (ensuring it's created once)
  const spinnerStyle = document.createElement('style');
  spinnerStyle.textContent = `
    .spinner {
      display: inline-block;
      width: 18px;
      height: 18px;
      border: 3px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: white;
      animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `;
  // Append only if not already appended
  if (!document.head.querySelector('style[data-spinner-style]')) {
      spinnerStyle.setAttribute('data-spinner-style', 'true'); // Add a custom attribute to identify it
      document.head.appendChild(spinnerStyle);
  }


  // Computer figure animations
  const computerFigure = document.querySelector('.computer-figure');

  if (computerFigure) { // Check if computerFigure exists before adding listeners
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(input => {
      input.addEventListener('focus', function() {
        computerFigure.classList.add('password-focused');
      });

      input.addEventListener('blur', function() {
        computerFigure.classList.remove('password-focused');
      });
    });

    // Animación de parpadeo aleatorio (los mouses se mueven un poco)
    function randomMovement() {
      const time = Math.random() * 4000 + 3000; // Entre 3 y 7 segundos

      setTimeout(() => {
        computerFigure.classList.add('peeking');

        setTimeout(() => {
          computerFigure.classList.remove('peeking');
          randomMovement();
        }, 300);
      }, time);
    }

    // Iniciar la animación
    randomMovement();
  }


  // ----------------------------------------------------
  //           LÓGICA PARA EL MODO OSCURO (NUEVO)
  // ----------------------------------------------------

  // 1. Obtener los elementos
  const darkModeToggle = document.getElementById('darkModeToggle');
  const body = document.body; // `body` is already defined globally

  // 2. Función para aplicar las configuraciones guardadas
  function applySavedDarkModeSetting() {
      // Aplicar modo oscuro si está activado en localStorage
      if (localStorage.getItem('darkMode') === 'enabled') {
          body.classList.add('dark-mode');
          // Marcar el interruptor si existe
          if (darkModeToggle) {
              darkModeToggle.checked = true;
          }
      }
  }

  // 3. Función para alternar el modo oscuro
  function toggleDarkMode() {
      if (this.checked) {
          body.classList.add('dark-mode');
          localStorage.setItem('darkMode', 'enabled');
      } else {
          body.classList.remove('dark-mode');
          localStorage.setItem('darkMode', 'disabled');
      }
  }

  // 4. Llama a la función al cargar la página
  applySavedDarkModeSetting();

  // 5. Configurar el evento del interruptor si existe
  if (darkModeToggle) {
      darkModeToggle.addEventListener('change', toggleDarkMode);
  }
});
