# AGENTS.md

Notas para un asistente de IA (Claude Code u otro) que retome este proyecto
sin el historial de la conversación en la que se construyó. Ver
[README.md](README.md) para instalación y uso; esto es contexto de "por qué
está hecho así" y decisiones a respetar.

## Qué es esto

Dos cosas independientes en el mismo repo:

1. **App de escritorio** (`main.py` + `cameras.py` + `streams.py` +
   `mapthumb.py` + `hls.min.js`): visor de 88 webcams públicas del
   Cantábrico (Asturias + costa gallega de Estaca de Bares), con
   navegación por teclado/ratón, buffer para cambio instantáneo, detección
   de cámaras muertas, meteo en vivo, modo loop y grabación.
2. **Rutina de evaluación del eclipse** (`captura_eclipse.py` +
   `evaluar_eclipse.py`): campaña de captura diaria (iniciada 17-07-2026,
   independiente de la app) para acumular datos de nubosidad real por
   ubicación de cara al eclipse solar total del **12-08-2026** (totalidad
   sobre Asturias ~20:26 CEST). Objetivo final: decidir desde qué webcam
   habría mejor probabilidad de verlo, y con el tiempo mejorar la
   predicción combinando el histórico con el forecast de Open-Meteo cerca
   de la fecha (idea pendiente, no implementada).

## Decisiones que no hay que deshacer sin motivo

- **No usar el reproductor embebido de rtsp.me/Angelcam directamente**
  (iframe). Se probó primero y el problema es real: ese reproductor exige
  un clic del usuario para arrancar y, al ser de otro origen, ni la app ni
  el usuario pueden dárselo de forma fiable (la capa de control de la app
  intercepta los clics). La solución fue extraer la URL `.m3u8` real
  (`streams.py: _extract_m3u8`) y reproducirla con `hls.js` sobre un
  `<video muted autoplay>` propio.
- **Los streams de rtsp.me "duermen" sin espectadores** y sirven una
  playlist con segmentos placeholder (nombre terminado en `-40x.ts`, ver
  `captura_eclipse.py: PLACEHOLDER_RE`) en vez de vídeo real. La rutina de
  captura los despierta imitando el comportamiento del reproductor
  (`wake_stream()`: página embed con cookies de sesión → su `.js` de
  sesión → sondeo de la playlist tocando segmentos hasta que cambian a
  reales). Sin esto, la captura por lotes solo conseguía ~25/80 cámaras en
  vez de ~71/80. La app normal no necesita esto porque hls.js reproduciendo
  activamente ya actúa como espectador y despierta el stream solo.
- **No borrar cámaras caídas de `cameras.py`**. El usuario pidió
  explícitamente no eliminar fuentes que fallan puntualmente porque pueden
  volver a funcionar. Tanto la app (marca "mala" temporal, reintenta a los
  10 min) como la rutina de captura (deja sin frames ese día, sin romper
  el resto) están pensadas para convivir con cámaras intermitentes.
- **No tocar el formato de `capturas/AAAA-MM-DD/<slug-cámara>/HHMMSS.jpg`
  ni los slugs de cámara** (`captura_eclipse.py: slug()`, indexado por
  posición en `CAMERAS`). `evaluar_eclipse.py` depende de ese formato para
  construir la serie histórica y el ranking acumulado; cambiarlo a mitad
  de campaña rompe la comparación entre días.
- **`capturas/`, `animaciones/`, `reportes/`, `grabaciones/` van en
  `.gitignore`**: son datos generados (potencialmente cientos de MB/día),
  no código. No los añadas al repo salvo que el usuario lo pida
  explícitamente.
- **La carpeta `memoria/`** es una copia puntual (volcado manual) de la
  memoria de contexto que un asistente Claude Code mantiene entre
  sesiones fuera del repo. No se sincroniza sola — si se actualiza la
  memoria real, hay que volver a copiarla aquí a mano si se quiere
  reflejar el cambio.
- **En Linux, `pywebview` debe forzarse a Qt (`PYWEBVIEW_GUI=qt`), nunca
  dejarlo en GTK** (backend por defecto ahí). Diagnosticado a fondo: con
  GTK/WebKit2GTK, `hls.js` parsea bien el manifest y la playlist pero nunca
  llega a pedir fragmentos (evento `hlsError`/`internalException` no fatal
  al montar el buffer) — la cámara se queda en negro para siempre aunque el
  stream funcione (mismo stream, mismo `hls.js`, en Chromium se ve bien al
  servir el HTML por HTTP). Qt usa QtWebEngine (motor Chromium, como
  WebView2 en Windows) y sí decodifica. `lanzar.sh` ya fuerza esto via env
  var; necesita `python-pyqt6` + `python-pyqt6-webengine` (paquetes de
  sistema, `sudo pacman -S ...`, no instalables por pip) y `qtpy` (sí por
  pip, ya en el `.venv`). No "arreglar" esto tocando GTK/WebKit2GTK — es un
  límite real de su soporte de Media Source Extensions, no una
  configuración que falte.

## Peculiaridades del entorno de desarrollo (no del equipo de producción)

Esto se descubrió en la máquina donde se escribió el código, que **no es**
la que ejecuta la app. Si aparecen los mismos síntomas en el equipo real,
aplican los mismos workarounds; si no aparecen, ignóralos:

