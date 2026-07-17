#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -d .venv ]; then
    python3 -m venv --system-site-packages .venv
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

# GTK/WebKit (backend por defecto de pywebview en Linux) no decodifica estos
# streams HLS: el video queda en negro. Qt+QtWebEngine si funciona (motor
# Chromium, igual que WebView2 en Windows).
export PYWEBVIEW_GUI=qt
if ! python3 -c "import qtpy" 2>/dev/null; then
    pip install --quiet qtpy
fi
if ! python3 -c "from PyQt6 import QtWebEngineWidgets" 2>/dev/null; then
    echo
    echo "Falta PyQt6 + QtWebEngine (paquetes de sistema, no instalables por pip)."
    echo "Instala con: sudo pacman -S python-pyqt6 python-pyqt6-webengine"
    echo "Sin esto la app usara GTK/WebKit y las camaras se veran en negro."
fi

python3 main.py
status=$?
if [ "$status" -ne 0 ]; then
    echo
    echo "La aplicacion termino con un error."
fi
exit "$status"
