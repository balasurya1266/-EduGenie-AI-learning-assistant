document.addEventListener('DOMContentLoaded', () => {
  const messagesEl = document.getElementById('chatMessages');
  const input = document.getElementById('questionInput');
  const sendBtn = document.getElementById('sendBtn');
  const useStream = document.getElementById('useStream');
  let lastResponse = '';
  let chatHistory = [];

  input?.addEventListener('input', () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  });
  input?.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } });

  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => { input.value = chip.dataset.prompt; send(); });
  });

  sendBtn?.addEventListener('click', send);
  document.getElementById('clearChat')?.addEventListener('click', () => {
    messagesEl.innerHTML = '';
    chatHistory = [];
    lastResponse = '';
    document.getElementById('downloadChat').disabled = true;
  });

  document.getElementById('downloadChat')?.addEventListener('click', () => {
    const blob = new Blob([chatHistory.map(m => `${m.role}: ${m.content}`).join('\n\n')], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'edugenie-chat.txt';
    a.click();
  });

  document.getElementById('ttsBtn')?.addEventListener('click', () => {
    if (lastResponse && window.speechSynthesis) {
      const u = new SpeechSynthesisUtterance(lastResponse.replace(/[#*`]/g, ''));
      speechSynthesis.speak(u);
    }
  });

  async function send() {
    const question = input.value.trim();
    if (!question) return;

    const welcome = messagesEl.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    addMessage('user', question);
    chatHistory.push({ role: 'User', content: question });
    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;

    const assistantEl = addMessage('assistant', '<span class="typing-dots">Thinking<span>.</span><span>.</span><span>.</span></span>', true);

    try {
      if (useStream?.checked) {
        await streamResponse(question, assistantEl);
      } else {
        const data = await apiCall('/api/ask', 'POST', { question });
        assistantEl.querySelector('.message-content').innerHTML = `<div class="markdown-body">${data.html || renderMarkdown(data.response)}</div>` + actionButtons(data.query_id);
        lastResponse = data.response;
        chatHistory.push({ role: 'Assistant', content: data.response });
      }
      document.getElementById('downloadChat').disabled = false;
    } catch (err) {
      assistantEl.querySelector('.message-content').textContent = 'Error: ' + err.message;
      Toast.show(err.message, 'error');
    }
    sendBtn.disabled = false;
  }

  async function streamResponse(question, assistantEl) {
    const contentEl = assistantEl.querySelector('.message-content');
    contentEl.innerHTML = '<div class="markdown-body typing-cursor"></div>';
    const mdEl = contentEl.querySelector('.markdown-body');
    let full = '';

    const res = await fetch('/api/ask/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({ question })
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split('\n');
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = JSON.parse(line.slice(6));
        if (data.chunk) {
          full += data.chunk;
          mdEl.innerHTML = renderMarkdown(full);
        }
        if (data.error) throw new Error(data.error);
        if (data.done) {
          lastResponse = full;
          chatHistory.push({ role: 'Assistant', content: full });
          contentEl.innerHTML = `<div class="markdown-body">${renderMarkdown(full)}</div>` + actionButtons(data.query_id);
        }
      }
    }
  }

  function addMessage(role, content, isHtml = false) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const avatar = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    div.innerHTML = `<div class="message-avatar">${avatar}</div><div class="message-content">${isHtml ? content : escapeHtml(content)}</div>`;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  function actionButtons(queryId) {
    return `<div class="message-actions">
      <button onclick="copyToClipboard(lastResponse || '')"><i class="fas fa-copy"></i> Copy</button>
      <button onclick="apiCall('/api/bookmarks','POST',{query_id:'${queryId}'}).then(()=>Toast.show('Bookmarked!','success'))"><i class="fas fa-bookmark"></i> Bookmark</button>
    </div>`;
  }

  function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
});
