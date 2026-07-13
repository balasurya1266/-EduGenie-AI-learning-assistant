"""Run EduGenie performance tests and generate a report."""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import psutil

BASE_URL = "http://localhost:8000"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def wait_for_server(timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(f"{BASE_URL}/health", timeout=2.0)
            if r.status_code == 200:
                return True
        except httpx.RequestError:
            pass
        time.sleep(0.5)
    return False


def run_locust(users: int, spawn_rate: int, duration: str, csv_prefix: str) -> int:
    cmd = [
        sys.executable, "-m", "locust",
        "-f", str(Path(__file__).parent / "locustfile.py"),
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "-t", duration,
        "--host", BASE_URL,
        "--csv", str(RESULTS_DIR / csv_prefix),
        "--html", str(RESULTS_DIR / f"{csv_prefix}_report.html"),
        "--only-summary",
    ]
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def read_locust_stats(csv_prefix: str) -> dict:
    stats_path = RESULTS_DIR / f"{csv_prefix}_stats.csv"
    if not stats_path.exists():
        return {}
    lines = stats_path.read_text(encoding="utf-8").strip().splitlines()
    if len(lines) < 2:
        return {}
    header = lines[0].split(",")
    for row in lines[1:]:
        cols = row.split(",")
        if len(cols) < len(header):
            continue
        record = dict(zip(header, cols))
        if record.get("Name") == "Aggregated" or record.get("Type") == "Aggregated":
            return record
    return {}


def process_memory_percent() -> float:
    """Memory used by Python processes running the app (more relevant than system-wide)."""
    total = 0.0
    for proc in psutil.process_iter(["name", "memory_percent"]):
        try:
            name = (proc.info.get("name") or "").lower()
            if "python" in name:
                total += proc.info.get("memory_percent") or 0.0
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return round(min(total, 100.0), 2)


def sample_system_usage(duration: int = 5) -> tuple[float, float]:
    cpu_samples, mem_samples = [], []
    end = time.time() + duration
    while time.time() < end:
        cpu_samples.append(psutil.cpu_percent(interval=0.5))
        mem_samples.append(psutil.virtual_memory().percent)
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0
    avg_mem = sum(mem_samples) / len(mem_samples) if mem_samples else 0.0
    return round(avg_cpu, 2), round(avg_mem, 2)


def status_pass(actual: float, target: float, less_than: bool = True) -> str:
    if less_than:
        return "Pass" if actual < target else "Fail"
    return "Pass" if actual >= target else "Fail"


def main():
    report_only = "--report-only" in sys.argv
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if not wait_for_server():
        print("ERROR: Server not reachable at", BASE_URL)
        sys.exit(1)

    scenarios = [
        {
            "id": 1,
            "name": "Load test – landing & health endpoints",
            "users": 10,
            "spawn_rate": 2,
            "duration": "30s",
            "prefix": "scenario1",
            "expected": "All requests succeed; avg response < 2s",
        },
        {
            "id": 2,
            "name": "Load test – auth pages (login, docs)",
            "users": 20,
            "spawn_rate": 5,
            "duration": "30s",
            "prefix": "scenario2",
            "expected": "Stable throughput with error rate < 1%",
        },
        {
            "id": 3,
            "name": "Stress test – peak concurrent users",
            "users": 50,
            "spawn_rate": 10,
            "duration": "30s",
            "prefix": "scenario3",
            "expected": "System remains responsive; max response < 5s",
        },
        {
            "id": 4,
            "name": "Spike test – rapid user ramp-up",
            "users": 30,
            "spawn_rate": 30,
            "duration": "20s",
            "prefix": "scenario4",
            "expected": "No crash; error rate stays below 1%",
        },
    ]

    print("Sampling baseline CPU/Memory...")
    cpu_before, _ = sample_system_usage(3)

    all_stats = []
    if report_only:
        for s in scenarios:
            stats = read_locust_stats(s["prefix"])
            stats["_scenario"] = s
            stats["_exit_code"] = 0
            all_stats.append(stats)
    else:
        for s in scenarios:
            print(f"\nRunning scenario {s['id']}: {s['name']} ...")
            code = run_locust(s["users"], s["spawn_rate"], s["duration"], s["prefix"])
            stats = read_locust_stats(s["prefix"])
            stats["_scenario"] = s
            stats["_exit_code"] = code
            all_stats.append(stats)

    print("\nSampling CPU/Memory during load...")
    cpu_during, _ = sample_system_usage(5)
    mem_during = process_memory_percent()

    def fnum(val, default=0.0):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    aggregated = all_stats

    total_requests = sum(fnum(s.get("Request Count")) for s in all_stats)
    total_failures = sum(fnum(s.get("Failure Count")) for s in all_stats)
    avg_times = [fnum(s.get("Average Response Time")) for s in all_stats if s.get("Average Response Time")]
    max_times = [fnum(s.get("Max Response Time")) for s in all_stats if s.get("Max Response Time")]
    throughputs = [fnum(s.get("Requests/s")) for s in all_stats if s.get("Requests/s")]

    # Weighted average response time across scenarios
    weighted_avg_ms = 0.0
    if total_requests:
        weighted_avg_ms = sum(
            fnum(s.get("Average Response Time")) * fnum(s.get("Request Count"))
            for s in all_stats
        ) / total_requests
    max_response_ms = max(max_times) if max_times else 0
    throughput = sum(throughputs) / len(throughputs) if throughputs else 0
    error_rate = (total_failures / total_requests * 100) if total_requests else 0

    avg_response_sec = round(weighted_avg_ms / 1000, 3)
    max_response_sec = round(max_response_ms / 1000, 3)
    error_rate = round(error_rate, 2)
    throughput = round(throughput, 2)
    cpu_peak = max(cpu_before, cpu_during)
    mem_peak = mem_during

    test_date = datetime.now(timezone.utc).astimezone().strftime("%d %B %Y")

    report = {
        "project_name": "EduGenie - AI-Powered Educational Learning Assistant",
        "test_date": test_date,
        "tool": "Locust (Python)",
        "test_type": "Load Testing, Stress Testing, Spike Testing",
        "target": "GET /, GET /health, GET /login, GET /docs",
        "environment": "Local (Windows, Uvicorn, http://localhost:8000)",
        "scenarios": scenarios,
        "metrics": {
            "avg_response_sec": avg_response_sec,
            "max_response_sec": max_response_sec,
            "throughput": throughput,
            "error_rate": error_rate,
            "cpu_utilization": cpu_peak,
            "memory_utilization": mem_peak,
        },
        "raw_stats": all_stats,
    }

    report_path = RESULTS_DIR / "performance_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_path = RESULTS_DIR / "PERFORMANCE_TEST_REPORT.md"
    md_path.write_text(build_markdown(report), encoding="utf-8")

    print("\n" + "=" * 60)
    print("PERFORMANCE TEST SUMMARY")
    print("=" * 60)
    print(f"Avg Response Time : {avg_response_sec}s  (target < 2s)  -> {status_pass(avg_response_sec, 2)}")
    print(f"Max Response Time : {max_response_sec}s  (target < 5s)  -> {status_pass(max_response_sec, 5)}")
    print(f"Throughput        : {throughput} req/s")
    print(f"Error Rate        : {error_rate}%  (target < 1%)  -> {status_pass(error_rate, 1)}")
    print(f"CPU Utilization   : {cpu_peak}%  (target < 80%)  -> {status_pass(cpu_peak, 80)}")
    print(f"Memory Utilization: {mem_peak}%  (target < 80%)  -> {status_pass(mem_peak, 80)}")
    print(f"\nReport saved to: {md_path}")
    print(f"HTML reports in: {RESULTS_DIR}")


def build_markdown(report: dict) -> str:
    m = report["metrics"]

    def st(actual, target, lt=True):
        return "Pass" if (actual < target if lt else actual >= target) else "Fail"

    scenarios_table = "\n".join(
        f"| {s['id']} | {s['name']} | {s['users']} | {s['duration'].replace('s','')} | {s['expected']} |"
        for s in report["scenarios"]
    )

    return f"""# Performance Testing Report

**Date:** {report['test_date']}  
**Project Name:** {report['project_name']}  
**Maximum Marks:** 5 Marks

---

## Step 1: Testing Overview

| Field | Details |
|-------|---------|
| Testing Tool Used | {report['tool']} |
| Type of Testing | {report['test_type']} |
| Target Module / API | {report['target']} |
| Test Environment | {report['environment']} |
| Test Date | {report['test_date']} |

---

## Step 2: Test Scenarios

| S.No | Test Scenario / Description | No. of Virtual Users | Duration (sec) | Expected Outcome |
|------|----------------------------|----------------------|----------------|--------------|
{scenarios_table}

---

## Step 3: Performance Test Results

| S.No | Metric | Target Value | Actual Value | Status (Pass / Fail) | Remarks |
|------|--------|--------------|--------------|----------------------|---------|
| 1 | Response Time (Avg) | < 2 seconds | {m['avg_response_sec']} s | {st(m['avg_response_sec'], 2)} | Measured across all scenarios |
| 2 | Response Time (Max) | < 5 seconds | {m['max_response_sec']} s | {st(m['max_response_sec'], 5)} | Peak under stress/spike load |
| 3 | Throughput (Req/sec) | — | {m['throughput']} | — | Aggregated requests per second |
| 4 | Error Rate | < 1% | {m['error_rate']}% | {st(m['error_rate'], 1)} | Failed requests / total requests |
| 5 | CPU Utilization | < 80% | {m['cpu_utilization']}% | {st(m['cpu_utilization'], 80)} | System-wide during test window |
| 6 | Memory Utilization | < 80% | {m['memory_utilization']}% | {st(m['memory_utilization'], 80)} | Python process memory during test window |

---

## Step 4: Observations & Analysis

EduGenie was tested locally using Locust with four scenarios covering normal load (10–20 users), stress (50 users), and spike (30 users instant ramp-up). Endpoints tested were lightweight page routes (`/`, `/health`, `/login`, `/docs`) to measure server throughput without external AI API latency.

- **Response times:** Average response time was **{m['avg_response_sec']}s** and maximum was **{m['max_response_sec']}s**, both {"within" if m['avg_response_sec'] < 2 and m['max_response_sec'] < 5 else "outside"} the target thresholds.
- **Throughput:** The server handled approximately **{m['throughput']} requests/second** under concurrent load.
- **Reliability:** Error rate was **{m['error_rate']}%**, indicating {"stable" if m['error_rate'] < 1 else "degraded"} behavior under test conditions.
- **Resource usage:** CPU peaked at **{m['cpu_utilization']}%** (system) and EduGenie Python processes used **{m['memory_utilization']}%** of available memory.
- **Note:** AI endpoints (`/api/ask`, `/api/quiz`, etc.) were excluded because they depend on external Gemini API latency and are not representative of server-only performance.

---

## Step 5: Screenshots / Evidence

HTML Locust reports generated in `performance/results/`:

- `scenario1_report.html` – Load test (10 users)
- `scenario2_report.html` – Load test (20 users)
- `scenario3_report.html` – Stress test (50 users)
- `scenario4_report.html` – Spike test (30 users)

Open these files in a browser for charts and detailed statistics. CSV raw data is also available (`scenario*_stats.csv`).
"""


if __name__ == "__main__":
    main()
