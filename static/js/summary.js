document.addEventListener('DOMContentLoaded', () => {
  let summaryType = 'medium', lastSummary = '';
  const output = document.getElementById('summaryOutput');
  const uploadZone = document.getElementById('uploadZone');
  const fileInput = document.getElementById('fileUpload');

  document.querySelectorAll('.type-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      summaryType = btn.dataset.type;
    });
  });

  uploadZone?.addEventListener('click', () => fileInput.click());
  uploadZone?.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('dragover'); });
  uploadZone?.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
  uploadZone?.addEventListener('drop', e => { e.preventDefault(); uploadZone.classList.remove('dragover'); handleFile(e.dataTransfer.files[0]); });
  fileInput?.addEventListener('change', () => handleFile(fileInput.files[0]));

  async function handleFile(file) {
    if (!file) return;
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch('/api/upload', { method: 'POST', body: form, credentials: 'same-origin' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      Toast.show(`Loaded: ${data.filename}`, 'success');
      const textarea = document.getElementById('summaryText');
      textarea.value = (textarea.value ? textarea.value + '\n\n' : '') + data.text;
    } catch (err) { Toast.show(err.message, 'error'); }
  }

  document.getElementById('summarizeBtn')?.addEventListener('click', async () => {
    const text = document.getElementById('summaryText').value.trim();
    if (text.length < 10) return Toast.show('Enter at least 10 characters', 'error');

    showLoading(output);
    try {
      const data = await apiCall('/api/summary', 'POST', { text, summary_type: summaryType });
      lastSummary = data.response;
      output.innerHTML = `
        <div class="output-actions" id="summaryActions" style="display:flex">
          <button class="btn btn-ghost btn-sm" id="copySummary"><i class="fas fa-copy"></i> Copy</button>
          <button class="btn btn-ghost btn-sm" id="downloadSummary"><i class="fas fa-file-pdf"></i> PDF</button>
        </div>
        <div class="markdown-body">${data.html || renderMarkdown(data.response)}</div>`;
      document.getElementById('copySummary').addEventListener('click', () => copyToClipboard(lastSummary));
      document.getElementById('downloadSummary').addEventListener('click', downloadPdf);
    } catch (err) {
      output.innerHTML = `<div class="empty-state"><p>${err.message}</p></div>`;
      Toast.show(err.message, 'error');
    }
  });

  async function downloadPdf() {
    const res = await fetch('/api/export/summary-pdf', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
      body: JSON.stringify({ title: 'Summary', content: lastSummary })
    });
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'summary.pdf';
    a.click();
  }
});
