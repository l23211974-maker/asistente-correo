# -*- coding: utf-8 -*-
"""Lanzador con menú: punto de entrada único (doble clic o `python menu.py`).

Opciones: demo, bandeja real + informe imprimible, chatbot, autenticación.
Sin argumentos muestra el menú; con `--inbox`, `--demo`, etc. pasa al CLI.
"""
import os
import sys

# Permite `python menu.py` y `python -m asistente_correo.menu`
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from asistente_correo.gmail_client import GmailClient, autenticar, mock_correos
from asistente_correo.priorizador import ordenar, priorizar
from asistente_correo.asistente_ia import resumir
from asistente_correo.informe import imprimir
from asistente_correo.chatbot import chat


def _resultados(reales: bool, limite: int = 20):
    if reales:
        cliente = GmailClient()
        if not cliente.autenticado():
            print("Sin token válido. Ejecuta primero la opción 4 (autenticación).")
            return []
        correos = cliente.listar(limite=limite, query="in:inbox")
        print(f"Leídos {len(correos)} correos reales.")
    else:
        correos = mock_correos()
    return ordenar([priorizar(c) for c in correos])


def _mostrar(resultados):
    for r in resultados:
        print(resumir(r))


def main():
    if len(sys.argv) > 1:
        from asistente_correo.cli import main as cli_main
        cli_main()
        return
    while True:
        print("\n=== ASISTENTE-CORREO (IA + semáforo) ===")
        print("1) Demo (correos de ejemplo) + informe imprimible")
        print("2) Mi bandeja real (Gmail) + informe imprimible")
        print("3) Chatbot decisor sobre mi bandeja real")
        print("4) Autenticación Gmail (solo la primera vez)")
        print("5) Demo + chatbot")
        print("0) Salir")
        op = input("Opción [0-5]: ").strip()
        if op == "0":
            break
        elif op == "1":
            _mostrar(res := _resultados(False)); imprimir(res, "informe.html")
        elif op == "2":
            _mostrar(res := _resultados(True)); 
            if res: imprimir(res, "informe.html")
        elif op == "3":
            if res := _resultados(True):
                _mostrar(res); chat(res)
        elif op == "4":
            autenticar()
        elif op == "5":
            if res := _resultados(False):
                _mostrar(res); chat(res)
        else:
            print("Opción no válida.")
        input("Enter para volver al menú...")


if __name__ == "__main__":
    main()
