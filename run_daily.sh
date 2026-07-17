#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

mkdir -p logs

echo "===== $(date -Is) - inicio rutina diaria eclipse =====" >> logs/daily.log

source .venv/bin/activate

# Captura diaria. captura_eclipse.py ya controla internamente la ventana
# 19:30-21:00 (espera a que empiece, termina sola a las 21:00), por eso no
# se envuelve con timeout aqui.
python3 captura_eclipse.py >> logs/daily.log 2>&1

# Evaluacion/ranking acumulado.
python3 evaluar_eclipse.py >> logs/daily.log 2>&1

echo "===== $(date -Is) - fin rutina diaria eclipse =====" >> logs/daily.log
