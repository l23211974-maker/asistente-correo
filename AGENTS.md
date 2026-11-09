# AGENTS.md — asistente-correo

Investigación aplicada: asistente de IA que revisa la bandeja de entrada, captura palabras clave y prioriza con semáforo **rojo (crítica/urgente) · amarillo (media) · verde (baja)**. Verde sigue siendo importante: nunca se oculta ni se descarta.

## Comandos (única fuente de verdad)

```powershell
cd C:\Users\Max\dev\asistente-correo
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .            # obligatorio: hace importable asistente_correo
.venv\Scripts\python -m pytest tests\ -v            # suite completa (reglas + integración mock)
.venv\Scripts\python -m pytest tests\test_priorizador.py -v  # solo motor de semáforo
.venv\Scripts\python -m asistente_correo.cli --autenticar  # OAuth offline una vez (abre navegador, guarda token.json)
.venv\Scripts\python -m asistente_correo.cli --inbox --limit 20  # Gmail real
.venv\Scripts\python -m asistente_correo.cli --demo --html informe.html --abrir  # visual local
.venv\Scripts\python -m asistente_correo.cli --inbox --html informe.html --abrir  # bandeja real + visual
.venv\Scripts\python -m asistente_correo.cli --inbox --imprimir  # bandeja real + abre informe listo para imprimir/Ctrl+P
.venv\Scripts\python -m asistente_correo.cli --inbox --chat  # chatbot interactivo (rules; --backend ollama para LLM local)
.venv\Scripts\python -m asistente_correo.cli --inbox --pregunta "qué atiendo primero"  # chatbot una vez
# Ejecutable único (doble clic):
# - `AsistenteCorreo.bat` → menú 1-5 (demo/bandeja/chat/auth/demo+chat)
# - `dist\AsistenteCorreo.exe` (34 MB, PyInstaller) → mismo menú; o CLI: `AsistenteCorreo.exe --inbox --pregunta "..."`
#   El exe busca `credentials.json`/`token.json` junto a sí mismo y en la carpeta actual.
```

- Usa `python` (global 3.13.15; venv 3.14.8), **nunca `python3`**. Usa `python -m` (no `pytest` suelto). Sin `pip install -e .`, `python -m asistente_correo.cli` falla con `ModuleNotFoundError`.
- Orden: `install` → `install -e .` → `test` → `autenticar` → `inbox`/`demo`. No hay build/lint; si añades uno, documenta el comando aquí.

## Semáforo (regla de oro — no cambiar sin actualizar tests)

| Color | Score | Significado | Acción |
|---|---|---|---|
| 🔴 `rojo` | ≥ 70 | Crítica/urgente: atender hoy | Sube a la cima + etiqueta Gmail `Prioridad/Rojo` |
| 🟡 `amarillo` | 40–69 | Media: atender esta semana | Sección media + etiqueta `Prioridad/Amarillo` |
| 🟢 `verde` | < 40 | Baja: revisar cuando aplique | Sección baja + etiqueta `Prioridad/Verde`; **se conserva siempre** |

- Lógica en `src/asistente_correo/priorizador.py` (reglas determinísticas auditables). Todo caso nuevo de palabra clave lleva su test en `tests/test_priorizador.py`.
- El LLM/chatbot (`chatbot.py`: `rules` por defecto, `ollama` con `qwen3.5:0.8b` local) solo **sugiere/explica**; nunca decide el color por sí solo. Trazabilidad: cada decisión guarda `score`, `keywords` detectadas y `motivo`.

## Arquitectura (5 etapas, cada una testeable sola)

1. **Ingesta** (`gmail_client.py`): Gmail API por OAuth → `mock` por defecto. Sin credenciales → correos mock, no error.
2. **Normalización**: minúsculas, sin acentos, asunto+cuerpo+snippet.
3. **Captura de keywords** (`priorizador.py` + `keywords.py`): listas ROJO/AMARILLO/VERDE con pesos.
4. **Priorización**: `score → color → orden` (rojo primero, luego fecha desc).
5. **Presentación + actuación**: CLI/demo primero; etiquetas Gmail solo después de la Fase 3.

Puntos de entrada reales: `priorizar(correo: dict) -> dict` y `cli --demo`. Entrypoints de datos: `mock_correos()` y `GmailClient.listar()`.

## Entorno y gotchas

- Copia `Downloads\client_secret_*.json` → `credentials.json` en la raíz del proyecto (ya hecho; está en `.gitignore`). Copia `.env.example` → `.env`. Variables: `GOOGLE_REDIRECT_URI` (def. `http://localhost:3000/api/auth/google/callback`, ya registrada en tu client_secret), `LLM_BACKEND`.
- Flujo OAuth **exige `access_type=offline`** (sin él, el token expira en 1 h: bug #59820). `token.json` y `credentials.json` nunca se commitean. Si el puerto 3000 está ocupado (CAPU), usa `--autenticar --manual` y pega el `code=`.
- Gmail API: solo lectura (`gmail.readonly` + `gmail.modify` pedido para etiquetas futuras). No muevas/borres correos reales en dev sin confirmación del usuario. El MCP `search_threads` de OpenCode también exige autorización (bug #59820); la lectura real de esta app va por `token.json` propio.
- Responde en **español**; documenta decisiones en la bóveda (`Desktop\obsidian\Maximiliano`) según `C:\Users\Max\AGENTS.md`.

## Estado

Fase 1 (motor + demo mock) y Fase 2 (Gmail real + visual `informe.html` imprimible con `@media print`, lectura) implementadas y en verde. `--imprimir` abre el informe listo para imprimir/Guardar PDF. Chatbot decisor listo (`--chat`/`--pregunta`, `rules` + `ollama` local con fallback; el modelo `qwen3.5:0.8b` es lento y puede dar timeout → cae a reglas). Fase 3+: etiquetas `Prioridad/*` y asistente IA en el informe — ver `PLAN.md`.
