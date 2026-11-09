# -*- coding: utf-8 -*-
"""Ingesta: Gmail API real (OAuth offline) con fallback mock.

Sin token/credenciales -> mock (nunca falla en silencio al pedir inbox real).
Nunca borra/mueve correos reales en dev; por defecto solo lectura.
"""
import base64
import os
import sys
import webbrowser
from pathlib import Path

# Raíz del proyecto (2 niveles arriba de src/asistente_correo/) o carpeta del .exe si es PyInstaller.
if getattr(sys, "frozen", False):
    PROYECTO = Path(sys.executable).resolve().parent
else:
    PROYECTO = Path(__file__).resolve().parents[2]
CREDENCIALES = PROYECTO / "credentials.json"
TOKEN = PROYECTO / "token.json"
# Si el token no está junto al exe pero sí en la carpeta de trabajo, úsalo también.
_CWD_TOKEN = Path.cwd() / "token.json"
if not TOKEN.exists() and _CWD_TOKEN.exists():
    TOKEN = _CWD_TOKEN
_CWD_CRED = Path.cwd() / "credentials.json"
if not CREDENCIALES.exists() and _CWD_CRED.exists():
    CREDENCIALES = _CWD_CRED
REDIRECT = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/google/callback")
# Lectura + etiquetas futuras; el código solo lee hasta la Fase 3.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.labels",
          "https://www.googleapis.com/auth/gmail.modify"]

MOCK = [
    {"id": "m1", "asunto": "URGENTE: sistema caído, sin acceso", "cuerpo": "El sistema esta caido desde las 8am. Accion requerida inmediata.", "remitente": "soporte@empresa.com"},
    {"id": "m2", "asunto": "Factura vencida - pago vencido", "cuerpo": "Su factura vencida vence hoy. Pague de inmediato.", "remitente": "banco@ejemplo.com"},
    {"id": "m3", "asunto": "Reunión mañana - entrega del reporte", "cuerpo": "Te pedimos el reporte de esta semana para la reunion de manana, por favor.", "remitente": "jefe@empresa.com"},
    {"id": "m4", "asunto": "Cotización solicitada", "cuerpo": "Solicitamos cotizacion para la entrega del proyecto.", "remitente": "cliente@ejemplo.com"},
    {"id": "m5", "asunto": "Newsletter semanal", "cuerpo": "Newsletter con oferta y descuento.", "remitente": "no-reply@promos.com"},
    {"id": "m6", "asunto": "Gracias por tu registro", "cuerpo": "Gracias, sin prisa. Cuando puedas completa tu perfil.", "remitente": "bienvenida@ejemplo.com"},
]


def mock_correos() -> list[dict]:
    return list(MOCK)


def _decodificar(data: str) -> str:
    try:
        return base64.urlsafe_b64decode(data + "===" ).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _extraer_cuerpo(payload: dict) -> str:
    partes = []
    mime = payload.get("mimeType", "")
    body = payload.get("body", {}).get("data")
    if body and mime in ("text/plain", "text/html"):
        partes.append(_decodificar(body))
    for p in payload.get("parts", []) or []:
        if p.get("mimeType") == "text/plain" and p.get("body", {}).get("data"):
            partes.append(_decodificar(p["body"]["data"]))
        elif p.get("parts"):
            partes.extend(_extraer_cuerpo(p) for _ in [0]) if False else partes.append(_extraer_cuerpo(p))
    # Filtra basura vacía y recorta a 4000 caracteres para priorizar.
    texto = " ".join(partes).strip()
    return texto[:4000]


def _parsear_mensaje(m: dict) -> dict:
    headers = {h["name"].lower(): h["value"] for h in m.get("payload", {}).get("headers", [])}
    return {
        "id": m.get("id", ""),
        "thread_id": m.get("threadId", ""),
        "asunto": headers.get("subject", "(sin asunto)"),
        "remitente": headers.get("from", ""),
        "fecha": headers.get("date", ""),
        "cuerpo": _extraer_cuerpo(m.get("payload", {})),
        "snippet": m.get("snippet", ""),
        "etiquetas": m.get("labelIds", []),
    }


