@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Asistente-Correo - doble clic recomendado (opcion 2: bandeja real, 3: chatbot)
".venv\Scripts\python.exe" menu.py
pause
