# EduGenie - AI-Powered Educational Learning Assistant

<p align="center">
  <strong>Learn Smarter with AI</strong><br>
  An intelligent educational platform powered by Google Gemini 1.5 Pro and LaMini-Flan-T5
</p>

---

## Overview

**EduGenie** is a production-ready, full-stack AI educational assistant that helps students, teachers, and self-learners:

- Ask educational questions (with RAG document chat)
- Understand concepts at beginner/intermediate/advanced levels
- Generate interactive quizzes with scoring and PDF export
- Summarize notes from text, PDF, or DOCX
- Receive personalized learning roadmaps
- Track progress with analytics, streaks, and badges

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript, Jinja2 |
| Backend | FastAPI, Uvicorn, Python 3.10+ |
| AI Models | Google Gemini 1.5 Pro, LaMini-Flan-T5 (optional local) |
| Database | JSON file-based storage |
| Auth | JWT cookies with bcrypt password hashing |

## Project Structure

```
edugenie/
├── main.py                 # FastAPI app entry point
├── run.py                  # Uvicorn server runner
├── requirements.txt
├── .env.example
├── app/
│   ├── config.py           # Environment configuration
│   ├── dependencies.py     # Auth dependencies
│   ├── models/             # Pydantic schemas + JSON DB
│   ├── routes/             # Page + API routes
│   ├── services/           # Business logic
│   ├── ai/                 # AI modules (Gemini, LaMini)
│   ├── prompts/            # Prompt engineering
│   └── utils/              # Security, PDF, markdown, export
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JavaScript assets
├── performance/            # Locust load tests (optional)
└── storage/data/           # JSON database files (gitignored, auto-created)
```

## Quick Start

### 1. Clone and Setup

```bash
cd p8.1
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
SECRET_KEY=your-random-secret-key
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/apikey).

### 3. Run the Application

```bash
python run.py
```

Open **http://localhost:8000** in your browser.

### 4. Create an Account

1. Click **Sign Up** on the landing page
2. Create your account
3. Explore the dashboard and AI features

## API Endpoints

### Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/login` | Login |
| `/signup` | Registration |
| `/dashboard` | Main dashboard |
| `/ask` | Question answering (ChatGPT-style) |
| `/explain` | Concept explanation |
| `/quiz` | Quiz generator |
| `/summary` | Summarizer |
| `/learning-path` | Learning path generator |
| `/history` | History & bookmarks |
| `/profile` | User profile |
| `/settings` | App settings |

### REST APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/signup` | Register user |
| POST | `/api/login` | Authenticate |
| POST | `/api/ask` | Question answering |
| POST | `/api/ask/stream` | Streaming Q&A |
| POST | `/api/explain` | Concept explanation |
| POST | `/api/quiz` | Generate quiz |
| POST | `/api/summary` | Summarize text |
| POST | `/api/learning-path` | Generate roadmap |
| POST | `/api/upload` | Upload PDF/DOCX for RAG |
| GET | `/api/history` | Get query history |
| POST | `/api/bookmarks` | Bookmark response |
| PUT | `/api/settings` | Update settings |

Full API docs available at **http://localhost:8000/docs** (when DEBUG=true).

## AI Modules

### Question Answering (Gemini 1.5 Pro)
Structured responses with examples, key takeaways, related topics, and reference links. Supports RAG-based document chat.

### Concept Explanation (LaMini-Flan-T5)
Beginner-friendly explanations with definition, examples, analogies, and summaries. Falls back to Gemini if local model is unavailable.

### Quiz Generator (Gemini)
MCQs with difficulty levels, timer, progress bar, scoring, and PDF export.

### Summarizer (Gemini)
Multiple summary types: short, medium, detailed, bullet points, exam notes, key concepts.

### Learning Path (Gemini)
Personalized roadmaps with weekly timelines, resources, projects, milestones, and career advice.

## LaMini Local Model (Optional)

To enable offline concept explanations:

```bash
pip install transformers torch sentencepiece
```

Set in `.env`:
```
USE_LOCAL_LAMINI=true
```

## Features

- Modern SaaS landing page with animations
- Glassmorphism auth pages
- ChatGPT-style Q&A interface with streaming
- Dark/light mode toggle
- PDF & DOCX upload with RAG
- Speech-to-text and text-to-speech
- Learning analytics, streaks, badges
- Bookmark responses
- Export quiz/summary as PDF
- Responsive mobile design
- JSON database following ER diagram

## Performance Testing (Optional)

See [performance/README.md](performance/README.md) for load/stress testing with Locust.

## Push to GitHub

### What gets committed

| Included | Excluded (via `.gitignore`) |
|----------|----------------------------|
| App source (`app/`, `templates/`, `static/`) | `.env` (secrets) |
| `main.py`, `run.py`, `requirements.txt` | `venv/` |
| `performance/` test scripts | `performance/results/` (generated reports) |
| `.env.example`, `LICENSE`, `README.md` | `storage/data/*.json` (user data) |
| | `__pycache__/`, `.cursor/` |

The `performance/` folder **is included** — only the test scripts (`locustfile.py`, `run_tests.py`, etc.). Generated PDFs, HTML reports, and CSV outputs are not committed.

### Steps

```bash
# 1. Initialize git (if not already)
git init

# 2. Copy environment template and add your API key locally (never commit .env)
cp .env.example .env

# 3. Stage and commit
git add .
git commit -m "Initial commit: EduGenie AI learning assistant"

# 4. Create a repo on GitHub, then:
git remote add origin https://github.com/balasurya1266/-EduGenie-AI-learning-assistant.git
git branch -M main
git push -u origin main
```

JSON database files in `storage/data/` are created automatically on first run — no need to commit them.

## Deployment

### Production Checklist

1. Set `DEBUG=false` in `.env`
2. Use a strong `SECRET_KEY`
3. Configure HTTPS reverse proxy (nginx)
4. Run with production ASGI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Database Schema

JSON collections following the ER diagram:
- `users.json` - User accounts
- `user_queries.json` - All user queries
- `ai_responses.json` - AI generated responses
- `quizzes.json` - Quiz questions
- `summaries.json` - Summaries
- `learning_paths.json` - Learning paths
- `bookmarks.json` - Saved responses
- `documents.json` - RAG document embeddings
- `analytics.json` - User statistics

## License

MIT License - Built for educational purposes and Google Cloud Generative AI Internship portfolio.
