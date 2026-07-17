"""Visor de webcams publicas de Asturias.

Reproduce los streams HLS directamente con hls.js sobre elementos <video>
propios (muted + autoplay), sin el reproductor embebido de rtsp.me, de modo
que el video esta SIEMPRE en reproduccion sin requerir clic del usuario.

- Al arrancar precarga un buffer de varias camaras en paralelo (videos
  ocultos reproduciendo en segundo plano) y tras una breve espera muestra
  la primera. Cambiar de camara solo alterna visibilidad: instantaneo.
- La URL del stream lleva un token que caduca (~1 h): Python la extrae de
  la pagina embed de rtsp.me y la refresca cuando el reproductor falla.

Salud de camaras: un hilo Python comprueba periodicamente que la playlist
de cada camara responde, y el frontend detecta imagen negra muestreando la
luminancia del fotograma. Las camaras muertas o en negro se SALTAN al
navegar (no se borran de la lista) y se reintentan pasado un tiempo.

Controles:
- Cualquier tecla avanza a la siguiente camara; la tecla "b" retrocede.
- Clic izquierdo del raton avanza; clic derecho retrocede.
- La tecla "l" activa/desactiva el modo loop (siguiente cada 10 s).
- En modo loop el video mostrado se captura continuamente; la tecla "r"
  guarda lo grabado como .webm en la carpeta "grabaciones" (y la captura
  se reinicia si el loop sigue activo). Salir del loop descarta lo no
  guardado.
"""

import base64
import datetime
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
import webview

from cameras import CAMERAS
from mapthumb import build_map_svg
from streams import HEADERS, StreamResolver, _http_get

# Camaras mantenidas conectadas ademas de la actual.
BUFFER_AHEAD = 3   # precargadas por delante (sentido "siguiente")
BUFFER_BEHIND = 2  # precargadas por detras (sentido "anterior")
WARMUP_MS = 5000   # espera inicial para alimentar el buffer

WEATHER_MAX_AGE = 10 * 60     # refrescar la meteorologia cada 10 minutos
HEALTH_INTERVAL = 5 * 60      # comprobar la salud de los streams cada 5 min
LOOP_SECONDS = 10             # intervalo del modo loop (tecla "l")


class HealthChecker:
    """Comprueba en segundo plano que la playlist de cada camara responde.

    No borra fuentes: solo mantiene una lista de estados (True viva,
    False muerta, None sin comprobar aun) que el frontend usa para saltar
    camaras caidas al navegar. Cada ronda vuelve a probar TODAS, asi que
    una camara caida se recupera sola cuando vuelve a emitir.
    """

    def __init__(self, resolver):
        self.resolver = resolver
        self.status = [None] * len(resolver.cameras)
        self.lock = threading.Lock()

    def _check_one(self, index):
        try:
            url = self.resolver.resolve(index)
            if not url:
                return False
            r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            return r.status_code == 200 and "#EXTINF" in r.text
        except Exception:
            return False

    def _run(self):
        while True:
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(self._check_one, range(len(self.status))))
            with self.lock:
                self.status = results
            time.sleep(HEALTH_INTERVAL)

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def get_all(self):
        with self.lock:
            return list(self.status)


class WeatherService:
    """Meteorologia actual (Open-Meteo) para todas las camaras en una sola
    peticion por lotes, cacheada WEATHER_MAX_AGE segundos."""

    def __init__(self, cameras):
        self.cameras = cameras
        self.data = []       # lista paralela a cameras: dict o None
        self.fetched_at = 0
        self.lock = threading.Lock()

    def _fetch_all(self):
        lats = ",".join(f"{c['lat']:.4f}" for c in self.cameras)
        lons = ",".join(f"{c['lon']:.4f}" for c in self.cameras)
        url = ("https://api.open-meteo.com/v1/forecast"
               f"?latitude={lats}&longitude={lons}"
               "&current=temperature_2m,cloud_cover,visibility")
        results = json.loads(_http_get(url))
        if isinstance(results, dict):
            results = [results]
        data = []
        for item in results:
            cur = item.get("current", {})
            data.append({
                "temp": cur.get("temperature_2m"),
                "cloud": cur.get("cloud_cover"),
                "vis": cur.get("visibility"),
            })
        return data

    def get(self, index):
        index = int(index)
        with self.lock:
            if time.time() - self.fetched_at > WEATHER_MAX_AGE:
                try:
                    self.data = self._fetch_all()
                    self.fetched_at = time.time()
                except Exception:
                    pass  # se conserva (o queda vacia) la cache anterior
            if 0 <= index < len(self.data):
                return self.data[index]
        return None


