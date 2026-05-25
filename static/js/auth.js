/**
 * Authentication Logic
 * Handles registration, login, form validation, and UI states.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    // Redirect if already logged in, but only if we are on login/register pages
    const path = window.location.pathname;
    const isAuthPage = path.includes('login') || path.includes('register') || path === '/' || path === '/index.html';
    if (isAuthenticated() && isAuthPage) {
        window.location.href = '/dashboard.html';
        return;
    }

    // --- Shared Elements ---
    const togglePassword = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    const alertContainer = document.getElementById('alert-container');
    
    // --- Toggle Password Visibility ---
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');
        });
    }

    // --- Helpers ---
    function showError(inputId, message) {
        const input = document.getElementById(inputId);
        const errorDiv = document.getElementById(`${inputId}-error`);
        if (input) input.classList.add('error');
        if (errorDiv) errorDiv.textContent = message;
    }

    function clearErrors() {
        document.querySelectorAll('.form-input').forEach(input => input.classList.remove('error'));
        document.querySelectorAll('.form-error').forEach(div => div.textContent = '');
        if (alertContainer) alertContainer.innerHTML = '';
    }

    function showAlert(message, type = 'error') {
        if (!alertContainer) return;
        alertContainer.innerHTML = `
            <div class="alert alert-${type}">
                <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
    }

    function setLoading(isLoading) {
        const btnText = document.getElementById('btn-text');
        const btnSpinner = document.getElementById('btn-spinner');
        const submitBtn = document.getElementById('submit-btn');
        
        if (!submitBtn) return;
        
        if (isLoading) {
            submitBtn.disabled = true;
            if (btnText) btnText.style.display = 'none';
            if (btnSpinner) btnSpinner.style.display = 'block';
        } else {
            submitBtn.disabled = false;
            if (btnText) btnText.style.display = 'block';
            if (btnSpinner) btnSpinner.style.display = 'none';
        }
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function validatePasswordStrength(password) {
        if (password.length < 8) return { valid: false, msg: 'Password must be at least 8 characters long' };
        if (!/[A-Z]/.test(password)) return { valid: false, msg: 'Password must contain at least one uppercase letter' };
        if (!/[a-z]/.test(password)) return { valid: false, msg: 'Password must contain at least one lowercase letter' };
        if (!/\d/.test(password)) return { valid: false, msg: 'Password must contain at least one digit' };
        return { valid: true };
    }

    // --- Login Form Logic ---
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors();
            
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            let isValid = true;
            
            if (!email) {
                showError('email', 'Email is required');
                isValid = false;
            } else if (!validateEmail(email)) {
                showError('email', 'Please enter a valid email address');
                isValid = false;
            }
            
            if (!password) {
                showError('password', 'Password is required');
                isValid = false;
            }
            
            if (!isValid) return;
            
            setLoading(true);
            
            const response = await apiPost('/auth/login', { email, password });
            
            setLoading(false);
            
            if (response && response.success) {
                setToken(response.data.access_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
                // Redirect to dashboard
                window.location.href = '/dashboard.html';
            } else if (response) {
                showAlert(response.error || 'Login failed', 'error');
            }
        });
    }

    // --- Registration Form Logic ---
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        
        // Live password strength indicator
        if (passwordInput) {
            passwordInput.addEventListener('input', (e) => {
                const val = e.target.value;
                const container = document.getElementById('password-strength-container');
                const bar = document.getElementById('password-strength-bar');
                
                if (val.length === 0) {
                    container.style.display = 'none';
                    return;
                }
                
                container.style.display = 'block';
                
                let score = 0;
                if (val.length >= 8) score++;
                if (/[A-Z]/.test(val)) score++;
                if (/[a-z]/.test(val)) score++;
                if (/\d/.test(val)) score++;
                if (/[^A-Za-z0-9]/.test(val)) score++; // Special char bonus
                
                let percent = (score / 5) * 100;
                let color = 'var(--error-red)';
                
                if (score >= 4) color = 'var(--success-green)';
                else if (score >= 2) color = 'var(--warning-orange)';
                
                bar.style.width = `${percent}%`;
                bar.style.backgroundColor = color;
            });
        }
        
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors();
            
            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const password = passwordInput.value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            let isValid = true;
            
            if (!name) {
                showError('name', 'Full name is required');
                isValid = false;
            }
            
            if (!email) {
                showError('email', 'Email is required');
                isValid = false;
            } else if (!validateEmail(email)) {
                showError('email', 'Please enter a valid email address');
                isValid = false;
            }
            
            const pwdCheck = validatePasswordStrength(password);
            if (!pwdCheck.valid) {
                showError('password', pwdCheck.msg);
                isValid = false;
            }
            
            if (password !== confirmPassword) {
                showError('confirm-password', 'Passwords do not match');
                isValid = false;
            }
            
            if (!isValid) return;
            
            setLoading(true);
            
            const response = await apiPost('/auth/register', { name, email, password });
            
            setLoading(false);
            
            if (response && response.success) {
                setToken(response.data.access_token);
                localStorage.setItem('user', JSON.stringify(response.data.user));
                showAlert('Registration successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard.html';
                }, 1000);
            } else if (response) {
                showAlert(response.error || 'Registration failed', 'error');
            }
        });
    }
});
