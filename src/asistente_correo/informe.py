# -*- coding: utf-8 -*-
"""Informe HTML visual imprimible: semáforo rojo/amarillo/verde."""
import html
from collections import Counter

COLORES = {"rojo": "#e11d48", "amarillo": "#d97706", "verde": "#16a34a"}


def generar_html(resultados: list[dict], ruta: str) -> str:
    conteo = Counter(r["color"] for r in resultados)
    tarjetas = []
    for r in resultados:
        color = COLORES.get(r["color"], "#64748b")
        keywords = "".join(f'<span class="chip">{html.escape(k)}</span>' for k in r["keywords"]) or '<span class="chip">ninguna</span>'
        tarjetas.append(f"""
        <article class="card" data-color="{r["color"]}" data-score="{r["score"]}">
          <div class="bar" style="background:{color}"></div>
          <header><strong>{html.escape(r["asunto"] or "(sin asunto)")}</strong>
          <span class="score">{r["score"]}</span></header>
          <p class="meta">{html.escape(r["remitente"])} · {html.escape(r.get("fecha",""))}</p>
          <p class="motivo">{html.escape(r["motivo"])}</p>
          <p class="kws">{keywords}</p>
        </article>""")
    documento = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Bandeja priorizada</title>
    <style>body{{font-family:Segoe UI,system-ui,sans-serif;background:#f8fafc;color:#0f172a;max-width:900px;margin:auto;padding:16px}}
    .filtros{{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}}button{{padding:6px 12px;border-radius:999px;border:1px solid #cbd5e1;cursor:pointer;background:#fff}}
    button.activo{{background:#0f172a;color:#fff}} .card{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:12px;margin:10px 0;position:relative;overflow:hidden}}
    .bar{{position:absolute;inset:0 auto 0 0;width:6px}} .score{{float:right;font-weight:700}} .chip{{background:#f1f5f9;border-radius:6px;padding:2px 8px;margin:2px;font-size:12px}}
    .meta,.motivo{{margin:6px 0;color:#475569}} input{{width:100%;padding:8px;border-radius:8px;border:1px solid #cbd5e1}}
    .acciones{{display:flex;gap:8px;align-items:center;margin:12px 0}} .imprimir{{background:#0f172a;color:#fff;border:none}}
    @media print{{
      .filtros,input,.acciones button{{display:none!important}}
      body{{background:#fff;max-width:none}}
      .card{{break-inside:avoid;border:1px solid #999}}
      .bar{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
    }}</style></head>
    <body><h1>Bandeja priorizada</h1>
    <p>🔴 Rojos: {conteo.get("rojo",0)} · 🟡 Amarillos: {conteo.get("amarillo",0)} · 🟢 Verdes: {conteo.get("verde",0)} (baja, pero no menos importante)</p>
    <div class="acciones"><button class="imprimir" onclick="window.print()">🖨 Imprimir / Guardar PDF</button></div>
    <input id="q" placeholder="Buscar asunto, remitente o keyword…">
    <div class="filtros"><button data-f="todos" class="activo">Todos</button><button data-f="rojo">🔴 Rojo</button><button data-f="amarillo">🟡 Amarillo</button><button data-f="verde">🟢 Verde</button></div>
    <main id="lista">{''.join(tarjetas)}</main>
    <script>const q=document.getElementById('q');let f='todos';
    document.querySelectorAll('.filtros button').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.filtros button').forEach(x=>x.classList.remove('activo'));b.classList.add('activo');f=b.dataset.f;filtrar();}});
    q.oninput=filtrar;function filtrar(){{document.querySelectorAll('.card').forEach(c=>{{c.style.display=((f==='todos'||c.dataset.color===f)&&c.textContent.toLowerCase().includes(q.value.toLowerCase()))?'':'none';}});}}</script>
    </body></html>"""
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write(documento)
    return ruta


def imprimir(resultados: list[dict], ruta_html: str = "informe.html") -> str:
    """Genera el HTML y abre el navegador con el diálogo de impresión listo (Ctrl+P)."""
    import webbrowser
    generar_html(resultados, ruta_html)
    webbrowser.open(ruta_html)
    print(f"Informe listo para imprimir: {ruta_html} (usa el botón 'Imprimir / Guardar PDF' o Ctrl+P)")
    return ruta_html