- Variables de entorno `SSL_CERT_FILE`/`REQUESTS_CA_BUNDLE` apuntando a un
  certificado corporativo inexistente rompían `requests`/OpenCV con
  streams por HTTPS. Workaround: `os.environ.pop(...)` al principio de
  `captura_eclipse.py`, y `verify=False` como fallback en
  `streams.py: _http_get` cuando falla la verificación TLS. Si el equipo
  real no tiene esas variables, este código es inocuo (nunca se dispara).
- Un aviso de log no fatal (`AccessibilityObject.Bounds... recursion`) al
  arrancar `pywebview` en el entorno de desarrollo (sandbox sin sesión
  gráfica interactiva real). No impidió que la ventana funcionara en las
  pruebas hechas vía navegador con los mismos streams. Si aparece en el
  equipo real y molesta, investigarlo entonces — no es necesariamente el
  mismo problema.

## Cómo se verificó cada pieza (sin navegador headless propio)

Todo el desarrollo se hizo en una máquina sin sesión gráfica interactiva
real, así que la verificación de UI se hizo renderizando el HTML generado
por `main.py` (`build_html(test_urls=...)`) en el navegador de la
herramienta de desarrollo, sirviéndolo por `python -m http.server` y
comprobando con JavaScript inyectado (`readyState`, luminancia, contenido
del DOM) en vez de capturas de pantalla de la ventana nativa. Si tocas
`main.py`, la forma más rápida de volver a comprobar cambios de
interfaz/JS sin instalar nada nuevo es ese mismo patrón: generar el HTML,
servirlo por HTTP, abrirlo en un navegador normal.

## Ejecución diaria de la rutina del eclipse (equipo Linux)

En el equipo Linux que ejecuta la campaña diaria (distinto del usado para
desarrollar), la ejecución real **no debe depender de una sesión interactiva
de Claude Code**. Decisión (ver detalle completo en
[establece_rutina_linux.md](establece_rutina_linux.md)):

- El planificador del sistema operativo (`cron` o `systemd timer`) es quien
  lanza [`run_daily.sh`](run_daily.sh) cada día a las **19:30** hora local
  (la ventana de captura es 19:30–21:00; `captura_eclipse.py` ya espera y
  corta solo, `run_daily.sh` no necesita `timeout` externo).
- Claude Code con `/loop` puede usarse **solo como supervisión** adicional
  (revisar logs, detectar fallos), nunca como el mecanismo principal de
  disparo diario: si se cierra la sesión, se reinicia el equipo o `/loop`
  no se recupera, no hay garantía de que la captura se lance.
- Este equipo concreto (Arch/Omarchy) **no tiene `cron` instalado**
  (`cronie` no está presente). Se usa un **systemd user timer** en su lugar
  (`~/.config/systemd/user/webcams-eclipse.{service,timer}`), equivalente en
  este caso a la receta de `cron` del documento de referencia. Si se
  reinstala el equipo o se cambia de máquina, reevaluar si instalar `cronie`
  o mantener systemd según lo que tenga esa máquina.
- `run_daily.sh` usa `.venv/` (creado con `python3 -m venv .venv`) porque
  Python del sistema en Arch es "externally managed" (PEP 668) y bloquea
  `pip install` global; no asumir que las dependencias del eclipse
  (`opencv-python`, `Pillow`, `requests`) están instaladas a nivel sistema.
- Antes de activar el timer se validó con una prueba rápida
  (`captura_eclipse.py --ahora 1`, 70/80 cámaras, formato correcto en
  `capturas/`) que el entorno funciona (mismo criterio que el documento de
  referencia para `cron`: no programar sin probar antes).
- Estado a 17-07-2026: timer **activo**
  (`systemctl --user enable --now webcams-eclipse.timer`) con
  `loginctl enable-linger chinso` para que se dispare aunque no haya sesión
  gráfica iniciada. Comprobar con
  `systemctl --user list-timers webcams-eclipse.timer` y revisar
  `logs/daily.log` tras la primera ejecución real.

## Fuentes de datos (contexto de por qué son de fiar)

- Cámaras: red **Webcams de Asturias** / **Hispacams**
  (`webcamsdeasturias.com`, `hispacams.com`), rastreadas por categoría
  (playas, puertos, comunidades limítrofes) para cubrir toda la costa; una
  cámara de Viveiro viene de Hispacams pero usa Angelcam como proveedor de
  vídeo en vez de rtsp.me. Las 8 cámaras de Fisterra→Ortigueira (índices
  80-87, añadidas 19-07-2026) vienen de Hispacams (Fisterra, rtsp.me) y de
  **G24/CRTVG** (`g24.gal`, radiotelevisión pública de Galicia) para el
  resto — streams `.m3u8` propios en `crtvg.es`, permanentes y sin
  necesidad de "despertar" (siempre en directo). Se probaron muchas otras
  fuentes para el tramo Costa da Morte (Camariñas, Malpica, Laxe, Cedeira,
  Cariño) sin éxito: `camaramar.com` cataloga esos puntos pero la mayoría
  no tiene cámara activa asociada (`"webcam":[]` en su Livewire), o solo
  ofrece un bucle grabado (`VODgrabaciones/...`), no directo real. Si se
  quiere ampliar esa zona más adelante, revisar de nuevo `camaramar.com`
  (puede que activen cámaras que hoy están vacías) o buscar webcams
  municipales propias de esos concellos.
- Meteo: **Open-Meteo** (`api.open-meteo.com`), API pública sin clave,
  consultada por lotes (todas las cámaras en una sola petición HTTP).
