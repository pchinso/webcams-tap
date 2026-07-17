#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

if ! python3 -c "import webview" 2>/dev/null; then
    echo "Instalando dependencias..."
    if ! pip install -r requirements.txt; then
        echo
        echo "No se pudieron instalar las dependencias. Revisa que Python 3 este instalado."
        exit 1
    fi
fi

python3 main.py
status=$?
if [ "$status" -ne 0 ]; then
    echo
    echo "La aplicacion termino con un error."
fi
exit "$status"
