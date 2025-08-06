document.addEventListener('DOMContentLoaded', function() {
  const tabs = document.querySelectorAll('.tab');
  const forms = document.querySelectorAll('.form');

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      if (!this.classList.contains('active')) {
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

      
      this.style.transform = 'translateY(-50%) scale(1.3)';
      setTimeout(() => {
        this.style.transform = 'translateY(-50%) scale(1)';
      }, 200);
    });
  });

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    const password1 = registerForm.querySelector('[name="password1"]');
    const password2 = registerForm.querySelector('[name="password2"]');

    function validatePasswords() {
      if (password1.value !== password2.value && password2.value.length > 0) {
        password2.style.borderColor = 'var(--error-color)'; 
        password2.style.boxShadow = '0 0 0 3px rgba(255, 71, 87, 0.2)';
        return false;
      } else {
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

  const messages = document.querySelector('.messages');
  if (messages) {
    setTimeout(() => {
      messages.style.opacity = '0';
      setTimeout(() => {
        messages.style.display = 'none';
      }, 300);
    }, 5000);
  }

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

  document.querySelectorAll('.input-group input').forEach(input => {
    if (!input.placeholder) {
      input.placeholder = ' ';
    }
  });

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
  if (!document.head.querySelector('style[data-spinner-style]')) {
      spinnerStyle.setAttribute('data-spinner-style', 'true'); 
      document.head.appendChild(spinnerStyle);
  }


  const computerFigure = document.querySelector('.computer-figure');

  if (computerFigure) { 
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    passwordInputs.forEach(input => {
      input.addEventListener('focus', function() {
        computerFigure.classList.add('password-focused');
      });

      input.addEventListener('blur', function() {
        computerFigure.classList.remove('password-focused');
      });
    });

    function randomMovement() {
      const time = Math.random() * 4000 + 3000; 

      setTimeout(() => {
        computerFigure.classList.add('peeking');

        setTimeout(() => {
          computerFigure.classList.remove('peeking');
          randomMovement();
        }, 300);
      }, time);
    }

    randomMovement();
  }


  const darkModeToggle = document.getElementById('darkModeToggle');
  const body = document.body; 

  function applySavedDarkModeSetting() {
      if (localStorage.getItem('darkMode') === 'enabled') {
          body.classList.add('dark-mode');
          if (darkModeToggle) {
              darkModeToggle.checked = true;
          }
      }
  }

  function toggleDarkMode() {
      if (this.checked) {
          body.classList.add('dark-mode');
          localStorage.setItem('darkMode', 'enabled');
      } else {
          body.classList.remove('dark-mode');
          localStorage.setItem('darkMode', 'disabled');
      }
  }

  applySavedDarkModeSetting();

  if (darkModeToggle) {
      darkModeToggle.addEventListener('change', toggleDarkMode);
  }
});
