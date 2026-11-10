"""
Genera 5 graficos de la pestana "sintetico" (benchmark 2D sintetico) directamente
desde los CSV de detalle, sin pasar por Power BI.

Incluye sMAPE (metrica de error relativo, misma que usa el paper de CAPTURe)
ademas del error absoluto -- util aca porque el error_abs crudo esta sesgado
por el tipo de pregunta: conteo_general permite ground_truth hasta 100,
mientras que conteo_forma/color/combinado casi siempre dan numeros chicos, asi
que el error absoluto de conteo_general domina el grafico 1 sin que eso
signifique necesariamente que el modelo "entiende peor" esa tarea.

Requiere:  pip install pandas matplotlib numpy

Uso:
    python graficos_sintetico.py

Los PNG quedan en: <BASE_DIR>\\graficos_sintetico\\
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CONFIGURACION
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"C:\Users\Home\Desktop\tt\benchmark_sintetico\pruebas")

MODELOS = {
    "InternVL2_1B":  "detalle_2Dsintetico_InternVL2-1B.csv",
    "moondream2":    "detalle_2Dsintetico_moondream2.csv",
    "paligemma2_3b": "detalle_2Dsintetico_paligemma2-3b-mix-448.csv",
    "qwen2_vl_2b":   "detalle_2Dsintetico_Qwen2-VL-2B-Instruct.csv",
}
ORDEN_MODELOS = list(MODELOS.keys())
ORDEN_TIPOS = ["conteo_general", "conteo_forma", "conteo_color", "conteo_combinado"]

COLORES = {
    "InternVL2_1B":  "#4EA8FF",
    "moondream2":    "#0B1F4B",
    "paligemma2_3b": "#FF7A45",
    "qwen2_vl_2b":   "#7A3FE0",
}

OUT_DIR = BASE_DIR / "graficos_sintetico"
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 2. CARGA Y UNION DE LOS 4 CSV
#    (ojo: en moondream2, respuesta_cruda a veces trae una oracion completa en
#    vez de un numero -- no afecta este script porque no se usa esa columna,
#    pero es el mismo motivo del bug que viste en Power Query)
# ---------------------------------------------------------------------------
frames = []
for modelo, archivo in MODELOS.items():
    ruta = BASE_DIR / modelo / archivo
    if not ruta.exists():
        print(f"[AVISO] no encontre {ruta}, me lo salto")
        continue
    df_m = pd.read_csv(ruta)
    df_m["modelo"] = modelo
    frames.append(df_m)

if not frames:
    raise SystemExit("No se encontro ningun CSV. Revisa BASE_DIR y los nombres de archivo.")

df = pd.concat(frames, ignore_index=True)

for col in ["acierto_exacto", "parse_fail", "timeout"]:
    if df[col].dtype != bool:
        df[col] = df[col].astype(str).str.strip().str.lower().map({"true": True, "false": False})

print(f"Filas totales cargadas: {len(df)}  |  filas por modelo:")
print(df["modelo"].value_counts().reindex(ORDEN_MODELOS))

# sMAPE por fila: 100 * |real-pred| / (|real|+|pred|), 0 si ambos son cero
denom = df["ground_truth"].abs() + df["prediccion"].abs()
df["smape"] = np.where(denom == 0, 0.0, 100 * (df["ground_truth"] - df["prediccion"]).abs() / denom)

ORDEN_NUM_SHAPES = sorted(df["num_shapes"].unique())

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.6,
    "font.size": 10,
})


def grafico_barras_agrupadas(tabla, categorias, titulo, ylabel, nombre_archivo, ylim=None):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    width = 0.8 / len(ORDEN_MODELOS)
    x = range(len(categorias))
    for i, modelo in enumerate(ORDEN_MODELOS):
        if modelo not in tabla.columns:
            continue
        ax.bar([xi + i * width for xi in x], tabla[modelo].reindex(categorias).values,
               width=width, label=modelo, color=COLORES[modelo])
    ax.set_xticks([xi + width * (len(ORDEN_MODELOS) - 1) / 2 for xi in x])
    ax.set_xticklabels(categorias, rotation=15, ha="right")
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / nombre_archivo, dpi=150)
    plt.close()


def grafico_lineas(tabla, categorias, titulo, ylabel, nombre_archivo):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for modelo in ORDEN_MODELOS:
        if modelo not in tabla.columns:
            continue
        ax.plot(categorias, tabla[modelo].reindex(categorias), marker="o", markersize=4,
                label=modelo, color=COLORES[modelo])
    ax.set_title(titulo)
    ax.set_xlabel("num_shapes")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / nombre_archivo, dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 3. GRAFICO 1 - Suma de error_abs por modelo y tipo_pregunta
# ---------------------------------------------------------------------------
tab1 = (
    df.groupby(["modelo", "tipo_pregunta"])["error_abs"].sum()
    .unstack("tipo_pregunta").reindex(ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(7, 4.2))
tab1.reindex(columns=ORDEN_TIPOS).plot(kind="bar", ax=ax,
    color=["#4EA8FF", "#0B1F4B", "#FF7A45", "#7A3FE0"], width=0.75)
ax.set_title("Suma de error_abs por modelo y tipo_pregunta")
ax.set_ylabel("Suma de error_abs")
ax.legend(title="tipo_pregunta", fontsize=8)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "1_error_abs_por_modelo_tipo.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 4. GRAFICO 2 - % de acierto_exacto por num_shapes y modelo (curva de dificultad)
# ---------------------------------------------------------------------------
tab2 = (
    df.groupby(["num_shapes", "modelo"])["acierto_exacto"].mean() * 100
).unstack("modelo").reindex(ORDEN_NUM_SHAPES)
grafico_lineas(tab2, ORDEN_NUM_SHAPES, "% de acierto_exacto por num_shapes y modelo",
               "% acierto_exacto", "2_pct_acierto_por_num_shapes.png")

# ---------------------------------------------------------------------------
# 5. GRAFICO 3 - Promedio de error_abs por num_shapes y modelo
# ---------------------------------------------------------------------------
tab3 = (
    df.groupby(["num_shapes", "modelo"])["error_abs"].mean()
).unstack("modelo").reindex(ORDEN_NUM_SHAPES)
grafico_lineas(tab3, ORDEN_NUM_SHAPES, "Promedio de error_abs por num_shapes y modelo",
               "Promedio de error_abs", "3_promedio_error_abs_por_num_shapes.png")

# ---------------------------------------------------------------------------
# 6. GRAFICO 4 - % de acierto_exacto por tipo_pregunta y modelo
# ---------------------------------------------------------------------------
tab4 = (
    df.groupby(["tipo_pregunta", "modelo"])["acierto_exacto"].mean() * 100
).unstack("modelo").reindex(ORDEN_TIPOS)
grafico_barras_agrupadas(tab4, ORDEN_TIPOS, "% de acierto_exacto por tipo_pregunta y modelo",
                          "% acierto_exacto", "4_pct_acierto_por_tipo.png", ylim=(0, 100))

# ---------------------------------------------------------------------------
# 7. GRAFICO 5 - sMAPE promedio por num_shapes y modelo
#    (version en error relativo del grafico 3 -- corrige el sesgo de escala
#    entre tipos de pregunta explicado arriba; compara ambos graficos)
# ---------------------------------------------------------------------------
tab5 = (
    df.groupby(["num_shapes", "modelo"])["smape"].mean()
).unstack("modelo").reindex(ORDEN_NUM_SHAPES)
grafico_lineas(tab5, ORDEN_NUM_SHAPES, "sMAPE promedio por num_shapes y modelo",
               "sMAPE (%)", "5_smape_por_num_shapes.png")

print(f"\nListo. Los 5 graficos quedaron en: {OUT_DIR}")
