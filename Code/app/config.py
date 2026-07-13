"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage" / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "storage" / "uploads"

for directory in (STORAGE_DIR, UPLOADS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "edugenie-dev-secret-change-in-production")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
LAMINI_MODEL = os.getenv("LAMINI_MODEL", "MBZUAI/LaMini-Flan-T5-783M")
USE_LOCAL_LAMINI = os.getenv("USE_LOCAL_LAMINI", "false").lower() == "true"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
APP_NAME = os.getenv("APP_NAME", "EduGenie")
SESSION_MAX_AGE = int(os.getenv("SESSION_MAX_AGE", "604800"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
