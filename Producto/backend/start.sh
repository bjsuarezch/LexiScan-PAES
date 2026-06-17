#!/bin/bash
# Script de arranque del backend LexiScan - Compatible con Linux/macOS
# Fuerza UTF-8 en Python antes de lanzar uvicorn

export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Activa el entorno virtual si existe
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo "[LexiScan] Iniciando backend con encoding UTF-8..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
