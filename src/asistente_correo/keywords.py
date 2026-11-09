# -*- coding: utf-8 -*-
"""Listas de palabras clave con pesos (normalizadas: minúsculas, sin acentos).

Regla: toda keyword nueva lleva su test en tests/test_priorizador.py.
"""
ROJO = {
    "urgente": 30, "asap": 30, "emergencia": 35, "critico": 30,
    "accion requerida": 25, "inmediato": 25,
    "pago vencido": 30, "factura vencida": 30,
    "fuera de servicio": 30, "sin acceso": 25, "bloqueado": 25,
    "sistema caido": 30, "error critico": 30,
    "phishing": 30, "seguridad": 20, "demanda": 30, "legal": 25,
    "vence hoy": 20, "hoy mismo": 20, "para hoy": 20,
}
AMARILLO = {
    "manana": 15, "esta semana": 10, "reunion": 15, "entrega": 15,
    "cotizacion": 15, "solicitud": 10, "reporte": 10, "proyecto": 10,
    "por favor": 5, "deadline": 15, "programa": 10,
}
VERDE = {
    "newsletter": -30, "promo": -30, "oferta": -25, "descuento": -25,
    "para tu informacion": -15, "fyi": -15, "gracias": -10,
    "sin prisa": -10, "cuando puedas": -5,
}
