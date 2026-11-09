# Arquitectura — Asistente-Correo

## Visión general

Pipeline en 5 etapas, cada una independiente y testeable:

```
(1) Gmail API / demo ──► (2) Normalización ──► (3) Palabras clave ──► (4) Score/Semáforo ──► (5) Informe / Chatbot
     gmail_client.py        texto plano            keywords.py         priorizador.py          informe.py · chatbot.py
```

## Módulos (src/asistente_correo/)

| Módulo | Responsabilidad | Entrada → Salida |
|---|---|---|
| `gmail_client.py` | Lectura Gmail (OAuth offline) o mock; parseo MIME (`Subject/From/Date/cuerpo/snippet`, base64url, truncado 4000) | `listar(limit, query) → [{id, asunto, cuerpo, snippet, remitente, fecha}]` |
| `priorizador.py` | Motor determinístico; normaliza (minúsculas, sin acentos), busca frases con regex `\b...?\b` | `priorizar(correo) → {color, score, keywords, motivo, asunto, remitente}` |
| `keywords.py` | Listas ponderadas ROJO/AMARILLO/VERDE | Constantes versionadas auditables |
| `chatbot.py` | Decisor: `rules` (heurísticas `/primero`, `/busca`...) + `ollama` (prompt con contexto, fallback a reglas) | `responder(pregunta, resultados) → str` |
| `informe.py` | HTML visual imprimible (`@media print`, filtros JS) | `generar_html(resultados, ruta)` |
| `cli.py` / `menu.py` | CLI (`--autenticar/--inbox/--demo/--imprimir/--chat/--pregunta`) y menú doble clic | Salida a consola + `informe.html` |
| `asistente_ia.py` | Compat: resumen textual del veredicto | `resumir(resultado) → str` |

## Reglas del semáforo

- Base **10** + pesos por palabra (**10–35**) + forma (MAYÚSCULAS sostenidas / ≥3 `!`: +10 c/u), total recortado a **0–100**.
- **Rojo:** `score ≥ 70` **y** al menos una señal roja explícita. Acumular amarillos nunca llega a rojo.
- **Amarillo:** `score 40–69`. **Verde:** `< 40` (siempre visible).
- Cada veredicto conserva `score`, `keywords` y `motivo` (trazabilidad para evaluar F1 por color contra etiquetado manual).

## OAuth (Gmail API)

`InstalledAppFlow` con `access_type=offline`, `prompt=consent`, `include_granted_scopes=false`, redirect `http://localhost:3000/api/auth/google/callback`. Mini-servidor local captura `code` (o `--manual` lo pega). `token.json` se refresca con `refresh_token`. Scopes: `readonly` + `labels` + `modify` (solo lectura usada hoy).

## Dependencias

Solo stdlib + `google-api-python-client`, `google-auth-oauthlib`, `python-dotenv`, `pytest`. Ollama vía HTTP stdlib (`/api/generate`), sin SDK.

## Pruebas

`tests/test_priorizador.py` (7) + `tests/test_chatbot.py` (4) = **11 en verde** en Python 3.14 (venv).
