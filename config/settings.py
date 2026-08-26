import os
from pathlib import Path


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# DATA
# ============================================================

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

PROCESSED_DATA_PATH = (
    DATA_DIR / "processed_reviews.json"
)


# ============================================================
# AI
# ============================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")


# ============================================================
# DASHBOARD
# ============================================================

TOP_ASPECTS = 10


# ============================================================
# APP
# ============================================================

PAGE_TITLE = "Voice of Customer Intelligence"
PAGE_ICON = "🏨"


# Pastikan folder tersedia
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)