# -*- coding: utf-8 -*-
"""Motor determinístico de semáforo: score -> rojo/amarillo/verde.

Trazabilidad: devuelve score, keywords detectadas y motivo.
El LLM (asistente_ia.py) solo explica; nunca cambia el color.
"""
import re
import unicodedata

from .keywords import ROJO, AMARILLO, VERDE


def normalizar(texto: str) -> str:
    texto = (texto or "").lower()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))
    return texto


def _texto_correo(correo: dict) -> tuple[str, str]:
    asunto = correo.get("asunto", "")
    cuerpo = correo.get("cuerpo", "") or correo.get("snippet", "")
    return normalizar(asunto), normalizar(f"{asunto} {cuerpo}")


def priorizar(correo: dict) -> dict:
    asunto_norm, texto = _texto_correo(correo)
    score, halladas = 10, []
    hay_senal_roja = False

    for palabra, peso in {**ROJO, **AMARILLO, **VERDE}.items():
        if re.search(rf"\b{re.escape(palabra)}\b", texto):
            score += peso
            halladas.append(palabra)
            if palabra in ROJO:
                hay_senal_roja = True

    # Señales de forma (no cambian el contrato, solo suman evidencia)
    raw = (correo.get("asunto", "") or "") + " " + (correo.get("cuerpo", "") or "")
    letras = [c for c in raw if c.isalpha()]
    if letras and sum(1 for c in letras if c.isupper()) / len(letras) > 0.6 and len(letras) > 12:
        score += 10
        halladas.append("mayusculas")
    if raw.count("!") >= 3:
        score += 10
        halladas.append("exclamaciones")

    score = max(0, min(100, score))
    # Regla de oro: rojo exige señal roja explícita; acumular amarillos no lo alcanza.
    if score >= 70 and hay_senal_roja:
        color = "rojo"
        motivo = "Prioridad critica/urgente: atender hoy."
    elif score >= 40:
        color = "amarillo"
        motivo = "Prioridad media: atender esta semana."
    else:
        color = "verde"
        motivo = "Prioridad baja, pero no menos importante: revisar cuando aplique."

    return {
        "id": correo.get("id", ""),
        "color": color, "score": score, "keywords": halladas, "motivo": motivo,
        "asunto": correo.get("asunto", ""),
        "remitente": correo.get("remitente", ""),
    }


def ordenar(resultados: list[dict]) -> list[dict]:
    """Rojo primero, luego amarillo, luego verde; dentro, fecha desc no disponible aquí."""
    orden = {"rojo": 0, "amarillo": 1, "verde": 2}
    return sorted(resultados, key=lambda r: (orden[r["color"]], -r["score"]))