def obtener_credenciales(interactivo: bool = True):
    """Carga token.json, refresca si caducó o lanza flujo offline si falta."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN.write_text(creds.to_json(), encoding="utf-8")
            return creds
    if not interactivo:
        return None
    return autenticar()


def autenticar(manual: bool = False):
    """Flujo OAuth con access_type=offline (bug #59820). Captura `code` en localhost:3000."""
    from google_auth_oauthlib.flow import InstalledAppFlow
    if not CREDENCIALES.exists():
        raise FileNotFoundError(
            f"No encontré {CREDENCIALES}. Copia tu client_secret de Google Cloud como `credentials.json` en la raíz del proyecto (nunca lo subas al repo)."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENCIALES), SCOPES)
    flow.redirect_uri = REDIRECT
    # include_granted_scopes=false: si va true, Google devuelve TODOS los scopes
    # ya concedidos (Drive/Classroom/send, etc.) y fetch_token falla por mismatch.
    url, _ = flow.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="false")
    print("Abre esta URL y autoriza con tu cuenta de Gmail:")
    print(url)
    print("Usa el `code=` de ESTA corrida (no uno viejo; cada code es de un solo uso y dura minutos).")
    if manual:
        codigo = input("Pega el parámetro `code=` de la URL final: ").strip()
        try:
            flow.fetch_token(code=codigo)
        except Exception as e:
            print(f"ERROR: {e}")
            print("Repité --autenticar y usa el código nuevo de ESTA URL (ni viejo ni reutilizado).")
            raise SystemExit(1)
    else:
        try:
            webbrowser.open(url)
        except Exception:
            pass
        codigo = _esperar_codigo_local()
        if codigo is None:
            codigo = input("Pega el parámetro `code=` de la URL final: ").strip()
        try:
            flow.fetch_token(code=codigo)
        except Exception as e:
            print(f"ERROR: {e}")
            print("Repité --autenticar y usa el código nuevo de ESTA URL (ni viejo ni reutilizado).")
            raise SystemExit(1)
    TOKEN.write_text(flow.credentials.to_json(), encoding="utf-8")
    print(f"Token guardado en {TOKEN} (no se commitea).")
    return flow.credentials


def _esperar_codigo_local(puerto: int = 3000, timeout: int = 180):
    """Mini-servidor en 3000 que captura GET /api/auth/google/callback?code=..."""
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs
    import threading
    capturado = {}
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            capturado["code"] = qs.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Autorizado. Puedes volver al terminal.</h1>")
        def log_message(self, *a):
            pass
    try:
        srv = HTTPServer(("localhost", puerto), H)
    except OSError:
        return None
    srv.timeout = 1
    print(f"Escuchando en http://localhost:{puerto}/api/auth/google/callback (o pega el code manualmente)...")
    import time
    inicio = time.time()
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    while "code" not in capturado and time.time() - inicio < timeout:
        time.sleep(0.3)
    srv.shutdown()
    return capturado.get("code")


class GmailClient:
    """Cliente Gmail real con fallback mock explícito."""

    def __init__(self, forzar_mock: bool = False):
        self.forzar_mock = forzar_mock

    def autenticado(self) -> bool:
        if self.forzar_mock:
            return False
        try:
            from google.oauth2.credentials import Credentials
            return TOKEN.exists() and Credentials.from_authorized_user_file(str(TOKEN), SCOPES).valid
        except Exception:
            return False

    def listar(self, limite: int = 20, query: str = "in:inbox") -> list[dict]:
        if self.forzar_mock or not TOKEN.exists() or not CREDENCIALES.exists():
            return mock_correos()[:limite]
        from googleapiclient.discovery import build
        creds = obtener_credenciales()
        servicio = build("gmail", "v1", credentials=creds)
        respuesta = servicio.users().messages().list(
            userId="me", maxResults=limite, q=query, includeSpamTrash=False).execute()
        correos = []
        for ref in respuesta.get("messages", []):
            detalle = servicio.users().messages().get(
                userId="me", id=ref["id"], format="full").execute()
            correos.append(_parsear_mensaje(detalle))
        return correos
