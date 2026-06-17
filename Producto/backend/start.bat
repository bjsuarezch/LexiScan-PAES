@echo off
REM Script de arranque del backend LexiScan - Compatible con cualquier locale de Windows
REM Fuerza UTF-8 en la consola y en Python antes de lanzar uvicorn

REM Cambia el codepage de la consola a UTF-8 (65001)
chcp 65001 > nul

REM Setea variables de entorno para que Python use UTF-8 siempre
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Activa el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [LexiScan] Iniciando backend con encoding UTF-8...
uvicorn main:app --reload --host 0.0.0.0 --port 8000
