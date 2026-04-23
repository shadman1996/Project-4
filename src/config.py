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
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

# --- Model Fallback Chain ---
# Ordered by: quality → quota size. Models with 0/0 quota are excluded.
# When a model hits 429/quota, the LLM wrapper auto-rotates to the next one.
MODEL_FALLBACK_CHAIN: list[str] = [
    "gemini-3.1-flash-lite-preview",  # 500 RPD  — primary (best free text model)
    "gemini-2.5-flash-lite",          # 20  RPD  — fallback
    "gemini-3-flash-preview",         # 20  RPD  — fallback
    "gemma-4-31b-it",                 # 1,500 RPD — high capacity
    "gemma-4-26b-a4b-it",             # 1,500 RPD — high capacity
    "gemma-3-27b-it",                 # 14,400 RPD — massive quota (largest Gemma)
    "gemma-3-12b-it",                 # 14,400 RPD — large Gemma
    "gemma-3-4b-it",                  # 14,400 RPD — medium Gemma
    "gemma-3-1b-it",                  # 14,400 RPD — last resort (smallest)
]

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
