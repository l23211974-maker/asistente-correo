# -*- coding: utf-8 -*-
"""Tests del chatbot decisor (modo rules, determinístico)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from asistente_correo.chatbot import responder_rules, responder
from asistente_correo.priorizador import priorizar, ordenar


def _resultados():
    return ordenar([
        priorizar({"id": "m1", "asunto": "URGENTE: sistema caído", "cuerpo": "accion requerida", "remitente": "soporte@x.com"}),
        priorizar({"id": "m5", "asunto": "Newsletter semanal", "cuerpo": "oferta descuento", "remitente": "promos@x.com"}),
    ])


def test_chatbot_primero_sugiere_rojo():
    r = responder_rules("¿qué atiendo primero?", _resultados())
    assert "sistema caído" in r.lower()


def test_chatbot_busca_keyword():
    r = responder_rules("/busca newsletter", _resultados())
    assert "newsletter" in r.lower()


def test_chatbot_sin_correos_no_explota():
    assert responder_rules("qué hago", []) != ""


def test_chatbot_responder_rules_no_llama_ollama():
    assert "Empieza" in responder("qué atiendo primero", _resultados(), "rules")
