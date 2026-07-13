document.addEventListener('DOMContentLoaded', () => {
  const speechBtn = document.getElementById('speechBtn');
  const questionInput = document.getElementById('questionInput');

  if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;

  speechBtn?.addEventListener('click', () => {
    recognition.start();
    speechBtn.classList.add('active');
    Toast.show('Listening...', 'info', 2000);
  });

  recognition.onresult = (e) => {
    const transcript = e.results[0][0].transcript;
    if (questionInput) questionInput.value = transcript;
    speechBtn.classList.remove('active');
  };

  recognition.onerror = () => {
    speechBtn.classList.remove('active');
    Toast.show('Speech recognition failed', 'error');
  };

  recognition.onend = () => speechBtn.classList.remove('active');
});
