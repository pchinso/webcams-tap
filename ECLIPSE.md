# Rutina de evaluación para el eclipse del 12-08-2026

La franja de totalidad del eclipse solar del **12 de agosto de 2026** cruza
Asturias (totalidad hacia las **20:26 CEST**; fases parciales aprox.
19:30–21:20). Esta rutina, independiente de la app de visualización, captura
cada día la ventana del eclipse en todas las cámaras para evaluar desde qué
ubicaciones se habría visto.

## Componentes

| Archivo | Función |
|---|---|
| `captura_eclipse.py` | Captura diaria: un frame de cada cámara cada 60 s durante la ventana 19:30–21:00, más meteo (nubes/visibilidad/temperatura) cada 10 min. |
| `evaluar_eclipse.py` | Genera un timelapse animado (.webp) por cámara y día, puntúa cada ubicación y produce informes HTML. |
| `capturar.bat` | Lanzador de la captura (instala dependencias si faltan). |

## Uso

**Programar la captura diaria** (una sola vez, en una consola con permisos):

```
schtasks /create /tn "CapturaEclipse" /tr "C:\_Dev\Python\Projects\webcams-tap\capturar.bat" /sc daily /st 19:25
```

(El script espera por sí mismo hasta las 19:30 y termina a las 21:00; si el
equipo está apagado ese día, no hay captura.)

**Prueba rápida** (sin esperar a la ventana):

```
python captura_eclipse.py --ahora 3 --intervalo 30
```

**Evaluar y generar informes** (cualquier momento; procesa todos los días
capturados):

```
python evaluar_eclipse.py
```

Abre después `reportes\reporte-global.html` (ranking acumulado) o los
`reporte-AAAA-MM-DD.html` de cada día, con el timelapse de cada cámara.

## Cómo puntúa

- **Probabilidad de éxito** = 100 − nubosidad media (%) durante la ventana,
  con datos de Open-Meteo tomados en el momento de la captura.
- Se exige evidencia visual: si una cámara aportó menos de 5 frames con
  imagen (no negros), se marca "sin datos" en vez de puntuar.
- Veredictos: ≥75 % probable · 45–74 % dudoso · <45 % improbable.

## Detalles técnicos

- Los frames se extraen del stream HLS con OpenCV/ffmpeg (1280 px de ancho,
  JPEG). ~90 frames por cámara y día; unos 550 MB/día de disco para las 88
  cámaras (80 hasta 18-07-2026, +8 de Fisterra/Muxía/A Coruña/Ferrol/
  Ortigueira añadidas el 19-07-2026 al final de `cameras.py`, índices 80-87,
  sin afectar a la serie histórica de las 80 anteriores).
- Los streams de rtsp.me se "duermen" sin espectadores y devuelven una
  playlist placeholder; la captura los despierta imitando a su reproductor
  (cookies de sesión + sondeo de playlist). Cámaras caídas en origen quedan
  sin frames y no puntúan.
- Ajustes en la cabecera de `captura_eclipse.py`: ventana horaria, intervalo,
  calidad JPEG, nº de hilos.