RECORDINGS_DIR = Path(__file__).parent / "grabaciones"


class Api:
    """Puente JS -> Python: streams, meteo, salud y guardado de capturas.

    La grabacion llega desde JS en trozos base64 (rec_begin / rec_chunk /
    rec_end) para no pasar cientos de MB en una sola llamada.
    """

    def __init__(self, resolver, weather, health):
        self._resolver = resolver
        self._weather = weather
        self._health = health
        self._rec_file = None
        self._rec_path = None
        self._rec_lock = threading.Lock()

    def get_stream(self, index, force=False):
        return self._resolver.resolve(index, force)

    def get_weather(self, index):
        return self._weather.get(index)

    def get_health(self):
        return self._health.get_all()

    def rec_begin(self):
        with self._rec_lock:
            if self._rec_file:
                self._rec_file.close()
            RECORDINGS_DIR.mkdir(exist_ok=True)
            stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self._rec_path = RECORDINGS_DIR / f"loop-{stamp}.webm"
            self._rec_file = open(self._rec_path, "wb")
        return True

    def rec_chunk(self, b64):
        with self._rec_lock:
            if not self._rec_file:
                return False
            self._rec_file.write(base64.b64decode(b64))
        return True

    def rec_end(self):
        with self._rec_lock:
            if not self._rec_file:
                return None
            self._rec_file.close()
            self._rec_file = None
            return str(self._rec_path)


PAGE_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {
    margin: 0; padding: 0; height: 100%; width: 100%;
    background: #000; overflow: hidden;
  }
  .camframe {
    position: fixed; inset: 0; width: 100%; height: 100%;
    object-fit: contain; background: #000;
    visibility: hidden; pointer-events: none;
  }
  .camframe.active { visibility: visible; }
  #overlay {
    position: fixed; inset: 0; z-index: 10; cursor: pointer;
  }
  #caption {
    position: fixed; left: 14px; bottom: 14px; z-index: 20;
    color: #fff; background: rgba(15, 20, 25, 0.72);
    padding: 8px 14px; border-radius: 8px;
    font-family: "Segoe UI", Arial, sans-serif;
    border: 1px solid rgba(255, 255, 255, 0.35);
    pointer-events: none;
  }
  #caption b { font-size: 16px; }
  #caption span { display: block; font-size: 12px; opacity: 0.8; margin-top: 2px; }
  #caption em { font-style: normal; color: #9fd0ff; }
  #loopbadge {
    display: none;
    position: fixed; right: 14px; top: 14px; z-index: 20;
    color: #fff; background: rgba(15, 20, 25, 0.72);
    padding: 6px 12px; border-radius: 8px;
    font-family: "Segoe UI", Arial, sans-serif; font-size: 13px;
    border: 1px solid rgba(255, 255, 255, 0.35);
    pointer-events: none;
  }
  #recbadge {
    display: none;
    position: fixed; right: 14px; top: 54px; z-index: 20;
    color: #ff6b60; background: rgba(30, 10, 10, 0.75);
    padding: 6px 12px; border-radius: 8px;
    font-family: "Segoe UI", Arial, sans-serif; font-size: 13px;
    border: 1px solid rgba(255, 90, 80, 0.55);
    pointer-events: none;
  }
  #toast {
    display: none;
    position: fixed; left: 50%; bottom: 64px; transform: translateX(-50%);
    z-index: 40; max-width: 80%;
    color: #fff; background: rgba(15, 20, 25, 0.88);
    padding: 10px 16px; border-radius: 8px;
    font-family: "Segoe UI", Arial, sans-serif; font-size: 14px;
    border: 1px solid rgba(255, 255, 255, 0.35);
    pointer-events: none;
  }
  #mapbox {
    position: fixed; right: 14px; bottom: 14px; z-index: 20;
    background: rgba(15, 20, 25, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 8px; padding: 6px; line-height: 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    pointer-events: none;
  }
  #splash {
    position: fixed; inset: 0; z-index: 30;
    background: #000; color: #fff;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-family: "Segoe UI", Arial, sans-serif;
    transition: opacity 0.6s;
  }
  #splash.hidden { opacity: 0; pointer-events: none; }
  #splash h1 { font-size: 22px; font-weight: 600; margin: 0 0 18px 0; }
  #bar {
    width: 320px; height: 6px; border-radius: 3px;
    background: rgba(255, 255, 255, 0.15); overflow: hidden;
  }
  #bar div {
    width: 0%; height: 100%; background: #4da3ff; border-radius: 3px;
  }
