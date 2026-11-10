"""
Genera 4 graficos de la pestana "omnispatial" directamente desde los CSV de
detalle, sin pasar por Power BI.

Requiere:  pip install pandas matplotlib

Uso:
    python graficos_omnispatial.py

Los PNG quedan en: <BASE_DIR>\\graficos_omnispatial\\
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CONFIGURACION
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"C:\Users\Home\Desktop\tt\pruebas\razonamiento espacial")

MODELOS = {
    "InternVL2_1B":  "detalle_OmniSpatial_InternVL2-1B.csv",
    "moondream2":    "detalle_OmniSpatial_moondream2.csv",
    "paligemma2_3b": "detalle_OmniSpatial_paligemma2-3b-mix-448.csv",
    "qwen2_vl_2b":   "detalle_OmniSpatial_Qwen2-VL-2B-Instruct.csv",
}
# carpeta real por modelo (paligemma2/qwen2vl tienen nombre de carpeta distinto
# al nombre "oficial" del modelo)
CARPETAS = {
    "InternVL2_1B":  "InternVL2_1B",
    "moondream2":    "moondream2",
    "paligemma2_3b": "paligemma2",
    "qwen2_vl_2b":   "qwen2vl",
}
ORDEN_MODELOS = list(MODELOS.keys())
ORDEN_TRACKS = ["Geometric_Reasoning", "Motion_Analysis", "Egocentric", "Allocentric"]

# baseline de azar por track (viene de tus resultados_OmniSpatial_*.txt; es
# identico en los 4 modelos porque depende del dataset, no del modelo)
BASELINE_AZAR = {
    "Geometric_Reasoning": 0.27,
    "Motion_Analysis": 0.31,
    "Egocentric": 0.36,
    "Allocentric": 0.28,
}

COLORES = {
    "InternVL2_1B":  "#4EA8FF",
    "moondream2":    "#0B1F4B",
    "paligemma2_3b": "#FF7A45",
    "qwen2_vl_2b":   "#7A3FE0",
}

OUT_DIR = BASE_DIR / "graficos_omnispatial"
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 2. CARGA Y UNION DE LOS 4 CSV
# ---------------------------------------------------------------------------
frames = []
for modelo, archivo in MODELOS.items():
    ruta = BASE_DIR / CARPETAS[modelo] / archivo
    if not ruta.exists():
        print(f"[AVISO] no encontre {ruta}, me lo salto")
        continue
    df_m = pd.read_csv(ruta)
    df_m["modelo"] = modelo
    frames.append(df_m)

if not frames:
    raise SystemExit("No se encontro ningun CSV. Revisa BASE_DIR/CARPETAS y los nombres de archivo.")

df = pd.concat(frames, ignore_index=True)

for col in ["acierto", "parse_fail", "timeout", "has_opts"]:
    if df[col].dtype != bool:
        df[col] = df[col].astype(str).str.strip().str.lower().map({"true": True, "false": False})

print(f"Filas totales cargadas: {len(df)}  |  filas por modelo:")
print(df["modelo"].value_counts().reindex(ORDEN_MODELOS))

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.6,
    "font.size": 10,
})


def grafico_barras_agrupadas(tabla, categorias, titulo, ylabel, nombre_archivo,
                              series_extra=None, ylim=None):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    n_series = len(ORDEN_MODELOS) + (1 if series_extra else 0)
    width = 0.8 / n_series
    x = range(len(categorias))
    for i, modelo in enumerate(ORDEN_MODELOS):
        if modelo not in tabla.columns:
            continue
        ax.bar([xi + i * width for xi in x], tabla[modelo].reindex(categorias).values,
               width=width, label=modelo, color=COLORES[modelo])
    if series_extra:
        nombre_serie, valores = series_extra
        i = len(ORDEN_MODELOS)
        ax.bar([xi + i * width for xi in x], [valores[c] for c in categorias],
               width=width, label=nombre_serie, color="#999999", hatch="//")
    ax.set_xticks([xi + width * (n_series - 1) / 2 for xi in x])
    ax.set_xticklabels(categorias, rotation=15, ha="right")
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / nombre_archivo, dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 3. GRAFICO 1 - % de acierto por track y modelo, con linea de baseline de azar
# ---------------------------------------------------------------------------
tab1 = (
    df.groupby(["track", "modelo"])["acierto"].mean() * 100
).unstack("modelo").reindex(ORDEN_TRACKS)

baseline_pct = {t: BASELINE_AZAR[t] * 100 for t in ORDEN_TRACKS}
grafico_barras_agrupadas(
    tab1, ORDEN_TRACKS,
    "% de acierto por track y modelo (vs. baseline de azar)",
    "% acierto",
    "1_pct_acierto_por_track.png",
    series_extra=("Baseline azar", baseline_pct),
    ylim=(0, 100),
)

# ---------------------------------------------------------------------------
# 4. GRAFICO 2 - % de parse_fail por modelo y track
#    (el parse_fail varia mucho por track -- ej. Motion_Analysis en InternVL2 -
#     y eso se pierde si solo se ve el total por modelo)
# ---------------------------------------------------------------------------
tab2 = (
    df.groupby(["track", "modelo"])["parse_fail"].mean() * 100
).unstack("modelo").reindex(ORDEN_TRACKS)

grafico_barras_agrupadas(
    tab2, ORDEN_TRACKS,
    "% de parse_fail por track y modelo",
    "% parse_fail",
    "2_pct_parse_fail_por_track.png",
)

# ---------------------------------------------------------------------------
# 5. GRAFICO 3 - % de acierto global por modelo (ranking simple)
# ---------------------------------------------------------------------------
tab3 = (df.groupby("modelo")["acierto"].mean() * 100).reindex(ORDEN_MODELOS)

fig, ax = plt.subplots(figsize=(5.5, 4))
ax.bar(ORDEN_MODELOS, tab3.values, color=[COLORES[m] for m in ORDEN_MODELOS])
ax.set_title("% de acierto global por modelo (OmniSpatial)")
ax.set_ylabel("% acierto")
ax.set_ylim(0, 100)
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig(OUT_DIR / "3_pct_acierto_global.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 6. GRAFICO 4 - Geometric_Reasoning: % de acierto con vs sin opciones, por modelo
#    (has_opts solo varia dentro de este track; en los otros 3 siempre es True)
# ---------------------------------------------------------------------------
geo = df[df["track"] == "Geometric_Reasoning"].copy()
geo["opciones"] = geo["has_opts"].map({True: "con_opts", False: "sin_opts"})

tab4 = (
    geo.groupby(["opciones", "modelo"])["acierto"].mean() * 100
).unstack("modelo").reindex(["sin_opts", "con_opts"])

grafico_barras_agrupadas(
    tab4, ["sin_opts", "con_opts"],
    "Geometric_Reasoning: % de acierto con vs sin opciones, por modelo",
    "% acierto",
    "4_geometric_con_sin_opciones.png",
    ylim=(0, 100),
)

n_geo = geo.groupby(["opciones", "modelo"]).size().unstack("modelo").reindex(["sin_opts", "con_opts"])
print("\nn por opciones y modelo en Geometric_Reasoning (para leer el grafico 4 con contexto):")
print(n_geo)

print(f"\nListo. Los 4 graficos quedaron en: {OUT_DIR}")
