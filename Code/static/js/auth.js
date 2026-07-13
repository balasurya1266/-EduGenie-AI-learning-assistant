document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const pwInput = document.getElementById('password');

  pwInput?.addEventListener('input', () => {
    const val = pwInput.value;
    const fill = document.getElementById('strengthFill');
    const text = document.getElementById('strengthText');
    if (!fill || !text) return;
    let score = 0;
    if (val.length >= 6) score++;
    if (val.length >= 10) score++;
    if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
    if (/\d/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;
    const levels = [
      { w: '0%', c: '#EF4444', t: 'Too weak' },
      { w: '25%', c: '#F97316', t: 'Weak' },
      { w: '50%', c: '#EAB308', t: 'Fair' },
      { w: '75%', c: '#14B8A6', t: 'Good' },
      { w: '100%', c: '#10B981', t: 'Strong' },
    ];
    const lvl = levels[Math.min(score, 4)];
    fill.style.width = val ? lvl.w : '0%';
    fill.style.background = lvl.c;
    text.textContent = val ? lvl.t : 'Password strength';
  });

  loginForm?.addEventListener('submit', async (e) => {    e.preventDefault();
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    try {
      await apiCall('/api/login', 'POST', {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        remember_me: document.getElementById('remember').checked
      });
      Toast.show('Welcome back!', 'success');
      window.location.href = '/dashboard';
    } catch (err) {
      Toast.show(err.message, 'error');
      btn.disabled = false;
    }
  });

  signupForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('signupBtn');
    btn.disabled = true;
    try {
      await apiCall('/api/signup', 'POST', {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        confirm_password: document.getElementById('confirm_password').value
      });
      Toast.show('Account created!', 'success');
      window.location.href = '/dashboard';
    } catch (err) {
      Toast.show(err.message, 'error');
      btn.disabled = false;
    }
  });
});
