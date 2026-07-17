@echo off
setlocal
cd /d "%~dp0"

python -c "import cv2, PIL" 2>nul
if errorlevel 1 (
    echo Instalando dependencias de captura...
    python -m pip install opencv-python Pillow requests
)

python captura_eclipse.py %*
