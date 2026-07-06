document.addEventListener('DOMContentLoaded', () => {
  let level = 'beginner';
  const output = document.getElementById('explainOutput');

  document.querySelectorAll('.level-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      level = btn.dataset.level;
    });
  });

  document.getElementById('explainBtn')?.addEventListener('click', async () => {
    const topic = document.getElementById('topicInput').value.trim();
    if (!topic) return Toast.show('Enter a topic', 'error');

    showLoading(output);
    try {
      const data = await apiCall('/api/explain', 'POST', { topic, level });
      output.innerHTML = `
        <div class="output-header"><span class="badge badge-explain">${data.model}</span></div>
        <div class="markdown-body">${data.html || renderMarkdown(data.response)}</div>
        <div class="output-actions" style="display:flex;margin-top:16px">
          <button class="btn btn-ghost btn-sm" onclick="copyToClipboard(\`${data.response.replace(/`/g,'')}\`)"><i class="fas fa-copy"></i> Copy</button>
        </div>`;
    } catch (err) {
      output.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>${err.message}</p></div>`;
      Toast.show(err.message, 'error');
    }
  });
});
