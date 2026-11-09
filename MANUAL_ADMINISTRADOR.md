# Manual del Administrador — Asistente-Correo

Para quien instala, configura, protege y evoluciona el sistema.

## 1. Alcance

Sistema de investigación aplicada (Python 3.13+): lectura Gmail API (OAuth offline, solo lectura), motor de reglas con semáforo auditable, chatbot rules/Ollama, informe HTML imprimible y ejecutable PyInstaller. No envía, borra ni etiqueta correos reales en esta versión.

## 2. Instalación desde código

```powershell
cd asistente-correo
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m pytest tests\ -v
```

Verificación: 11 tests en verde; `cli --demo` imprime 2-2-2; `cli --demo --imprimir` genera `informe.html`.

### Ejecutable

```powershell
.venv\Scripts\python.exe -m PyInstaller --onefile --name AsistenteCorreo --collect-all googleapiclient --collect-all google_auth_oauthlib --collect-all google.auth menu.py
Copy-Item credentials.json,token.json dist\ -Force
```

El `.exe` busca `credentials.json`/`token.json` junto a sí mismo y en la carpeta actual; sin ellos funciona en modo demo.

## 3. OAuth en Google Cloud (paso a paso)

1. Google Cloud Console → proyecto nuevo → **APIs y servicios → Biblioteca → habilita Gmail API**.
2. **Pantalla de consentimiento OAuth** → tipo **Externo** (en modo prueba, añade tu correo como usuario de prueba; en producción requiere verificación si pides scopes sensibles).
3. **Credenciales → Crear ID de cliente OAuth → Tipo: Aplicación web**.
4. **URIs de redirección autorizadas:** `http://localhost:3000/api/auth/google/callback` (la usada por `--autenticar`).
5. Descarga el JSON → renómbralo a **`credentials.json`** en la raíz del proyecto (nunca commitees).
6. Ejecuta `--autenticar` (o `--autenticar --manual` si el 3000 está ocupado). El flujo usa `access_type=offline` + `prompt=consent` + `include_granted_scopes=false` (este último evita el error *"Scope has changed"* cuando la cuenta ya concedió scopes amplios vía MCP).
7. El token se guarda en **`token.json`** (renovado con `refresh_token`). Ejecutable: copia `token.json` a `dist/` junto al `.exe`.

Scopes pedidos: `gmail.readonly`, `gmail.labels`, `gmail.modify` (los dos últimos, reservados para etiquetas futuras; el código solo lee).

## 4. Configuración

- `.env` (opcional, nunca en git): `GOOGLE_REDIRECT_URI`, `LLM_BACKEND=rules|ollama`, `OLLAMA_MODEL` (def. `qwen3.5:0.8b`).
- Ollama local: `ollama pull qwen3.5:0.8b` y `ollama serve` en `http://localhost:11434`. El chatbot degrada a reglas si Ollama tarda/falla (timeout 120 s).

## 5. Seguridad

- Archivos sensibles (`.gitignore`): `.env`, `credentials.json`, `client_secret_*.json`, `token.json`, `informe*.html`, `build/`, `dist/`, `*.egg-info/`.
- Rotación: si un token se filtra, revócalo en Google → Seguridad → Acceso de terceros y repite `--autenticar`.
- Privacidad: la lectura es de solo lectura; no hay telemetría ni envío a terceros. Los informes son locales.

## 6. Operación y mantenimiento

- Comandos: `cli --inbox --limit N --query "..." --html/--imprimir/--chat/--pregunta "..."` (ver `AGENTS.md`).
- Cuota Gmail API: por defecto 20 correos por lectura; aumenta `--limit` solo si lo necesitas. No automatices polling sin backoff en esta fase.
- Actualizar pesos: edita `keywords.py` + añade test en `tests/test_priorizador.py` + documenta en `PLAN.md`.

## 7. Solución de problemas

| Síntoma | Causa | Acción |
|---|---|---|
| `Invalid code verifier` | Código viejo/reutilizado | Repite `--autenticar` y usa el `code=` de esa corrida al instante. |
| `Scope has changed` | `include_granted_scopes=true` y grants previos amplios | Resuelto en código (`false`); repite `--autenticar` con código nuevo. |
| `Sin token válido` | Sin `token.json` o caducado | Repite `--autenticar`; si el token caducó, se refresca solo. |
| `UnicodeEncodeError ... 💸` | Consola cp1252 | Resuelto (UTF-8 en CLI). En tu terminal: `$env:PYTHONIOENCODING="utf-8"`. |
| Puerto 3000 ocupado | CAPU u otro servicio | Usa `--autenticar --manual` y pega el `code=`. |
| Ollama timeout | Modelo 0.8b lento | Normal: cae a reglas. Para LLM, prueba `--backend rules` o un modelo menor. |
| `ModuleNotFoundError` | Falta `pip install -e .` | Ejecútalo tras `pip install -r requirements.txt`. |

## 8. Despliegue y repositorio

- Repo público en `https://github.com/l23211974-maker/asistente-correo`.
- Flujo: ramas `main`/`develop`/`feature/*` con PR; cambios de alcance en issue con plantilla.
- CI sugerida: `pip install -r requirements.txt && pip install -e . && pytest` en push/PR (ver `.github/workflows/ci.yml` si existe).

## 9. Contribuir

Ver [`CONTRIBUTING`](#contribuir) en el README o abre un issue. Toda palabra clave nueva lleva test y nota en `docs/`.
