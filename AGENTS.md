# AGENTS.md

Notas para un asistente de IA (Claude Code u otro) que retome este proyecto
sin el historial de la conversación en la que se construyó. Ver
[README.md](README.md) para instalación y uso; esto es contexto de "por qué
está hecho así" y decisiones a respetar.

## Qué es esto

Dos cosas independientes en el mismo repo:

1. **App de escritorio** (`main.py` + `cameras.py` + `streams.py` +
   `mapthumb.py` + `hls.min.js`): visor de 80 webcams públicas del
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

## Fuentes de datos (contexto de por qué son de fiar)

- Cámaras: red **Webcams de Asturias** / **Hispacams**
  (`webcamsdeasturias.com`, `hispacams.com`), rastreadas por categoría
  (playas, puertos, comunidades limítrofes) para cubrir toda la costa; una
  cámara de Viveiro viene de Hispacams pero usa Angelcam como proveedor de
  vídeo en vez de rtsp.me.
- Meteo: **Open-Meteo** (`api.open-meteo.com`), API pública sin clave,
  consultada por lotes (todas las cámaras en una sola petición HTTP).
