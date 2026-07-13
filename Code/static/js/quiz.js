document.addEventListener('DOMContentLoaded', () => {
  let questions = [], currentQ = 0, answers = {}, timer = null, seconds = 0, topic = '';

  document.getElementById('generateQuizBtn')?.addEventListener('click', generate);
  document.getElementById('prevQ')?.addEventListener('click', () => navigate(-1));
  document.getElementById('nextQ')?.addEventListener('click', () => navigate(1));
  document.getElementById('submitQuiz')?.addEventListener('click', showResults);
  document.getElementById('restartQuiz')?.addEventListener('click', reset);
  document.getElementById('downloadQuiz')?.addEventListener('click', downloadPdf);

  async function generate() {
    topic = document.getElementById('quizTopic').value.trim();
    if (!topic) return Toast.show('Enter a topic', 'error');

    const btn = document.getElementById('generateQuizBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loading-spinner"></div> Generating...';

    try {
      const data = await apiCall('/api/quiz', 'POST', {
        topic,
        difficulty: document.getElementById('quizDifficulty').value,
        num_questions: parseInt(document.getElementById('quizCount').value)
      });
      questions = data.questions;
      currentQ = 0; answers = {}; seconds = 0;
      document.getElementById('quizSetup').classList.add('hidden');
      document.getElementById('quizActive').classList.remove('hidden');
      document.getElementById('quizResults').classList.add('hidden');
      startTimer();
      renderQuestion();
    } catch (err) {
      Toast.show(err.message, 'error');
    }
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-play"></i> Generate Quiz';
  }

  function startTimer() {
    clearInterval(timer);
    timer = setInterval(() => {
      seconds++;
      const m = String(Math.floor(seconds / 60)).padStart(2, '0');
      const s = String(seconds % 60).padStart(2, '0');
      document.querySelector('#quizTimer span').textContent = `${m}:${s}`;
    }, 1000);
  }

  function renderQuestion() {
    const q = questions[currentQ];
    const opts = ['a', 'b', 'c', 'd'];
    document.getElementById('quizQuestion').innerHTML = `
      <h3>Question ${currentQ + 1}</h3>
      <p style="margin:16px 0;font-size:1.05rem">${q.question}</p>
      ${opts.map(l => `
        <button class="quiz-option ${answers[currentQ] === l.toUpperCase() ? 'selected' : ''}" data-opt="${l.toUpperCase()}">
          <strong>${l.toUpperCase()}.</strong> ${q['option_' + l]}
        </button>`).join('')}`;

    document.querySelectorAll('.quiz-option').forEach(btn => {
      btn.addEventListener('click', () => {
        answers[currentQ] = btn.dataset.opt;
        document.querySelectorAll('.quiz-option').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
      });
    });

    const pct = ((currentQ + 1) / questions.length) * 100;
    document.getElementById('quizProgress').style.width = pct + '%';
    document.getElementById('quizProgressText').textContent = `${currentQ + 1} / ${questions.length}`;
    document.getElementById('prevQ').disabled = currentQ === 0;
    document.getElementById('nextQ').classList.toggle('hidden', currentQ === questions.length - 1);
    document.getElementById('submitQuiz').classList.toggle('hidden', currentQ !== questions.length - 1);
  }

  function navigate(dir) {
    currentQ = Math.max(0, Math.min(questions.length - 1, currentQ + dir));
    renderQuestion();
  }

  function showResults() {
    clearInterval(timer);
    let correct = 0;
    let detail = '';
    questions.forEach((q, i) => {
      const isCorrect = answers[i] === q.correct_option;
      if (isCorrect) correct++;
      detail += `<div class="card" style="margin-bottom:12px;padding:16px">
        <p><strong>Q${i+1}:</strong> ${q.question}</p>
        <p class="${isCorrect ? 'correct' : 'incorrect'}" style="color:${isCorrect?'#10B981':'#EF4444'}">
          Your answer: ${answers[i] || 'None'} | Correct: ${q.correct_option}
        </p>
        <p class="muted">${q.explanation}</p></div>`;
    });

    const score = Math.round((correct / questions.length) * 100);
    document.getElementById('quizActive').classList.add('hidden');
    document.getElementById('quizResults').classList.remove('hidden');
    document.getElementById('scoreCircle').textContent = score + '%';
    document.getElementById('resultsDetail').innerHTML = detail;
    Toast.show(`Score: ${score}%`, score >= 70 ? 'success' : 'info');
  }

  function reset() {
    clearInterval(timer);
    document.getElementById('quizSetup').classList.remove('hidden');
    document.getElementById('quizActive').classList.add('hidden');
    document.getElementById('quizResults').classList.add('hidden');
  }

  async function downloadPdf() {
    const res = await fetch('/api/export/quiz-pdf', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
      body: JSON.stringify({ topic, questions })
    });
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'quiz.pdf';
    a.click();
  }
});
