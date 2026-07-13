# Performance Testing

Load, stress, and spike tests for EduGenie using [Locust](https://locust.io/).

Run all commands from the `Code/` directory.

## Setup

```bash
cd Code
pip install -r performance/requirements-perf.txt
playwright install chromium   # optional, for PDF screenshots
```

## Run tests

1. Start the app: `python run.py`
2. Run tests: `python performance/run_tests.py`
3. Generate PDF report: `python performance/generate_pdf_report.py`

Results are written to `Code/performance/results/` (gitignored).

## Endpoints tested

- `GET /` – landing page
- `GET /health` – health check
- `GET /login` – login page
- `GET /docs` – API docs

AI endpoints are excluded because they depend on external Gemini API latency.
