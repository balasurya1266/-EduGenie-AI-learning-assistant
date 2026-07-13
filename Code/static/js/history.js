document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('historyTab').classList.toggle('hidden', tab.dataset.tab !== 'history');
      document.getElementById('bookmarksTab').classList.toggle('hidden', tab.dataset.tab !== 'bookmarks');
    });
  });

  document.getElementById('historySearch')?.addEventListener('input', async (e) => {
    const q = e.target.value.trim();
    if (q.length < 2) return;
    try {
      const data = await apiCall(`/api/history/search?q=${encodeURIComponent(q)}`);
      Toast.show(`Found ${data.results.length} results`, 'info');
    } catch (_) {}
  });

  document.querySelectorAll('.bookmark-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await apiCall('/api/bookmarks', 'POST', { query_id: btn.dataset.queryId });
        Toast.show('Bookmarked!', 'success');
      } catch (err) { Toast.show(err.message, 'error'); }
    });
  });

  document.getElementById('deleteHistory')?.addEventListener('click', async () => {
    if (!confirm('Delete all history?')) return;
    try {
      await apiCall('/api/history', 'DELETE');
      Toast.show('History cleared', 'success');
      setTimeout(() => location.reload(), 1000);
    } catch (err) { Toast.show(err.message, 'error'); }
  });

  const params = new URLSearchParams(location.search);
  if (params.get('q')) document.getElementById('historySearch').value = params.get('q');
});