</style>
<script>__HLS_JS__</script>
</head>
<body>
  <div id="frames"></div>
  <div id="overlay"></div>
  <div id="caption"><b></b><span></span></div>
  <div id="loopbadge">&#10227; loop __LOOP_S__ s &middot; pulsa L para salir</div>
  <div id="recbadge"></div>
  <div id="toast"></div>
  <div id="mapbox"></div>
  <div id="splash">
    <h1>Precargando c&aacute;maras&hellip;</h1>
    <div id="bar"><div></div></div>
  </div>
<script>
  var CAMERAS = __CAMERAS__;
  var BUFFER_AHEAD = __BUFFER_AHEAD__;
  var BUFFER_BEHIND = __BUFFER_BEHIND__;
  var WARMUP_MS = __WARMUP_MS__;
  var LOOP_MS = __LOOP_MS__;
  var TEST_URLS = __TEST_URLS__;

  var total = CAMERAS.length;
  var current = 0;
  var players = {};          // indice -> {video, hls, black, retries}
  var framesRoot = document.getElementById('frames');
  var poolTimer = null;

  // Salud de camaras. pyHealth: lista de Python (playlist responde o no).
  // jsHealth: observaciones locales (imagen negra, errores fatales), con
  // caducidad para volver a intentar camaras marcadas como malas.
  var pyHealth = null;
  var jsHealth = {};         // indice -> {s: 'ok'|'bad', ts: epoch_ms}
  var HEALTH_TTL_MS = 10 * 60 * 1000;

  function setHealth(i, state) {
    jsHealth[i] = { s: state, ts: Date.now() };
  }

  function isUsable(i) {
    var h = jsHealth[i];
    if (h && Date.now() - h.ts < HEALTH_TTL_MS) {
      return h.s === 'ok';
    }
    if (pyHealth && pyHealth[i] === false) { return false; }
    return true;  // sin datos: se le da una oportunidad
  }

  function mod(n) { return ((n % total) + total) % total; }

  // Siguiente/anterior camara utilizable; si todas parecen malas,
  // devuelve la inmediata para no quedarse nunca bloqueado.
  function step(dir) {
    for (var k = 1; k <= total; k++) {
      var cand = mod(current + dir * k);
      if (isUsable(cand)) { return cand; }
    }
    return mod(current + dir);
  }

  function getStream(i, force) {
    if (TEST_URLS) { return Promise.resolve(TEST_URLS[i] || null); }
    return window.pywebview.api.get_stream(i, !!force);
  }

  function getWeather(i) {
    if (TEST_URLS) { return Promise.resolve({temp: 19.5, cloud: 40, vis: 12300}); }
    return window.pywebview.api.get_weather(i);
  }

  function formatWeather(w) {
    var parts = [];
    if (w.temp !== null && w.temp !== undefined) {
      parts.push(w.temp.toFixed(1).replace('.', ',') + ' \\u00b0C');
    }
    if (w.cloud !== null && w.cloud !== undefined) {
      parts.push('nubes ' + Math.round(w.cloud) + '%');
    }
    if (w.vis !== null && w.vis !== undefined) {
      var km = w.vis / 1000;
      parts.push('visib. ' + (km >= 10 ? Math.round(km) : km.toFixed(1).replace('.', ',')) + ' km');
    }
    return parts.join(' \\u00b7 ');
  }

  function updateWeather(i) {
    getWeather(i).then(function (w) {
      if (i !== current || !w) { return; }
      var text = formatWeather(w);
      if (text) {
        document.getElementById('weather').textContent = '\\u00b7 ' + text;
      }
    }).catch(function () {});
  }

  function attachStream(i, url) {
    var p = players[i];
    if (!p || !url) { return; }
    if (p.hls) { p.hls.destroy(); }
    var hls = new Hls({
      liveDurationInfinity: true,
      manifestLoadingMaxRetry: 3,
      levelLoadingMaxRetry: 3,
      fragLoadingMaxRetry: 3
    });
    p.hls = hls;
    hls.attachMedia(p.video);
    hls.loadSource(url);
    hls.on(Hls.Events.MANIFEST_PARSED, function () {
      p.video.play().catch(function () {});
    });
    hls.on(Hls.Events.ERROR, function (event, data) {
      if (!data.fatal) { return; }
      if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
        hls.recoverMediaError();
        return;
      }
      // Error de red fatal: normalmente token caducado. Pedimos a Python
      // una URL fresca y recargamos. Tras varios intentos fallidos se
      // marca la camara como mala (se reintentara al caducar la marca).
      p.retries = (p.retries || 0) + 1;
      if (p.retries > 2) {
        setHealth(i, 'bad');
        return;
      }
      getStream(i, true).then(function (fresh) {
        if (players[i] && players[i].hls === hls) {
          attachStream(i, fresh);
        }
      });
    });
    hls.on(Hls.Events.FRAG_BUFFERED, function () {
      p.retries = 0;
    });
  }

  function createFrame(i) {
    if (players[i]) { return; }
    var v = document.createElement('video');
    v.className = 'camframe';
    v.muted = true;
    v.autoplay = true;
    v.playsInline = true;
    framesRoot.appendChild(v);
    players[i] = { video: v, hls: null };
    getStream(i, false).then(function (url) {
      if (!players[i]) { return; }
      if (!url) { setHealth(i, 'bad'); return; }
      attachStream(i, url);
    });
  }

  function destroyFrame(i) {
    var p = players[i];
    if (!p) { return; }
    if (p.hls) { p.hls.destroy(); }
    framesRoot.removeChild(p.video);
    delete players[i];
  }

  function poolIndices() {
    var wanted = [current];
    for (var a = 1; a <= BUFFER_AHEAD; a++) { wanted.push(mod(current + a)); }
    for (var b = 1; b <= BUFFER_BEHIND; b++) { wanted.push(mod(current - b)); }
    return wanted;
  }

  // Recoloca el pool alrededor de la camara actual: conecta las que faltan
  // y desconecta las que quedan lejos. Se hace con retardo para no crear y
  // destruir conexiones mientras el usuario pasa camaras rapido.
  function schedulePoolUpdate() {
    if (poolTimer) { clearTimeout(poolTimer); }
    poolTimer = setTimeout(function () {
      var wanted = poolIndices();
      wanted.forEach(createFrame);
      Object.keys(players).forEach(function (key) {
        var i = parseInt(key, 10);
        if (wanted.indexOf(i) === -1) { destroyFrame(i); }
      });
    }, 600);
  }

  function show(i) {
    current = mod(i);
    createFrame(current);  // por si el usuario va mas rapido que el buffer
    Object.keys(players).forEach(function (key) {
      var idx = parseInt(key, 10);
      players[key].video.classList.toggle('active', idx === current);
    });
    var p = players[current];
    if (p && p.video.paused) { p.video.play().catch(function () {}); }
    var cam = CAMERAS[current];
    document.querySelector('#caption b').textContent = cam.title;
    document.querySelector('#caption span').innerHTML =
      cam.town + ' \\u00b7 c\\u00e1mara ' + (current + 1) + '/' + total +
      ' <em id="weather"></em>';
    document.getElementById('mapbox').innerHTML = cam.map;
    updateWeather(current);
    schedulePoolUpdate();
  }

  function next() { show(step(1)); }
  function prev() { show(step(-1)); }

  // ---- Avisos en pantalla ----
  function toast(msg) {
    var t = document.getElementById('toast');
    t.textContent = msg;
    t.style.display = 'block';
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { t.style.display = 'none'; }, 4000);
  }

  // ---- Captura del stream en modo loop (tecla "r" guarda) ----
  // El video activo se dibuja en un canvas y se graba con MediaRecorder.
  var recorder = null, recChunks = [], recStartTs = 0;
  var recDraw = null, recTimer = null, recCanvas = null, recCtx = null;

  function startCapture() {
    if (recorder) { return; }
    if (!recCanvas) {
      recCanvas = document.createElement('canvas');
      recCanvas.width = 1280; recCanvas.height = 720;
      recCtx = recCanvas.getContext('2d');
    }
    recDraw = setInterval(function () {
      recCtx.fillStyle = '#000';
      recCtx.fillRect(0, 0, recCanvas.width, recCanvas.height);
      var p = players[current];
      if (p && p.video.readyState >= 2 && p.video.videoWidth) {
        var vw = p.video.videoWidth, vh = p.video.videoHeight;
        var s = Math.min(recCanvas.width / vw, recCanvas.height / vh);
        var w = vw * s, h = vh * s;
        recCtx.drawImage(p.video, (recCanvas.width - w) / 2, (recCanvas.height - h) / 2, w, h);
      }
    }, 40);
    var mime = MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
      ? 'video/webm;codecs=vp9' : 'video/webm';
    recorder = new MediaRecorder(recCanvas.captureStream(25),
                                 { mimeType: mime, videoBitsPerSecond: 2500000 });
    recChunks = [];
    recorder.ondataavailable = function (e) {
      if (e.data && e.data.size) { recChunks.push(e.data); }
    };
    recorder.start(1000);
    recStartTs = Date.now();
    var badge = document.getElementById('recbadge');
    badge.style.display = 'block';
    badge.textContent = '\\u25cf REC 0:00 \\u00b7 R guarda';
    recTimer = setInterval(function () {
      var s = Math.floor((Date.now() - recStartTs) / 1000);
      badge.textContent = '\\u25cf REC ' + Math.floor(s / 60) + ':' +
        ('0' + s % 60).slice(-2) + ' \\u00b7 R guarda';
    }, 1000);
  }

  function stopCapture() {
    if (!recorder) { return; }
    try { recorder.onstop = null; recorder.stop(); } catch (e) {}
    clearInterval(recDraw);
    clearInterval(recTimer);
    recorder = null;
    recChunks = [];
    document.getElementById('recbadge').style.display = 'none';
  }

  function uploadBlob(blob) {
    if (TEST_URLS) {
      toast('TEST: capturados ' + Math.round(blob.size / 1024) + ' kB');
      return;
    }
    toast('Guardando grabaci\\u00f3n\\u2026');
    window.pywebview.api.rec_begin().then(function () {
      var CHUNK = 3 * 1024 * 1024;
      var off = 0;
      function sendNext() {
        if (off >= blob.size) {
          return window.pywebview.api.rec_end().then(function (path) {
            toast('Grabaci\\u00f3n guardada: ' + path);
          });
        }
        var slice = blob.slice(off, off + CHUNK);
        off += CHUNK;
        return new Promise(function (resolve, reject) {
          var fr = new FileReader();
          fr.onload = function () {
            window.pywebview.api.rec_chunk(fr.result.split(',')[1]).then(resolve, reject);
          };
          fr.onerror = reject;
          fr.readAsDataURL(slice);
        }).then(sendNext);
      }
      return sendNext();
    }).catch(function () { toast('Error al guardar la grabaci\\u00f3n'); });
  }

  function saveRecording() {
    if (!recorder) {
      toast('No hay captura activa: el loop (tecla L) graba autom\\u00e1ticamente');
      return;
    }
    var rec = recorder;
    rec.onstop = function () {
      var blob = new Blob(recChunks, { type: 'video/webm' });
      recChunks = [];
      recorder = null;
      clearInterval(recDraw);
      clearInterval(recTimer);
      document.getElementById('recbadge').style.display = 'none';
      if (loopTimer) { startCapture(); }
      if (blob.size < 50000) { toast('Grabaci\\u00f3n demasiado corta'); return; }
      uploadBlob(blob);
    };
    rec.stop();
  }

  // ---- Modo loop: avance automatico (tecla "l") ----
  var loopTimer = null;

  function toggleLoop() {
    if (loopTimer) {
      clearInterval(loopTimer);
      loopTimer = null;
      document.getElementById('loopbadge').style.display = 'none';
      if (recorder && Date.now() - recStartTs > 3000) {
        toast('Grabaci\\u00f3n descartada (pulsa R antes de salir del loop para guardarla)');
      }
      stopCapture();
    } else {
      loopTimer = setInterval(next, LOOP_MS);
      document.getElementById('loopbadge').style.display = 'block';
      startCapture();
      next();
    }
  }

  var overlay = document.getElementById('overlay');

  overlay.addEventListener('click', function () { next(); });

  overlay.addEventListener('contextmenu', function (e) {
    e.preventDefault();
    prev();
  });

  var IGNORED_KEYS = ['Shift', 'Control', 'Alt', 'Meta', 'CapsLock', 'Tab'];

  window.addEventListener('keydown', function (e) {
    if (e.repeat || IGNORED_KEYS.indexOf(e.key) !== -1) { return; }
    if (e.key === 'l' || e.key === 'L') { toggleLoop(); }
    else if (e.key === 'r' || e.key === 'R') { saveRecording(); }
    else if (e.key === 'b' || e.key === 'B') { prev(); }
    else { next(); }
  });

  // ---- Deteccion de imagen en negro ----
  // Los videos llegan por MSE, asi que se puede muestrear el fotograma en
  // un canvas y medir la luminancia media. Dos muestras seguidas casi a
  // cero marcan la camara como negra; cualquier muestra con imagen la
  // marca como buena. El umbral es bajo para no confundir con la noche.
  var probe = document.createElement('canvas');
  probe.width = 32; probe.height = 18;
  var probeCtx = probe.getContext('2d', { willReadFrequently: true });

  function sampleLuma(video) {
    try {
      probeCtx.drawImage(video, 0, 0, probe.width, probe.height);
      var d = probeCtx.getImageData(0, 0, probe.width, probe.height).data;
      var sum = 0;
      for (var j = 0; j < d.length; j += 4) {
        sum += 0.299 * d[j] + 0.587 * d[j + 1] + 0.114 * d[j + 2];
      }
      return sum / (d.length / 4);
    } catch (e) {
      return null;
    }
  }

  setInterval(function () {
    Object.keys(players).forEach(function (key) {
      var i = parseInt(key, 10);
      var p = players[key];
      if (p.video.readyState < 2) { return; }
      var luma = sampleLuma(p.video);
      if (luma === null) { return; }
      if (luma < 8) {
        p.black = (p.black || 0) + 1;
        if (p.black >= 2) { setHealth(i, 'bad'); }
      } else {
        p.black = 0;
        setHealth(i, 'ok');
      }
    });
  }, 5000);

  // ---- Salud comprobada por Python (playlists) ----
  function refreshPyHealth() {
    if (TEST_URLS) { return; }
    window.pywebview.api.get_health().then(function (h) {
      pyHealth = h;
    }).catch(function () {});
  }
  setInterval(refreshPyHealth, 60 * 1000);

  // Vigilante: si el video visible se queda pausado por cualquier motivo,
  // lo relanza. Garantiza reproduccion continua sin intervencion.
  setInterval(function () {
    var p = players[current];
    if (p && p.video.paused) { p.video.play().catch(function () {}); }
  }, 3000);

  // La meteorologia del rotulo se refresca aunque no se cambie de camara.
  setInterval(function () { updateWeather(current); }, 5 * 60 * 1000);

  function boot() {
    refreshPyHealth();
    poolIndices().forEach(createFrame);

    var barFill = document.querySelector('#bar div');
    var t0 = Date.now();
    var barTimer = setInterval(function () {
      var pct = Math.min(100, (Date.now() - t0) / WARMUP_MS * 100);
      barFill.style.width = pct + '%';
      if (pct >= 100) { clearInterval(barTimer); }
    }, 100);

    setTimeout(function () {
      show(0);
      document.getElementById('splash').className = 'hidden';
    }, WARMUP_MS);
  }

  if (TEST_URLS || window.pywebview) {
    boot();
  } else {
    window.addEventListener('pywebviewready', boot);
  }
