"""Resolucion de URLs de stream HLS (.m3u8) a partir de las paginas embed
de rtsp.me y Angelcam. Modulo compartido por la app (main.py) y la rutina
de captura del eclipse (captura_eclipse.py)."""

import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STREAM_URL_MAX_AGE = 40 * 60  # refrescar el token pasados 40 minutos

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
# URL .m3u8 dentro del HTML del reproductor (rtsp.me la incluye en claro;
# Angelcam la incluye con escapes \\uXXXX y %XX que hay que deshacer; CRTVG/
# G24 la incluye dentro de un literal JS con las barras escapadas \/).
M3U8_RE = re.compile(r"https:\\?/\\?/[^\s\"'<>]+?\.m3u8[^\s\"'<>]*")


def _http_get(url):
    try:
        return requests.get(url, headers=HEADERS, timeout=15).text
    except (requests.exceptions.SSLError, OSError):
        # Algunos entornos corporativos rompen la verificacion TLS; para
        # extraer una URL publica de streaming es asumible ir sin verificar.
        return requests.get(url, headers=HEADERS, timeout=15, verify=False).text


def _extract_m3u8(html):
    match = M3U8_RE.search(html)
    if not match:
        return None
    url = match.group(0)
    if "\\u" in url:
        url = url.encode("ascii", "ignore").decode("unicode_escape")
    if "%" in url:
        url = requests.utils.unquote(url)
    if "\\/" in url:
        url = url.replace("\\/", "/")
    return url


class StreamResolver:
    """Extrae y cachea las URLs .m3u8 tokenizadas de las paginas embed."""

    def __init__(self, cameras):
        self.cameras = cameras
        self.cache = {}  # indice -> (url, timestamp)
        self.lock = threading.Lock()

    def resolve(self, index, force=False):
        index = int(index)
        with self.lock:
            hit = self.cache.get(index)
        if hit and not force and time.time() - hit[1] < STREAM_URL_MAX_AGE:
            return hit[0]
        try:
            url = _extract_m3u8(_http_get(self.cameras[index]["embed_url"]))
        except Exception:
            url = None
        if not url:
            return hit[0] if hit else None
        with self.lock:
            self.cache[index] = (url, time.time())
        return url

    def prefetch_all(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            pool.map(self.resolve, range(len(self.cameras)))


def fetch_weather(cameras):
    """Meteo actual de Open-Meteo para todas las camaras en una peticion.

    Devuelve una lista paralela a `cameras` de dicts con temp (grados C),
    cloud (% nubosidad) y vis (visibilidad en metros)."""
    import json as _json
    lats = ",".join(f"{c['lat']:.4f}" for c in cameras)
    lons = ",".join(f"{c['lon']:.4f}" for c in cameras)
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lats}&longitude={lons}"
           "&current=temperature_2m,cloud_cover,visibility")
    results = _json.loads(_http_get(url))
    if isinstance(results, dict):
        results = [results]
    return [
        {
            "temp": item.get("current", {}).get("temperature_2m"),
            "cloud": item.get("current", {}).get("cloud_cover"),
            "vis": item.get("current", {}).get("visibility"),
        }
        for item in results
    ]
