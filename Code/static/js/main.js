document.addEventListener('DOMContentLoaded', () => {
  // Scroll reveal
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

  // Password toggle
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      const icon = btn.querySelector('i');
      if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
      } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
      }
    });
  });
});

async function apiCall(url, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin' };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.message || 'Request failed');
  return data;
}

function renderMarkdown(text) {
  if (typeof marked !== 'undefined') {
    const html = marked.parse(text);
    setTimeout(() => document.querySelectorAll('pre code').forEach(b => hljs?.highlightElement(b)), 50);
    return html;
  }
  return text.replace(/\n/g, '<br>');
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => Toast.show('Copied to clipboard!', 'success'));
}

function showLoading(el) {
  el.innerHTML = '<div class="empty-state"><div class="loading-spinner"></div><p>Generating...</p></div>';
}
