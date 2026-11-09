# -*- coding: utf-8 -*-
"""Asistente IA (Fase 3): solo resúmenes y explicación. Nunca decide el color."""
import os


def resumir(resultado: dict) -> str:
    backend = os.getenv("LLM_BACKEND", "rules")
    if backend == "rules":
        return f"[{resultado['color']}] {resultado['asunto']} — {resultado['motivo']} (score {resultado['score']}, keywords: {', '.join(resultado['keywords']) or 'ninguna'})"
    # TODO Fase 3: Ollama local o API nube según LLM_BACKEND; fallback a rules ante error.
    return resumir({**resultado, "asunto": resultado["asunto"]})
