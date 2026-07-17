# webcams-tap

App de escritorio (Windows) que muestra en directo webcams públicas del
Cantábrico — costa de Asturias y la zona de Estaca de Bares en Galicia — más
una rutina independiente para evaluar de cara al **eclipse solar total del
12-08-2026** qué ubicaciones tendrán mejor probabilidad de cielo despejado.

Este repo se desarrolló en una máquina que **no ejecuta la app** (solo
edita el código); todo lo de abajo es para ponerlo en marcha en el equipo
real. Ver también [AGENTS.md](AGENTS.md) si quien lo retoma es un asistente
de IA.

## Instalación

Requiere Python 3.11+ en Windows (usa WebView2, ya incluido en Windows
10/11 con Edge).

```
pip install -r requirements.txt
```

Instala `pywebview` y `requests` (para la app) y `opencv-python` + `Pillow`
(para la rutina del eclipse). `lanzar.bat` y `capturar.bat` también
instalan solos lo que falte.

## App de visualización (`main.py`)

```
python main.py
```
o doble clic en [lanzar.bat](lanzar.bat) (Windows). En Linux,
[`./lanzar.sh`](lanzar.sh) hace lo mismo: crea `.venv` si falta e instala
`requirements.txt` si `pywebview` no está disponible.

**Backend de pywebview en Linux — usar Qt, no GTK**: el backend GTK/WebKit2GTK
(el que pywebview elige por defecto en Linux) no consigue decodificar estos
streams HLS vía `hls.js`/MediaSource — la cámara se queda en negro
indefinidamente aunque el stream funcione perfectamente (comprobado: mismo
stream, mismo `hls.js`, en Chromium se ve bien). `lanzar.sh` fuerza el
backend Qt (`PYWEBVIEW_GUI=qt`), que usa QtWebEngine (motor Chromium, igual
que WebView2 en Windows) y sí decodifica bien. Requiere paquetes de sistema
que `pip` no puede instalar solo:

```
sudo pacman -S python-pyqt6 python-pyqt6-webengine
```

`lanzar.sh` avisa en pantalla si faltan.

Al arrancar precarga varios streams en paralelo (barra de progreso ~5 s) y
muestra la primera cámara de [cameras.py](cameras.py) (80 cámaras, ordenadas
de oeste a este siguiendo la costa: Viveiro → La Franca, con 4 cámaras de
interior al final).

**Controles:**
| Acción | Tecla/ratón |
|---|---|
| Siguiente cámara | cualquier tecla · clic izquierdo |
| Cámara anterior | `b` · clic derecho |
| Activar/desactivar modo loop (avanza sola cada 10 s) | `l` |
| Guardar lo grabado durante el loop | `r` (solo graba mientras el loop está activo; guarda en `grabaciones/loop-*.webm` y sigue grabando) |

**Qué se ve en pantalla:** vídeo a pantalla completa, rótulo abajo a la
izquierda (nombre, pueblo, nº de cámara, temperatura/nubes/visibilidad),
mapa de ubicación abajo a la derecha, insignias de loop/grabación arriba a
la derecha cuando están activos.

### Cómo funciona por dentro (para no romperlo sin saberlo)

- Las cámaras son streams HLS. Casi todas vienen de **rtsp.me** (la web
  `webcamsdeasturias.com` embebe su reproductor); una (Viveiro) usa
  **Angelcam**. En vez de usar su reproductor embebido (exige clic manual
  para arrancar, imposible de automatizar desde un iframe de otro origen),
  [`streams.py`](streams.py) **extrae la URL `.m3u8` real** de la página
  embed y la reproduce con `hls.js` sobre un `<video muted autoplay>`
  propio — así siempre está en reproducción sin intervención.
- La URL `.m3u8` lleva un token que caduca (~40 min): se refresca sola si
  el reproductor falla.
- **Los streams de rtsp.me "duermen" sin espectadores** y devuelven una
  playlist con segmentos placeholder (nombre acabado en `-40x.ts`) en vez
  de vídeo real. Para "despertarlos" hay que imitar a su reproductor:
  cargar la página embed (cookies de sesión), su `.js` de sesión, y sondear
  la playlist tocando los segmentos hasta que aparecen los reales. Esto
  está implementado en `wake_stream()` dentro de
  [`captura_eclipse.py`](captura_eclipse.py); la app (`main.py`) no lo
  necesita porque hls.js reproduciendo activamente ya cuenta como
  "espectador" y el stream despierta solo en unos segundos.
