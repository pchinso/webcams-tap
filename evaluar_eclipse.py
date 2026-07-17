"""Evalua las capturas diarias del eclipse: genera una animacion por camara
y dia, calcula la probabilidad de exito (cielo despejado) y produce informes
HTML: uno por dia y un ranking global acumulado.

Uso:
    python evaluar_eclipse.py                 evalua todos los dias capturados
    python evaluar_eclipse.py 2026-07-20      evalua solo ese dia

Salida:
    animaciones/AAAA-MM-DD/<camara>.webp      timelapse animado por camara
    reportes/reporte-AAAA-MM-DD.html          informe del dia (ranking)
    reportes/reporte-global.html              ranking acumulado de todos los dias

Criterio de puntuacion por camara y dia:
    - nubosidad media durante la ventana (Open-Meteo, capturada en el momento):
      la probabilidad base de ver el eclipse es (100 - nubosidad media).
    - se penaliza si la camara fallo (pocos frames): sin imagen no hay evidencia.
    - la luminancia de los frames descarta camaras muertas o en negro.
"""

import json
import statistics
import sys
from pathlib import Path

from PIL import Image

from cameras import CAMERAS

BASE = Path(__file__).parent
CAPTURAS = BASE / "capturas"
ANIMACIONES = BASE / "animaciones"
REPORTES = BASE / "reportes"

ANIM_WIDTH = 480         # ancho de las animaciones
ANIM_FRAME_MS = 150      # duracion de cada frame en la animacion
MIN_FRAMES = 5           # menos frames que esto = datos insuficientes
BLACK_LUMA = 10          # umbral de frame negro (0-255)

ECLIPSE_INFO = ("Eclipse solar total del 12-08-2026 &middot; totalidad sobre "
                "Asturias hacia las 20:26 CEST &middot; ventana evaluada: "
                "19:30&ndash;21:00")


def mean_luma(img):
    small = img.convert("L").resize((32, 18))
    data = list(small.getdata())
    return sum(data) / len(data)


def build_animation(frames, out_path):
    images = []
    for f in frames:
        img = Image.open(f)
        w, h = img.size
        if w > ANIM_WIDTH:
            img = img.resize((ANIM_WIDTH, int(h * ANIM_WIDTH / w)))
        images.append(img)
    images[0].save(out_path, save_all=True, append_images=images[1:],
                   duration=ANIM_FRAME_MS, loop=0, quality=70, method=4)


def weather_stats(meteo, cam_index):
    clouds, vis = [], []
    for snap in meteo:
        item = snap.get("data", [])
        if cam_index < len(item) and item[cam_index]:
            c = item[cam_index].get("cloud")
            v = item[cam_index].get("vis")
            if c is not None:
                clouds.append(c)
            if v is not None:
                vis.append(v)
    return {
        "cloud_avg": statistics.mean(clouds) if clouds else None,
        "cloud_max": max(clouds) if clouds else None,
        "vis_min": min(vis) if vis else None,
    }


def evaluate_day(date_str):
    day_dir = CAPTURAS / date_str
    if not day_dir.is_dir():
        print(f"  {date_str}: sin capturas, se omite")
        return None

    meteo = []
    meteo_file = day_dir / "meteo.json"
    if meteo_file.exists():
        meteo = json.loads(meteo_file.read_text(encoding="utf-8"))

    anim_dir = ANIMACIONES / date_str
    anim_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, cam in enumerate(CAMERAS):
        cam_dirs = sorted(day_dir.glob(f"{i:02d}-*"))
        frames = sorted(cam_dirs[0].glob("*.jpg")) if cam_dirs else []
        stats = weather_stats(meteo, i)

        row = {
            "index": i,
            "town": cam["town"],
            "title": cam["title"],
            "frames": len(frames),
            "anim": None,
            "luma_ok": 0,
            **stats,
        }

        if frames:
            lumas = [mean_luma(Image.open(f)) for f in frames]
            row["luma_ok"] = sum(1 for l in lumas if l > BLACK_LUMA)
            anim_path = anim_dir / f"{cam_dirs[0].name}.webp"
            if not anim_path.exists() and len(frames) >= 2:
                try:
                    build_animation(frames, anim_path)
                except Exception as e:
                    print(f"  aviso: animacion fallida {cam_dirs[0].name}: {e}")
            if anim_path.exists():
                row["anim"] = anim_path

        # Puntuacion: base meteorologica, anulada si no hay evidencia visual
        if row["cloud_avg"] is None or row["luma_ok"] < MIN_FRAMES:
            row["score"] = None
        else:
            row["score"] = round(100 - row["cloud_avg"])
        rows.append(row)

    rows.sort(key=lambda r: (r["score"] is None, -(r["score"] or 0)))
    write_day_report(date_str, rows)
    return rows


def fmt_vis(vis_min):
    if vis_min is None:
        return "&ndash;"
    return f"{vis_min / 1000:.0f} km" if vis_min >= 10000 else f"{vis_min / 1000:.1f} km"


def verdict(score):
    if score is None:
        return ("sin datos", "#777")
    if score >= 75:
        return ("probable", "#2e9e4f")
    if score >= 45:
        return ("dudoso", "#d99a26")
    return ("improbable", "#c9463d")


