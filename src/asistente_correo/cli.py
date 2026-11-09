# -*- coding: utf-8 -*-
"""CLI: --autenticar | --demo (mock) | --inbox (Gmail real) + --html / --imprimir."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))  # src/

from asistente_correo.gmail_client import GmailClient, autenticar, mock_correos
from asistente_correo.priorizador import ordenar, priorizar
from asistente_correo.asistente_ia import resumir
from asistente_correo.informe import generar_html, imprimir
from asistente_correo.chatbot import chat, responder as responder_chat


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="Asistente de correos con semáforo de prioridades")
    p.add_argument("--autenticar", action="store_true", help="Flujo OAuth offline (guarda token.json)")
    p.add_argument("--manual", action="store_true", help="Pegar el code a mano en vez de captura local")
    p.add_argument("--demo", action="store_true", help="Demo con correos mock")
    p.add_argument("--inbox", action="store_true", help="Lee la bandeja real de Gmail")
    p.add_argument("--query", default="in:inbox", help="Query Gmail (def. in:inbox)")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--html", default="", help="Ruta del HTML visual, ej. informe.html")
    p.add_argument("--abrir", action="store_true", help="Abrir el HTML en el navegador")
    p.add_argument("--imprimir", action="store_true", help="Genera informe.html y lo abre listo para imprimir (Ctrl+P / Guardar PDF)")
    p.add_argument("--chat", action="store_true", help="Chatbot decisor interactivo sobre la bandeja")
    p.add_argument("--pregunta", default="", help='Chatbot de una sola vez: --pregunta "qué atiendo primero"')
    p.add_argument("--backend", default="", help="Backend chatbot: rules (def) o ollama")
    p.add_argument("--modelo", default="qwen3.5:0.8b", help="Modelo Ollama")
    args = p.parse_args()

    if args.autenticar:
        autenticar(manual=args.manual)
        return

    if args.inbox:
        cliente = GmailClient()
        if not cliente.autenticado():
            print("Sin token válido. Ejecuta primero: python -m asistente_correo.cli --autenticar")
            return
        correos = cliente.listar(limite=args.limit, query=args.query)
        print(f"Leídos {len(correos)} correos reales.")
    else:
        correos = mock_correos()

    resultados = ordenar([priorizar(c) for c in correos])
    for r in resultados:
        print(resumir(r))

    if args.pregunta:
        print(responder_chat(args.pregunta, resultados, args.backend or "rules", args.modelo))
        return
    if args.chat:
        chat(resultados, args.backend or "rules", args.modelo)
        return

    if args.imprimir:
        imprimir(resultados, args.html or "informe.html")
    elif args.html:
        generar_html(resultados, args.html)
        print(f"Informe visual: {args.html}")
        if args.abrir:
            import webbrowser
            webbrowser.open(args.html)


if __name__ == "__main__":
    main()
