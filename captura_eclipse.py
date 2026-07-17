"""Captura diaria de todas las webcams durante la ventana del eclipse.

El 12-08-2026 la franja de totalidad del eclipse solar cruza Asturias
(totalidad hacia las 20:26 CEST, con fases parciales aprox. 19:30-21:20).
Esta rutina, independiente de la app, guarda cada dia un frame de cada
camara cada FRAME_INTERVAL segundos durante la ventana del eclipse, junto
con instantaneas meteorologicas, para evaluar despues con que probabilidad
se habria visto el eclipse desde cada ubicacion.

Estructura de salida:
    capturas/AAAA-MM-DD/meteo.json            instantaneas meteo (cada 10 min)
    capturas/AAAA-MM-DD/<nn-camara>/HHMMSS.jpg  frames

Uso:
    python captura_eclipse.py                 espera a la ventana de hoy y captura
    python captura_eclipse.py --ahora N       captura N rondas ya mismo (pruebas)
    python captura_eclipse.py --intervalo S   cambia el intervalo entre rondas

Programacion diaria (Programador de tareas de Windows, ejecutar una vez):
    schtasks /create /tn "CapturaEclipse" /tr "C:\\_Dev\\Python\\Projects\\webcams-tap\\capturar.bat" /sc daily /st 19:25
"""

import argparse
import datetime
import json
import os
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Evitar que rutas CA corporativas rotas y el ruido de ffmpeg molesten.
os.environ.pop("SSL_CERT_FILE", None)
os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.setdefault("OPENCV_FFMPEG_LOGLEVEL", "-8")

import cv2  # noqa: E402
import requests  # noqa: E402
import urllib.parse  # noqa: E402

from cameras import CAMERAS  # noqa: E402
from streams import HEADERS, M3U8_RE, _extract_m3u8, fetch_weather  # noqa: E402

# ---- Configuracion ----
WINDOW_START = "19:30"   # hora local de inicio de la ventana de captura
WINDOW_END = "21:00"     # hora local de fin
FRAME_INTERVAL = 60      # segundos entre rondas de captura
METEO_INTERVAL = 600     # segundos entre instantaneas meteorologicas
WORKERS = 8              # capturas simultaneas
JPEG_MAX_WIDTH = 1280    # se reescala si el frame es mas ancho
JPEG_QUALITY = 82
OUT_DIR = Path(__file__).parent / "capturas"


def slug(index, cam):
    text = f"{cam['town']} {cam['title']}"
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return f"{index:02d}-{text[:50]}"


import re as _re  # noqa: E402

SESSION_JS_RE = _re.compile(
    r"src=.(https://[a-z0-9]+\.rtsp\.me/[A-Za-z0-9_-]+/\d+/hls/[A-Za-z0-9]+\.js\?time=\d+)")
PLACEHOLDER_RE = _re.compile(r"-40\d\.ts$")

# Cache por camara: (url, epoch del ultimo exito). Mientras el stream siga
# "despierto" (capturas recientes) se reutiliza la URL sin re-despertar.
_awake = {}
_awake_lock = __import__("threading").Lock()
AWAKE_TTL = 150  # seg sin exito tras los cuales se vuelve a despertar


def _playlist_is_real(text):
    segs = [l for l in text.splitlines() if l and not l.startswith("#")]
    if not segs:
        return False
    return not all(PLACEHOLDER_RE.search(s) for s in segs)


def wake_stream(index, timeout=45):
    """Despierta un stream rtsp.me dormido imitando a su reproductor:
    pagina embed (cookies de sesion), .js de sesion, sondeo de la playlist
    cada segundo tocando los segmentos placeholder. Devuelve la URL .m3u8
    activa, o None si no despierta en `timeout` segundos."""
    cam = CAMERAS[index]
    s = requests.Session()
    s.headers.update(HEADERS)
    s.verify = False
    try:
        emb = s.get(cam["embed_url"], timeout=15).text
        url = _extract_m3u8(emb)
        if not url:
            return None
        jsm = SESSION_JS_RE.search(emb)
        if jsm:
            s.get(jsm.group(1), timeout=10)
        base = url.rsplit("/", 1)[0] + "/"
        t0 = time.time()
        while time.time() - t0 < timeout:
            pl = s.get(url, timeout=10).text
            if _playlist_is_real(pl):
                return url
            segs = [l for l in pl.splitlines() if l and not l.startswith("#")]
            if segs:
                try:
                    s.get(urllib.parse.urljoin(base, segs[-1]), timeout=5)
                except Exception:
                    pass
            time.sleep(1)
    except Exception:
        pass
    finally:
        s.close()
    return None


