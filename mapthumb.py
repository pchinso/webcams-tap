"""Genera un mapa SVG simplificado (Asturias + costa norte de Galicia)
con un marcador de ubicacion."""

# Bounding box: desde Fisterra hasta el oriente asturiano
LON_MIN, LON_MAX = -9.40, -4.50
LAT_MIN, LAT_MAX = 42.85, 43.85

WIDTH, HEIGHT = 330, 96

# Silueta simplificada de Asturias (lon, lat). No es topograficamente
# exacta: sirve como referencia visual de ubicacion en una miniatura.
OUTLINE_ASTURIAS = [
    (-7.05, 43.58), (-6.90, 43.62), (-6.55, 43.60), (-6.15, 43.61),
    (-5.93, 43.62), (-5.70, 43.64), (-5.66, 43.58), (-5.30, 43.54),
    (-5.05, 43.49), (-4.75, 43.45), (-4.55, 43.32), (-4.85, 43.02),
    (-5.20, 42.90), (-5.75, 42.95), (-6.25, 43.05), (-6.65, 43.16),
    (-7.05, 43.26), (-7.18, 43.46), (-7.05, 43.58),
]

# Franja costera del norte de Galicia (A Marina / Ortegal / Ferrolterra /
# A Coruna / Costa da Morte), con la punta de Estaca de Bares y Fisterra,
# para ubicar las camaras gallegas.
OUTLINE_GALICIA = [
    (-7.04, 43.56), (-7.25, 43.60), (-7.35, 43.68), (-7.45, 43.71),
    (-7.60, 43.70), (-7.66, 43.75), (-7.70, 43.79), (-7.75, 43.75),
    (-7.88, 43.70), (-7.90, 43.55),
    (-7.95, 43.48), (-8.10, 43.45), (-8.25, 43.48), (-8.35, 43.42),
    (-8.40, 43.37), (-8.55, 43.31), (-8.75, 43.34), (-8.90, 43.28),
    (-9.05, 43.24), (-9.15, 43.15), (-9.22, 43.11), (-9.29, 42.98),
    (-9.29, 42.89), (-9.15, 42.87), (-9.00, 42.93), (-8.80, 42.95),
    (-8.55, 42.92), (-8.30, 42.95), (-8.00, 43.05), (-7.75, 43.18),
    (-7.55, 43.28), (-7.40, 43.35),
    (-7.10, 43.40), (-7.05, 43.47), (-7.04, 43.56),
]


def _project(lon, lat):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * WIDTH
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * HEIGHT
    return x, y


def _polygon(outline, fill, opacity):
    points = " ".join(
        f"{x:.1f},{y:.1f}" for x, y in (_project(lon, lat) for lon, lat in outline)
    )
    return (f'<polygon points="{points}" fill="{fill}" stroke="#bfe3c4" '
            f'stroke-width="1" opacity="{opacity}"/>')


def build_map_svg(lat, lon):
    mx, my = _project(lon, lat)
    mx = max(4, min(WIDTH - 4, mx))
    my = max(4, min(HEIGHT - 4, my))

    return f'''<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}"
     xmlns="http://www.w3.org/2000/svg">
  {_polygon(OUTLINE_GALICIA, "#3d5a7a", 0.85)}
  {_polygon(OUTLINE_ASTURIAS, "#2f6b3a", 0.9)}
  <circle cx="{mx:.1f}" cy="{my:.1f}" r="7" fill="#ff3b30" opacity="0.35">
    <animate attributeName="r" values="5;9;5" dur="1.8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.45;0.05;0.45" dur="1.8s" repeatCount="indefinite"/>
  </circle>
  <circle cx="{mx:.1f}" cy="{my:.1f}" r="3.2" fill="#ff3b30" stroke="#ffffff" stroke-width="1"/>
</svg>'''
