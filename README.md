# Asistente-Correo — IA que prioriza tu bandeja con un semáforo

> **Investigación aplicada en tecnologías:** asistente de IA que revisa tu bandeja de Gmail, captura palabras clave y organiza los correos por prioridad con un **semáforo**: 🔴 rojo (crítica/urgente), 🟡 amarillo (media) y 🟢 verde (baja, *pero no menos importante*). Incluye chatbot decisor, informe visual imprimible y ejecutable único con menú.

![Licencia](https://img.shields.io/badge/licencia-MIT-green) ![Python](https://img.shields.io/badge/Python-3.13%2B-blue) ![Tests](https://img.shields.io/badge/tests-11%2F11%20en%20verde-brightgreen)

---

## ¿Qué es esto, en palabras simples?

¿Se te acumula la bandeja y no sabes qué abrir primero? Este programa lee tus correos de Gmail (solo lectura, sin enviar ni borrar nada), detecta palabras que indican urgencia y los ordena con un semáforo como en el tráfico:

| Semáforo | Significado | Cuándo lo ves |
|---|---|---|
| 🔴 **rojo** | Crítica o urgente: atiende **hoy** | Arriba de todo, con puntaje ≥ 70 (requiere palabra roja explícita: *urgente, factura vencida, sin acceso...*) |
| 🟡 **amarillo** | Media: atiende **esta semana** | En medio, puntaje 40–69 (*mañana, entrega, reunión, cotización...*) |
| 🟢 **verde** | Baja: revisa cuando aplique | Abajo, puntaje < 40 — **siempre visible**, nunca se oculta ni se descarta |

Además, un **chatbot decisor** te ayuda a decidir: *¿qué atiendo primero?*, *busca "factura"*, *resumen de la bandeja*. Y el **informe visual** (`informe.html`) muestra todo con tarjetas de colores, filtros y opción de imprimir o guardar en PDF.

**Nada se decide "solo" por la IA sin explicación:** el color lo pone un motor de reglas auditable (cada correo guarda su puntaje, palabras detectadas y motivo); la IA local (Ollama) solo sugiere y explica. Si Ollama no está, todo sigue funcionando en modo reglas.

---

## Inicio rápido (Windows)

### Opción A — Ejecutable único (recomendado, doble clic)

1. Doble clic en **`AsistenteCorreo.bat`** (menú) o en **`dist\AsistenteCorreo.exe`**.
2. La primera vez elige **4) Autenticación Gmail** y sigue los pasos del navegador.
3. Luego **2) Mi bandeja real** para ver tu bandeja priorizada, o **3) Chatbot** para que te ayude a decidir.

El menú también acepta comandos directos:
```powershell
AsistenteCorreo.exe --inbox --limit 20 --html informe.html --abrir
AsistenteCorreo.exe --inbox --pregunta "qué atiendo primero"
```

### Opción B — Desde Python (desarrollo)

```powershell
cd asistente-correo
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .
.venv\Scripts\python -m pytest tests\ -v        # 11 tests en verde
.venv\Scripts\python -m asistente_correo.cli --demo          # demo sin Gmail
```

> Usa `python` (no `python3`). La primera vez conecta Gmail con:
> ```powershell
> .venv\Scripts\python -m asistente_correo.cli --autenticar
> .venv\Scripts\python -m asistente_correo.cli --inbox --limit 20 --html informe.html --abrir
> ```

---

## Funciones principales

- **Lectura real de Gmail** vía API oficial (OAuth `offline`, solo lectura). Sin credenciales → modo demo con correos de ejemplo.
- **Captura de palabras clave** con pesos y señales de forma (MAYÚSCULAS, `!!!`), normalización sin acentos ni mayúsculas.
- **Chatbot decisor** (`--chat`, `--pregunta`, `--backend ollama`): sugiere el siguiente paso, resume y busca. Comandos: `/resumen`, `/primero`, `/busca <texto>`, `/salir`.
- **Informe imprimible** (`informe.html` + botón *Imprimir / Guardar PDF*, `--imprimir`): tarjetas de colores, contadores, buscador y filtros por color.
- **Trazabilidad académica:** cada veredicto guarda `score`, `keywords` y `motivo` para evaluar precisión (F1 por color) en la investigación.

---

## Arquitectura (pinta para principiantes)

```
Gmail / demo → Normalización → Palabras clave → Score → Semáforo → Informe / Chatbot
  gmail_client.py   texto plano    keywords.py    priorizador.py       informe.py · chatbot.py
                                            ↕ reglas auditables (nunca solo LLM)
```

| Carpeta/archivo | Para qué sirve |
|---|---|
| `src/asistente_correo/gmail_client.py` | Conecta a Gmail API (OAuth) o usa correos de ejemplo. Nunca borra ni envía. |
| `src/asistente_correo/keywords.py` | Listas ROJO/AMARILLO/VERDE con pesos. Toda palabra nueva lleva test. |
| `src/asistente_correo/priorizador.py` | Motor del semáforo: `priorizar(correo) → {color, score, motivo}`. |
| `src/asistente_correo/chatbot.py` | Ayuda a decidir (`rules` siempre; `ollama` local opcional con fallback). |
| `src/asistente_correo/informe.py` | Genera el HTML visual imprimible. |
| `src/asistente_correo/cli.py` + `menu.py` | Línea de comandos y menú con doble clic. |
| `tests/` | 11 pruebas automáticas (semáforo + chatbot). |
| `docs/` | Diseño, seguridad y resultados. |

**Flujo de decisión:** base 10 + pesos por palabra (10–35) + forma → total 0–100. Rojo exige **señal roja explícita** (acumular amarillos nunca llega a rojo). Detalles en [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md).

---

## Requisitos

- Windows + Python **3.13 o superior** (probado en 3.13.15 global / 3.14.8 en venv) — o usa el `.exe`.
- Cuenta Google con Gmail. Para uso real necesitas crear un proyecto OAuth en Google Cloud (ver [`MANUAL_ADMINISTRADOR.md`](MANUAL_ADMINISTRADOR.md) § OAuth).
- Opcional: Ollama + modelo `qwen3.5:0.8b` para el modo IA local (`--backend ollama`). Sin Ollama, el modo reglas basta.

---

## Documentación

- [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md) — guía paso a paso sin tecnicismos: conectarte, leer la bandeja, imprimir, usar el chatbot, preguntas frecuentes.
- [`MANUAL_ADMINISTRADOR.md`](MANUAL_ADMINISTRADOR.md) — instalación avanzada, OAuth, seguridad, solución de problemas, despliegue y contribución.
- [`PLAN.md`](PLAN.md) — plan de producción en 5 fases; [`AGENTS.md`](AGENTS.md) — reglas para agentes de código.

---

## Privacidad y seguridad

- **Solo lectura** en esta versión: nunca envía, borra ni archiva correos reales.
- `credentials.json`, `token.json` y `.env` **nunca se suben al repo** (están en `.gitignore`). El token se renueva con `refresh_token` (offline).
- El informe local no sale de tu computadora cuando lo imprimes.

---

## Resultados (verificación)

- `pytest`: **11/11 en verde** (7 de semáforo + 4 de chatbot).
- Prueba con bandeja real: **20 correos leídos**, 1 🟡 + 19 🟢 (sin rojos en esa ventana), chatbot responde *"No hay rojos. Siguiente: UNIDAD 4..."*.

---

## Licencia

MIT — ver [`LICENSE`](LICENSE). Investigación académica: cita la fuente si reutilizas el semáforo de prioridades.
