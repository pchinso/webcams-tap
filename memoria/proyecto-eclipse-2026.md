---
name: proyecto-eclipse-2026
description: Campaña de captura diaria de webcams para evaluar ubicaciones del eclipse total del 12-08-2026
metadata: 
  node_type: memory
  type: project
  originSessionId: a24bd727-61ca-4e4f-8056-7afdb2e01f7e
---

El usuario evalúa desde qué webcams del Cantábrico se verá el eclipse solar
total del **12-08-2026** (totalidad sobre Asturias ~20:26 CEST). Campaña de
captura diaria iniciada el **17-07-2026** con `captura_eclipse.py` (ventana
19:30–21:00, frame/cámara/60 s + meteo Open-Meteo cada 10 min, salida en
`capturas/`). `evaluar_eclipse.py` genera timelapses .webp e informes HTML
(`reportes/reporte-global.html` = ranking acumulado).

**Why:** el ranking acumulado de días previos estima la probabilidad de cielo
despejado por ubicación; el usuario quiere además mejorar la predicción los
días previos al eclipse (idea pendiente: usar el forecast de nubosidad de
Open-Meteo para el 12-08 y combinarlo con la tasa histórica capturada).

**How to apply:** no tocar el formato de `capturas/` ni los slugs de cámaras
(romperían la serie histórica). Cámaras caídas se dejan en la lista (pueden
volver). Los streams rtsp.me dormidos se despiertan imitando a su reproductor
(ya implementado en `wake_stream`). ~6 cámaras caídas en origen a 17-07:
Portelo, Porcía, Acantilados de Luarca, San Pedro de la Ribera,
Desembocadura del Nalón, La Ñora.
