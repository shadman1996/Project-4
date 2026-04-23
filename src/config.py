"""
Project 4 — Configuration loader.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# --- Gemini ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- Project ---
PROJECT_DIR: str = os.getenv("PROJECT_DIR", str(_PROJECT_ROOT))

# --- Agent color map (for Chainlit UI) ---
AGENT_COLORS = {
    "Coordinator":  "#6366f1",  # Indigo
    "Search-A":     "#f59e0b",  # Amber
    "Search-B":     "#d97706",  # Dark Amber
    "Verification": "#10b981",  # Emerald
    "Ranking":      "#8b5cf6",  # Violet
    "Synthesis":    "#ec4899",  # Pink
    "Data":         "#06b6d4",  # Cyan
}

AGENT_ICONS = {
    "Coordinator":  "🎯",
    "Search-A":     "🔍",
    "Search-B":     "🔎",
    "Verification": "✅",
    "Ranking":      "📊",
    "Synthesis":    "📝",
    "Data":         "💾",
}