def grab_frame(index, day_dir, stamp):
    """Captura un frame de la camara `index` y lo guarda como JPEG."""
    with _awake_lock:
        hit = _awake.get(index)
    url = hit[0] if hit and time.time() - hit[1] < AWAKE_TTL else None
    if not url:
        url = wake_stream(index)
    if not url:
        return False

    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    ok, frame = cap.read()
    cap.release()
    if not ok and hit:  # la URL cacheada pudo caducar: re-despertar
        url = wake_stream(index)
        if url:
            cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            ok, frame = cap.read()
            cap.release()
    if not (ok and frame is not None and frame.size):
        return False

    h, w = frame.shape[:2]
    if w > JPEG_MAX_WIDTH:
        frame = cv2.resize(frame, (JPEG_MAX_WIDTH, int(h * JPEG_MAX_WIDTH / w)))
    cam_dir = day_dir / slug(index, CAMERAS[index])
    cam_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(cam_dir / f"{stamp}.jpg"), frame,
                [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    with _awake_lock:
        _awake[index] = (url, time.time())
    return True


def capture_round(day_dir):
    stamp = datetime.datetime.now().strftime("%H%M%S")
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(
            lambda i: grab_frame(i, day_dir, stamp),
            range(len(CAMERAS))))
    ok = sum(results)
    print(f"  [{stamp}] ronda completada: {ok}/{len(CAMERAS)} camaras", flush=True)
    return ok


def save_weather(day_dir, snapshots):
    try:
        snapshots.append({
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "data": fetch_weather(CAMERAS),
        })
        (day_dir / "meteo.json").write_text(
            json.dumps(snapshots, ensure_ascii=False), encoding="utf-8")
        print(f"  meteo guardada ({len(snapshots)} instantaneas)", flush=True)
    except Exception as e:
        print(f"  aviso: fallo al obtener meteo: {e}", flush=True)


def parse_hhmm(text):
    h, m = text.split(":")
    return datetime.time(int(h), int(m))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ahora", type=int, metavar="N", default=0,
                        help="capturar N rondas inmediatamente (pruebas)")
    parser.add_argument("--intervalo", type=int, default=FRAME_INTERVAL,
                        help="segundos entre rondas")
    args = parser.parse_args()

    today = datetime.date.today()
    day_dir = OUT_DIR / today.isoformat()
    day_dir.mkdir(parents=True, exist_ok=True)
    snapshots = []
    if (day_dir / "meteo.json").exists():
        snapshots = json.loads((day_dir / "meteo.json").read_text(encoding="utf-8"))

    if args.ahora:
        print(f"Modo prueba: {args.ahora} rondas cada {args.intervalo}s")
        last_meteo = 0
        for n in range(args.ahora):
            t0 = time.time()
            if time.time() - last_meteo >= METEO_INTERVAL or n == 0:
                save_weather(day_dir, snapshots)
                last_meteo = time.time()
            capture_round(day_dir)
            if n < args.ahora - 1:
                time.sleep(max(0, args.intervalo - (time.time() - t0)))
        return

    start = datetime.datetime.combine(today, parse_hhmm(WINDOW_START))
    end = datetime.datetime.combine(today, parse_hhmm(WINDOW_END))
    now = datetime.datetime.now()

    if now >= end:
        print(f"La ventana de hoy ({WINDOW_START}-{WINDOW_END}) ya paso. Nada que hacer.")
        return
    if now < start:
        wait = (start - now).total_seconds()
        print(f"Esperando hasta las {WINDOW_START} ({wait/60:.0f} min)...", flush=True)
        time.sleep(wait)

    print(f"Captura de {today}: cada {args.intervalo}s hasta las {WINDOW_END}", flush=True)
    last_meteo = 0
    while datetime.datetime.now() < end:
        t0 = time.time()
        if time.time() - last_meteo >= METEO_INTERVAL:
            save_weather(day_dir, snapshots)
            last_meteo = time.time()
        capture_round(day_dir)
        time.sleep(max(0, args.intervalo - (time.time() - t0)))
    print("Ventana terminada. Captura del dia completa.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.")
        sys.exit(1)
