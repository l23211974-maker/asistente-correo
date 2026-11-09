# -*- coding: utf-8 -*-
"""Configuración desde entorno (.env). Nunca hardcodees secretos."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:
    pass

REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/google/callback")
LLM_BACKEND = os.getenv("LLM_BACKEND", "rules")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
