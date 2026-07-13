document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('saveApiKey')?.addEventListener('click', async () => {
    try {
      await apiCall('/api/settings', 'PUT', {
        gemini_api_key: document.getElementById('apiKeyInput').value
      });
      Toast.show('API key saved!', 'success');
    } catch (err) { Toast.show(err.message, 'error'); }
  });

  document.getElementById('languageSelect')?.addEventListener('change', async (e) => {
    try {
      await apiCall('/api/settings', 'PUT', { language: e.target.value });
      Toast.show('Language updated', 'success');
    } catch (_) {}
  });

  document.getElementById('deleteHistoryBtn')?.addEventListener('click', async () => {
    if (!confirm('Delete all history?')) return;
    try {
      await apiCall('/api/history', 'DELETE');
      Toast.show('History deleted', 'success');
    } catch (err) { Toast.show(err.message, 'error'); }
  });

  document.getElementById('resetAppBtn')?.addEventListener('click', async () => {
    if (!confirm('This will reset all your data. Continue?')) return;
    try {
      await apiCall('/api/history', 'DELETE');
      Toast.show('App reset complete', 'success');
      setTimeout(() => location.href = '/dashboard', 1000);
    } catch (err) { Toast.show(err.message, 'error'); }
  });
});
