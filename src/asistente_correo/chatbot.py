# -*- coding: utf-8 -*-
"""Chatbot decisor: ayuda a tomar decisiones sobre la bandeja priorizada.

Dos backends: `rules` (siempre disponible, determinístico) y `ollama` (local,
mismo semáforo como contexto). El chatbot NUNCA cambia el color; solo sugiere
orden, explica y propone el siguiente paso.
"""
import json
import os
import re
import urllib.request
from collections import Counter

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODELO_DEFECTO = os.getenv("OLLAMA_MODEL", "qwen3.5:0.8b")


def _contexto(resultados: list[dict], limite: int = 20) -> str:
    lineas = []
    for r in resultados[:limite]:
        lineas.append(f"[{r['color']} {r['score']}] {r['asunto']} — {r['remitente']} — {r['motivo']}")
    return "\n".join(lineas)


def _conteo(resultados: list[dict]) -> str:
    c = Counter(r["color"] for r in resultados)
    return f"🔴 {c.get('rojo',0)} rojos · 🟡 {c.get('amarillo',0)} amarillos · 🟢 {c.get('verde',0)} verdes"


def _siguiente(resultados: list[dict]) -> str:
    if not resultados:
        return "No hay correos para decidir."
    r = resultados[0]
    if r["color"] == "rojo":
        return f"Empieza por este (atender hoy): «{r['asunto']}» de {r['remitente']} (score {r['score']}, {', '.join(r['keywords']) or 'sin keywords detectadas'})."
    if r["color"] == "amarillo":
        return f"No hay rojos. Siguiente (esta semana): «{r['asunto']}» de {r['remitente']} (score {r['score']})."
    return f"Todo verde. Revisa cuando aplique, sin prisa: primero «{r['asunto']}». Recuerda: verde no significa menos importante."


def _buscar(resultados: list[dict], texto: str) -> str:
    texto = texto.strip().lower()
    hits = [r for r in resultados if texto in f"{r['asunto']} {r['remitente']} {' '.join(r['keywords'])}".lower()]
    if not hits:
        return f"No encontré nada con «{texto}»."
    lineas = [f"Encontré {len(hits)}:"]
    lineas += [f"- [{r['color']} {r['score']}] {r['asunto']} ({r['remitente']})" for r in hits[:10]]
    return "\n".join(lineas)


def responder_rules(pregunta: str, resultados: list[dict]) -> str:
    p = pregunta.strip().lower()
    if p in ("", "ayuda", "/ayuda", "help"):
        return ("Comandos: /resumen · /primero (qué atender primero) · /explica <parte del asunto> · "
                "/busca <texto> · /salir\nEj.: «¿qué atiendo primero?» o «/busca factura»")
    if any(k in p for k in ("primero", "siguiente", "que hago", "qué hago", "accion", "acción", "decidir")):
        return _siguiente(resultados)
    if p.startswith("/resumen") or "resumen" in p:
        return f"{_conteo(resultados)}\n"+_siguiente(resultados)
    if p.startswith("/busca") or p.startswith("/buscar"):
        return _buscar(resultados, p.removeprefix("/busca").removeprefix("r").strip())
    if p.startswith("/explica") or p.startswith("/explicar"):
        return _buscar(resultados, p.removeprefix("/explica").removeprefix("r").strip())
    # Pregunta libre en modo rules: mejor esfuerzo con búsqueda de palabras clave.
    palabras = [w for w in re.findall(r"\w{4,}", p) if w not in ("que", "como", "para", "esto", "este", "esta")]
    for w in palabras:
        h = _buscar(resultados, w)
        if "No encontré" not in h:
            return h
    return ("No sé cómo decidir eso con reglas. Prueba: /primero · /resumen · /busca <texto>\n"
            + _siguiente(resultados))


def responder_ollama(pregunta: str, resultados: list[dict], modelo: str = MODELO_DEFECTO) -> str:
    prompt = (
        "Eres un asistente que ayuda a MAX a decidir qué correo atender, con este semáforo: "
        "rojo=critico hoy, amarillo=esta semana, verde=baja pero no menos importante. "
        "No cambies el color. Sé breve y accionable.\n"
        f"Bandeja ({_conteo(resultados)}):\n{_contexto(resultados)}\n"
        f"Pregunta: {pregunta}\nRespuesta en español, 3-5 líneas."
    )
    datos = json.dumps({"model": modelo, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=datos,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8")).get("response", "").strip()


def responder(pregunta: str, resultados: list[dict], backend: str | None = None,
              modelo: str = MODELO_DEFECTO) -> str:
    backend = backend or os.getenv("LLM_BACKEND", "rules")
    if backend == "ollama":
        try:
            return responder_ollama(pregunta, resultados, modelo)
        except Exception as e:
            return f"[Ollama no disponible ({e}); modo reglas] " + responder_rules(pregunta, resultados)
    return responder_rules(pregunta, resultados)


def chat(resultados: list[dict], backend: str = "rules", modelo: str = MODELO_DEFECTO):
    print(responder_rules("ayuda", resultados))
    print(f"Backend: {backend} · Modelo: {modelo} · {_conteo(resultados)}")
    while True:
        try:
            p = input("Tú> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if p.lower() in ("salir", "/salir", "exit", "quit"):
            break
        print(responder(p, resultados, backend, modelo))
