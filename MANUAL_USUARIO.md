# Manual de Usuario — Asistente-Correo

Guía sin tecnicismos. Asume que solo sabes usar Gmail.

## 1. ¿Qué voy a lograr?

Voy a priorizar mi bandeja de Gmail con un semáforo: 🔴 atiendo hoy, 🟡 esta semana, 🟢 cuando aplique (sin descartar nunca nada).

## 2. ¿Qué necesito?

- Una computadora Windows.
- Mi cuenta de Gmail.
- Seguir los pasos de abajo (5 minutos la primera vez).

## 3. Primera vez: conectar Gmail (solo una vez)

1. Haz doble clic en **`AsistenteCorreo.bat`**.
2. Elige **4) Autenticación Gmail**.
3. Se abre el navegador: elige tu cuenta y pulsa **Permitir**.
4. Espera a que diga "Token guardado". Ya no necesitas repetirlo (a menos que cambies de computadora).

> Si el programa te muestra una URL y te pide pegar un `code=`, copia **solo** lo que va después de `code=` y antes de `&` y pégalo. Si ves "no se puede acceder a localhost:3000", es normal: el código ya está en la barra de direcciones.

## 4. Ver mi bandeja priorizada

1. Doble clic en **`AsistenteCorreo.bat`** → **2) Mi bandeja real**.
2. Verás tu lista: primero los 🔴, luego 🟡, luego 🟢, cada uno con puntaje, palabras detectadas y motivo.
3. Se abre **`informe.html`** en el navegador: tarjetas de colores con buscador y filtros (Todos / Rojo / Amarillo / Verde). Usa el botón **🖨 Imprimir / Guardar PDF** para imprimir o guardar en PDF.

O desde PowerShell:
```powershell
.\.venv\Scripts\python.exe -m asistente_correo.cli --inbox --limit 20 --html informe.html --abrir
```

## 5. Usar el chatbot decisor

1. Menú → **3) Chatbot**.
2. Pregunta en español, por ejemplo: `¿qué atiendo primero?`, `/resumen`, `/busca factura`.
3. Escribe `/salir` para terminar.

O de una vez:
```powershell
.\.venv\Scripts\python.exe -m asistente_correo.cli --inbox --pregunta "qué atiendo primero"
```

## 6. ¿Qué significa cada color? (ejemplos)

- 🔴 **Rojo** — "URGENTE: sistema caído", "Factura vencida", "Sin acceso desde hoy". Atender hoy.
- 🟡 **Amarillo** — "Reunión mañana", "Entrega del reporte esta semana", "Cotización solicitada". Atender esta semana.
- 🟢 **Verde** — "Newsletter semanal", "Gracias por tu registro". Revisar cuando aplique (sigue siendo importante).

## 7. Preguntas frecuentes

- **¿Va a borrar o responder mis correos?** No. Solo lee.
- **¿Por qué sale "Sin token válido"?** Falta la autenticación. Repite el menú opción 4.
- **¿Por qué no abre el navegador?** Abre `informe.html` a mano desde la carpeta del proyecto.
- **¿Dónde queda el informe?** En `informe.html` junto al programa.
- **¿Necesito internet?** Sí, para leer Gmail la primera vez y en cada uso real. La demo no.

## 8. ¿Cómo quito el acceso? (opcional)

En tu cuenta de Google → Seguridad → Acceso de terceros → elimina "Asistente-Correo". El archivo `token.json` local deja de funcionar.
