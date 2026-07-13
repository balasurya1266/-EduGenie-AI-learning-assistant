/* Theme management */
const Theme = {
  init() {
    const saved = localStorage.getItem('edugenie-theme') || 'light';
    this.set(saved);
    document.getElementById('themeToggle')?.addEventListener('click', () => this.toggle());
    document.getElementById('darkModeToggle')?.addEventListener('change', (e) => this.set(e.target.checked ? 'dark' : 'light'));
  },
  set(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('edugenie-theme', theme);
    const icon = document.querySelector('#themeToggle i');
    if (icon) icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) toggle.checked = theme === 'dark';
  },
  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.set(current === 'dark' ? 'light' : 'dark');
    this.syncSettings();
  },
  async syncSettings() {
    try {
      await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dark_mode: document.documentElement.getAttribute('data-theme') === 'dark' })
      });
    } catch (_) {}
  }
};
document.addEventListener('DOMContentLoaded', () => Theme.init());
