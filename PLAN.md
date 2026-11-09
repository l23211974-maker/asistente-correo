# PLAN de organización y producción — asistente-correo

**Tema:** Investigación aplicada en tecnologías — uso de la IA para automatizar la revisión de correos y organizarlos por prioridad.
**Ubicación:** `C:\Users\Max\dev\asistente-correo` · **Stack:** Python 3.14 (`python -m`) · **Fuente de correos:** Gmail API (OAuth `access_type=offline`) con fallback `mock` · **Asistente IA:** motor de reglas auditable + LLM que refina/resume (nunca decide el color solo).

## 1. Semáforo de prioridades (diseño)

| Color | Regla | Ejemplos de señales | Acción en el sistema |
|---|---|---|---|
| 🔴 **rojo** | Score ≥ 70 | `urgente`, `asap`, `emergencia`, `crítico`, `acción requerida`, `pago vencido`, `factura vencida`, `fuera de servicio`, `sin acceso`, `bloqueado`, `phishing`, `demanda`/`legal`, `inmediato`, `vence hoy` + ≥3 `!` o MAYÚSCULAS sostenidas | Cima de la lista, etiqueta `Prioridad/Rojo`, orden primero |
| 🟡 **amarillo** | 40–69 | `mañana`, `esta semana`, `reunión`, `entrega`, `cotización`, `solicitud`, `reporte`, `por favor`, `deadline` sin urgencia | Sección media, etiqueta `Prioridad/Amarillo` |
| 🟢 **verde** | < 40 | `newsletter`, `promo`, `fyi`/`para tu información`, `gracias`, `sin prisa`, ausencia de señales | Sección baja, etiqueta `Prioridad/Verde` — **se conserva y se muestra siempre** ("baja, pero no menos importante") |

**Scoring:** base 10 + pesos por keyword (10–35) + señales de forma (mayúsculas, exclamaciones, remitente VIP) + urgencia temporal. Cada veredicto guarda `score`, `keywords` y `motivo` para trazabilidad académica. Normalización: minúsculas, sin acentos, búsqueda por frase en `asunto + cuerpo + snippet`.

## 2. Arquitectura de producción (pipeline en 5 etapas)

```
Gmail API (mock | real) → Normalización → Captura de keywords → Scoring/semáforo → Presentación + etiquetas
   gmail_client.py          texto plano         keywords.py          priorizador.py      cli.py / app web / labels
                                                  ↑                        ↑
                                              asistente_ia.py (LLM: resumen + explicación, opcional)
                                              SQLite (caché, historial de decisiones para métricas)
```

- **Ingesta:** `GmailClient.listar(limit, q)` paginado; `mock_correos()` para demo y tests. Nunca borra/mueve correos reales en desarrollo.
- **Captura:** listas ROJO/AMARILLO/VERDE con pesos; extrae además entidades simples (fechas, remitente, tiene adjunto).
- **IA:** `asistente_ia.py` con backends intercambiables (`rules` por defecto, `ollama` local, `api` nube). El LLM solo genera resumen corto + explicación del color; si falla, el sistema sigue con reglas.
- **Actuación:** Fase 1 solo lectura (CLI). Fase 3+ crea etiquetas `Prioridad/*` en Gmail y un panel web mínimo (HTML/CSS/JS sin framework, como CAPU).

## 3. Fases de producción (orden estricto)

| Fase | Entregable | Verificación | Estado |
|---|---|---|---|
| **0. Setup** | Estructura `src/`, `requirements.txt`, `.env.example`, `pytest` en verde | `python -m pytest` ✓ | **Hecha** |
| **1. Motor + demo** | `priorizador.py` (reglas + tests) + `cli --demo` con 6 correos mock (2 por color) | `pytest` + salida demo con semáforo | **Hecha** |
| **2. Gmail real (lectura)** | OAuth `offline`, `GmailClient` real (parseo `Subject/From/Date/cuerpo/snippet`), `--autenticar`, visual `informe.html` local | `cli --inbox` sin escribir en la bandeja | **Hecha en código** (pendiente tu `--autenticar` en navegador; `credentials.json` ya copiado de Downloads) |
| **3. Asistente IA** | Mejora de keywords con embeddings/reglas ampliadas, resumen por correo, explicación del color | Precisión medida contra etiquetado manual (F1 por color) | Pendiente |
| **4. Panel + automatización** | Panel web (filtros por color, buscador), scheduler/polling cada N min, métricas (precisión, tiempo de revisión) | Prueba manual + tests de integración | Pendiente |
| **5. Evaluación final** | Documentación de la investigación: hipótesis, método, resultados, conclusiones | Informe + demo en vivo | Pendiente |

**Criterios de salida por fase:** tests en verde (`python -m pytest`), demo ejecutable, decisiones registradas en la bóveda. No se avanza de fase con la anterior en rojo.

## 4. Organización del repo

```
asistente-correo/
├── AGENTS.md  PLAN.md  README.md  requirements.txt  .env.example  pyproject.toml
├── src/asistente_correo/   config.py · keywords.py · priorizador.py · asistente_ia.py · gmail_client.py · cli.py
├── tests/  test_priorizador.py (un test por peso/keyword nueva)
├── docs/   (capturas, resultados de evaluación)
└── .venv/  (no se commitea)
```

## 5. Riesgos y mitigaciones

- **OAuth sin `offline`** → token caduca en 1 h (bug #59820): flujo con `access_type=offline` desde el día uno; guardado fuera del repo.
- **LLM alucina el color** → el color lo decide siempre el motor de reglas versionado; el LLM solo explica.
- **Cuota Gmail API** → paginación, caché SQLite, etiquetas en batch, límite por defecto 20.
- **Privacidad** → solo lectura en Fases 1–2; sin envíos automáticos; `.env`/tokens nunca versionados.

## 6. Decisiones tomadas (usuario, 2026-11-08) y siguiente paso

- **Ubicación:** local en `C:\Users\Max\dev\asistente-correo` (no `Desktop\Proyecto`, no home). Motivo: visualizar y probar aquí; el repositorio se crea después sobre esta carpeta.
- **Fuente:** Gmail API vía OAuth (lectura real), no IMAP. `mock` queda solo para demo/tests.
- **Stack:** Python (`python -m`).
- **Siguiente paso (único bloqueante):** corre `.venv\Scripts\python -m asistente_correo.cli --autenticar` y autoriza en el navegador (escucha en `localhost:3000` o modo `--manual`). Luego `cli --inbox --html informe.html --abrir`.
