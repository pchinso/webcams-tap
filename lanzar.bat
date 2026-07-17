@echo off
setlocal
cd /d "%~dp0"

python -c "import webview" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo No se pudieron instalar las dependencias. Revisa que Python este instalado y en el PATH.
        pause
        exit /b 1
    )
)

python main.py
if errorlevel 1 (
    echo.
    echo La aplicacion termino con un error.
    pause
)
