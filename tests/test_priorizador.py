# -*- coding: utf-8 -*-
"""Tests del motor de semáforo. Un caso por peso/keyword nueva."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from asistente_correo.priorizador import priorizar, ordenar


def test_rojo_urgente():
    r = priorizar({"id": "1", "asunto": "URGENTE: sistema caído", "cuerpo": "accion requerida inmediata", "remitente": "a@b.com"})
    assert r["color"] == "rojo" and r["score"] >= 70


def test_rojo_pago_vencido():
    r = priorizar({"id": "2", "asunto": "Factura vencida", "cuerpo": "pago vencido", "remitente": "banco@x.com"})
    assert r["color"] == "rojo" and "pago vencido" in r["keywords"]


def test_amarillo_reunion():
    r = priorizar({"id": "3", "asunto": "Reunión mañana", "cuerpo": "trae el reporte para la entrega", "remitente": "jefe@x.com"})
    assert r["color"] == "amarillo" and 40 <= r["score"] < 70


def test_verde_newsletter():
    r = priorizar({"id": "4", "asunto": "Newsletter", "cuerpo": "oferta y descuento", "remitente": "promo@x.com"})
    assert r["color"] == "verde" and r["score"] < 40
    assert "prioridad baja" in r["motivo"].lower()


def test_verde_default_sin_senales():
    r = priorizar({"id": "5", "asunto": "Hola", "cuerpo": "te escribo solo para saludar", "remitente": "a@b.com"})
    assert r["color"] == "verde"


def test_amarillos_acumulados_no_llegan_a_rojo():
    # Muchos amarillos sin señal roja no deben volverse rojos.
    r = priorizar({"id": "x", "asunto": "reunión mañana", "cuerpo": "entrega reporte cotización esta semana por favor", "remitente": "j@x.com"})
    assert r["color"] != "rojo"


def test_orden_rojo_primero():
    resultados = [
        priorizar({"id": "v", "asunto": "Newsletter", "cuerpo": "promo", "remitente": "x@y.com"}),
        priorizar({"id": "r", "asunto": "urgente", "cuerpo": "emergencia", "remitente": "x@y.com"}),
        priorizar({"id": "a", "asunto": "reunión", "cuerpo": "entrega", "remitente": "x@y.com"}),
    ]
    assert [r["id"] for r in ordenar(resultados)] == ["r", "a", "v"]