- **Buffer de reproducción**: para que cambiar de cámara sea instantáneo,
  se mantienen conectados en paralelo la cámara actual + 3 siguientes + 2
  anteriores (`BUFFER_AHEAD`/`BUFFER_BEHIND` en `main.py`). Cambiar de
  cámara solo alterna qué `<video>` oculto se muestra.
- **Detección de cámaras muertas/en negro**: un hilo Python comprueba cada
  5 min que la playlist de cada cámara responde de verdad, y el frontend
  muestrea la luminancia del fotograma cada 5 s (imagen casi negra dos
  veces seguidas → mala). Las cámaras marcadas malas se **saltan** al
  navegar (nunca se borran de la lista: se reintentan solas a los 10 min).
- **Meteo**: temperatura/nubes/visibilidad de Open-Meteo (API pública sin
  clave), una sola petición por lotes para las 80 cámaras, cacheada 10 min.
- Ver las constantes configurables al principio de `main.py`
  (`BUFFER_AHEAD`, `WARMUP_MS`, `WEATHER_MAX_AGE`, `HEALTH_INTERVAL`,
  `LOOP_SECONDS`).

## Rutina de captura para el eclipse

Ver **[ECLIPSE.md](ECLIPSE.md)** para el detalle completo (cómo programar
la tarea diaria, cómo puntúa, formato de datos). Resumen:

- **[`captura_eclipse.py`](captura_eclipse.py)**: cada día, en la ventana
  19:30–21:00 (totalidad del eclipse ~20:26 CEST), guarda un frame JPEG de
  cada cámara cada 60 s + meteo cada 10 min, en `capturas/AAAA-MM-DD/`.
  Uso normal: `python captura_eclipse.py` (espera a la ventana de hoy).
  Prueba rápida: `python captura_eclipse.py --ahora 3 --intervalo 30`.
- **[`evaluar_eclipse.py`](evaluar_eclipse.py)**: genera un timelapse
  animado (.webp) por cámara/día y los informes HTML en `reportes/`
  (`reporte-AAAA-MM-DD.html` por día, `reporte-global.html` acumulado).
  Uso: `python evaluar_eclipse.py`.
- Programación diaria (Programador de tareas de Windows, una vez):
  ```
  schtasks /create /tn "CapturaEclipse" /tr "C:\_Dev\Python\Projects\webcams-tap\capturar.bat" /sc daily /st 19:25
  ```

`capturas/`, `animaciones/`, `reportes/` y `grabaciones/` están en
`.gitignore`: son datos generados, no se versionan.

## Estructura de archivos

| Archivo | Qué es |
|---|---|
| `main.py` | App de visualización (ventana pywebview) |
| `cameras.py` | Lista de las 80 cámaras: pueblo, título, lat/lon, URL embed |
| `streams.py` | Resolución de URLs `.m3u8` desde rtsp.me/Angelcam (compartido por app y rutina) |
| `mapthumb.py` | Genera el mapa SVG de ubicación (Asturias + costa gallega) |
| `hls.min.js` | Librería hls.js embebida en la página (no es código propio) |
| `lanzar.bat` | Lanza la app en Windows, instalando dependencias si faltan |
| `lanzar.sh` | Lanza la app en Linux, instalando dependencias si faltan |
| `captura_eclipse.py` | Rutina diaria de captura para el eclipse |
| `evaluar_eclipse.py` | Genera timelapses e informes del eclipse |
| `capturar.bat` | Lanza la captura diaria (para el Programador de tareas) |
| `run_daily.sh` | Lanza la captura + evaluación diaria en Linux (cron/systemd) |
| `ECLIPSE.md` | Documentación detallada de la campaña del eclipse |
| `memoria/` | Copia de la memoria de contexto del proyecto (ver `memoria/MEMORY.md`) — no se sincroniza sola, es un volcado puntual |

## Añadir o corregir cámaras

Cada entrada de `cameras.py` es:
```python
{
    "town": "Nombre del pueblo",
    "title": "Descripción de la cámara",
    "lat": 43.5, "lon": -5.6,
    "embed_url": "https://rtsp.me/embed/XXXXXXXX/",  # o el iframe de Angelcam
},
```
Para encontrar el `embed_url` de una cámara de `webcamsdeasturias.com`:
abrir su página, buscar en el HTML el `<iframe src="https://rtsp.me/embed/...">`
(o el de `v.angelcam.com/iframe?v=...` para las de Hispacams/Viveiro).

## Estado conocido a 17-07-2026

Cámaras caídas en origen (sin stream, no es un bug de la app): Burela -
Playa de Portelo, Playa de Porcía, Acantilados de Luarca, Playa San Pedro
de la Ribera, Desembocadura del río Nalón, Playa de La Ñora. Se dejan en
la lista por si vuelven a emitir.
