document.addEventListener('DOMContentLoaded', () => {
  const hoursSlider = document.getElementById('pathHours');
  const hoursVal = document.getElementById('pathHoursVal');
  const output = document.getElementById('pathOutput');
  let lastResponse = '';
  let lastTopic = '';

  hoursSlider?.addEventListener('input', () => {
    hoursVal.textContent = hoursSlider.value;
  });

  document.getElementById('generatePathBtn')?.addEventListener('click', async () => {
    const topic = document.getElementById('pathTopic').value.trim();
    const goal = document.getElementById('pathGoal').value.trim();
    if (!topic || !goal) return Toast.show('Fill in all fields', 'error');

    lastTopic = topic;
    const btn = document.getElementById('generatePathBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Generating...';
    showLoading(output);

    try {
      const data = await apiCall('/api/learning-path', 'POST', {
        topic,
        current_level: document.getElementById('pathLevel').value,
        weekly_hours: parseInt(hoursSlider.value),
        goal
      });
      lastResponse = data.response;
      output.innerHTML = `
        <div class="output-toolbar">
          <span class="badge badge-learn">${data.model}</span>
          <div class="output-actions">
            <button class="btn btn-ghost btn-sm" id="copyPath"><i class="fas fa-copy"></i> Copy</button>
            <button class="btn btn-ghost btn-sm" id="downloadPathTxt"><i class="fas fa-file-alt"></i> TXT</button>
            <button class="btn btn-primary btn-sm" id="downloadPathPdf"><i class="fas fa-file-pdf"></i> Download PDF</button>
          </div>
        </div>
        <div class="markdown-body path-content">${data.html || renderMarkdown(data.response)}</div>`;

      document.getElementById('copyPath').addEventListener('click', () => copyToClipboard(lastResponse));
      document.getElementById('downloadPathTxt').addEventListener('click', downloadTxt);
      document.getElementById('downloadPathPdf').addEventListener('click', downloadPdf);
      Toast.show('Learning path generated!', 'success');
    } catch (err) {
      output.innerHTML = `<div class="empty-state"><i class="fas fa-exclamation-triangle"></i><p>${err.message}</p></div>`;
      Toast.show(err.message, 'error');
    }
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-map"></i> Generate Learning Path';
  });

  function downloadTxt() {
    const header = `Learning Path: ${lastTopic}\n${'='.repeat(40)}\n\n`;
    const blob = new Blob([header + lastResponse], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `learning-path-${lastTopic.replace(/\s+/g, '-').toLowerCase()}.txt`;
    a.click();
    Toast.show('Downloaded as TXT', 'success');
  }

  async function downloadPdf() {
    const res = await fetch('/api/export/learning-path-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ title: `Learning Path: ${lastTopic}`, content: lastResponse })
    });
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `learning-path-${lastTopic.replace(/\s+/g, '-').toLowerCase()}.pdf`;
    a.click();
    Toast.show('Downloaded as PDF', 'success');
  }
});