HTML_HEAD = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>{title}</title><style>
body {{ font-family: "Segoe UI", Arial, sans-serif; background: #10151b;
       color: #e8edf2; margin: 24px; }}
h1 {{ font-size: 22px; }} .sub {{ color: #9ab; margin-bottom: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ padding: 8px 10px; border-bottom: 1px solid #2a3542;
          text-align: left; vertical-align: middle; font-size: 14px; }}
th {{ color: #9ab; font-weight: 600; }}
.bar {{ background: #223; border-radius: 4px; width: 120px; height: 10px;
        display: inline-block; vertical-align: middle; margin-right: 8px; }}
.bar div {{ height: 100%; border-radius: 4px; }}
img.anim {{ width: 240px; border-radius: 6px; display: block; }}
.tag {{ padding: 2px 8px; border-radius: 10px; font-size: 12px;
        color: #fff; display: inline-block; }}
</style></head><body>
"""


def score_cell(score):
    label, color = verdict(score)
    if score is None:
        return f'<span class="tag" style="background:{color}">{label}</span>'
    return (f'<span class="bar"><div style="width:{score}%;background:{color}">'
            f'</div></span>{score}% '
            f'<span class="tag" style="background:{color}">{label}</span>')


def write_day_report(date_str, rows):
    REPORTES.mkdir(exist_ok=True)
    out = [HTML_HEAD.format(title=f"Eclipse - {date_str}")]
    out.append(f"<h1>Simulacro de eclipse &mdash; {date_str}</h1>")
    out.append(f'<div class="sub">{ECLIPSE_INFO}</div>')
    out.append("<table><tr><th>#</th><th>Ubicaci&oacute;n</th>"
               "<th>Probabilidad de &eacute;xito</th><th>Nubes media/m&aacute;x</th>"
               "<th>Visib. m&iacute;n</th><th>Frames</th><th>Timelapse</th></tr>")
    for pos, r in enumerate(rows, 1):
        clouds = ("&ndash;" if r["cloud_avg"] is None
                  else f"{r['cloud_avg']:.0f}% / {r['cloud_max']:.0f}%")
        anim = "&ndash;"
        if r["anim"]:
            rel = Path("..") / r["anim"].relative_to(BASE)
            anim = f'<img class="anim" loading="lazy" src="{rel.as_posix()}">'
        out.append(
            f"<tr><td>{pos}</td><td><b>{r['title']}</b><br>"
            f"<span style='color:#9ab'>{r['town']}</span></td>"
            f"<td>{score_cell(r['score'])}</td><td>{clouds}</td>"
            f"<td>{fmt_vis(r['vis_min'])}</td>"
            f"<td>{r['luma_ok']}/{r['frames']}</td><td>{anim}</td></tr>")
    out.append("</table></body></html>")
    path = REPORTES / f"reporte-{date_str}.html"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"  informe del dia: {path}")


def write_global_report(all_days):
    """all_days: dict fecha -> rows (resultado de evaluate_day)."""
    accum = {}
    for date_str, rows in all_days.items():
        for r in rows:
            a = accum.setdefault(r["index"], {
                "town": r["town"], "title": r["title"], "scores": [], "days": 0})
            a["days"] += 1
            if r["score"] is not None:
                a["scores"].append(r["score"])

    ranking = []
    for idx, a in accum.items():
        avg = round(statistics.mean(a["scores"])) if a["scores"] else None
        ranking.append({**a, "index": idx, "avg": avg, "valid": len(a["scores"])})
    ranking.sort(key=lambda r: (r["avg"] is None, -(r["avg"] or 0)))

    out = [HTML_HEAD.format(title="Eclipse - ranking global")]
    out.append("<h1>Ranking global de ubicaciones para el eclipse</h1>")
    out.append(f'<div class="sub">{ECLIPSE_INFO}<br>'
               f"D&iacute;as evaluados: {len(all_days)} "
               f"({', '.join(sorted(all_days))})</div>")
    out.append("<table><tr><th>#</th><th>Ubicaci&oacute;n</th>"
               "<th>Probabilidad media</th><th>D&iacute;as con datos</th></tr>")
    for pos, r in enumerate(ranking, 1):
        out.append(
            f"<tr><td>{pos}</td><td><b>{r['title']}</b><br>"
            f"<span style='color:#9ab'>{r['town']}</span></td>"
            f"<td>{score_cell(r['avg'])}</td>"
            f"<td>{r['valid']}/{r['days']}</td></tr>")
    out.append("</table></body></html>")
    path = REPORTES / "reporte-global.html"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"Informe global: {path}")


def main():
    if len(sys.argv) > 1:
        dates = sys.argv[1:]
    else:
        dates = sorted(d.name for d in CAPTURAS.iterdir() if d.is_dir()) \
            if CAPTURAS.is_dir() else []
    if not dates:
        print("No hay capturas que evaluar. Ejecuta antes captura_eclipse.py")
        return

    all_days = {}
    for date_str in dates:
        print(f"Evaluando {date_str}...")
        rows = evaluate_day(date_str)
        if rows:
            all_days[date_str] = rows
    if all_days:
        write_global_report(all_days)


if __name__ == "__main__":
    main()
