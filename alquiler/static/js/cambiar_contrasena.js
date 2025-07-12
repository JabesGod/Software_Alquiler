document.addEventListener('DOMContentLoaded', function () {
    const wrapper = document.querySelector('.password-wrapper[data-username]');
    const username = wrapper?.dataset.username || '';
    const email = wrapper?.dataset.email || '';
    const passwordInput = wrapper?.querySelector('input[type="password"], input[type="text"]');
    const requirements = document.querySelectorAll('.password-requirements li');

    const commonPasswords = ['password', '12345678', 'qwerty', 'admin', 'welcome'];

    if (passwordInput) {
        passwordInput.addEventListener('input', function () {
            const password = this.value;

            const validations = {
                length: password.length >= 8,
                personal: !isSimilarToPersonalInfo(password, username, email),
                common: !isCommonPassword(password),
                number: /\d/.test(password),
                special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
            };

            requirements.forEach(req => {
                const requirement = req.getAttribute('data-requirement');
                const icon = req.querySelector('i');

                if (validations[requirement]) {
                    icon.classList.remove('fa-times', 'text-danger');
                    icon.classList.add('fa-check', 'text-success');
                    req.style.opacity = '0.7';
                } else {
                    icon.classList.remove('fa-check', 'text-success');
                    icon.classList.add('fa-times', 'text-danger');
                    req.style.opacity = '1';
                }
            });
        });
    }

    function isSimilarToPersonalInfo(password, username, email) {
        const userInfo = [username, email.split('@')[0], 'usuario', 'user'];
        return userInfo.some(info =>
            info && password.toLowerCase().includes(info.toLowerCase())
        );
    }

    function isCommonPassword(password) {
        return commonPasswords.includes(password.toLowerCase());
    }

    // 👁️ Mostrar/Ocultar contraseña
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function () {
            const input = document.getElementById(this.dataset.targetId);
            if (input) {
                const isPassword = input.type === 'password';
                input.type = isPassword ? 'text' : 'password';
                this.textContent = isPassword ? '👁️‍🗨️' : '👁️';
            }
        });
    });
});