</script>
</body>
</html>"""


def build_html(test_urls=None):
    cams = [
        {
            "title": c["title"],
            "town": c["town"],
            "map": build_map_svg(c["lat"], c["lon"]),
        }
        for c in CAMERAS
    ]
    hls_js = (Path(__file__).parent / "hls.min.js").read_text(encoding="utf-8")
    return (
        PAGE_TEMPLATE
        .replace("__HLS_JS__", hls_js)
        .replace("__CAMERAS__", json.dumps(cams, ensure_ascii=False))
        .replace("__BUFFER_AHEAD__", str(BUFFER_AHEAD))
        .replace("__BUFFER_BEHIND__", str(BUFFER_BEHIND))
        .replace("__WARMUP_MS__", str(WARMUP_MS))
        .replace("__LOOP_MS__", str(LOOP_SECONDS * 1000))
        .replace("__LOOP_S__", str(LOOP_SECONDS))
        .replace("__TEST_URLS__", json.dumps(test_urls) if test_urls else "null")
    )


def main():
    resolver = StreamResolver(CAMERAS)
    threading.Thread(target=resolver.prefetch_all, daemon=True).start()
    health = HealthChecker(resolver)
    health.start()
    webview.create_window(
        "Webcams de Asturias",
        html=build_html(),
        js_api=Api(resolver, WeatherService(CAMERAS), health),
        width=1280,
        height=800,
        background_color="#000000",
    )
    webview.start()


if __name__ == "__main__":
    main()
