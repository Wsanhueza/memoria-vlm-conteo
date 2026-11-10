"""
Genera 6 graficos de la pestana "capture" (benchmark CAPTURe) directamente
desde los CSV de detalle, sin pasar por Power BI.

Incluye sMAPE (la metrica de error relativo que usa el paper original de
CAPTURe) ademas del error absoluto, y un grafico especifico del subset
"sintetico" por num_occluded (la variable de dificultad que el paper
identifica como la que realmente explica el error -- no la magnitud total).
El subset "real" no tiene num_occluded en el dataset original (se verifico:
sus columnas son image_file, log_prob, density_map_sum, ground_truth, object,
bbox), asi que para "real" seguimos usando el bucket por magnitud.

Requiere:  pip install pandas matplotlib numpy

Uso:
    python graficos_capture.py

Los PNG quedan en: <BASE_DIR>\\graficos_capture\\
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CONFIGURACION - ajusta BASE_DIR si tu estructura cambia
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"C:\Users\Home\Desktop\tt\pruebas\Conteo")

# carpeta -> (nombre de modelo para los graficos, nombre del csv de detalle)
MODELOS = {
    "InternVL2_1B":  "detalle_CAPTURe_InternVL2-1B.csv",
    "moondream2":    "detalle_CAPTURe_moondream2.csv",
    "paligemma2_3b": "detalle_CAPTURe_paligemma2-3b.csv",
    "qwen2_vl_2b":   "detalle_CAPTURe_qwen2vl-2b.csv",
}
ORDEN_MODELOS = list(MODELOS.keys())

COLORES = {
    "InternVL2_1B":  "#4EA8FF",
    "moondream2":    "#0B1F4B",
    "paligemma2_3b": "#FF7A45",
    "qwen2_vl_2b":   "#7A3FE0",
}

OUT_DIR = BASE_DIR / "graficos_capture"
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 2. CARGA Y UNION DE LOS 4 CSV (equivalente a tu consulta "capture_resultados")
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

# columnas booleanas: en el csv suelen venir como texto "True"/"False"
for col in ["acierto_exacto", "parse_fail", "timeout"]:
    if df[col].dtype != bool:
        df[col] = (
            df[col].astype(str).str.strip().str.lower().map({"true": True, "false": False})
        )

print(f"Filas totales cargadas: {len(df)}  |  filas por modelo:")
print(df["modelo"].value_counts().reindex(ORDEN_MODELOS))

# ---------------------------------------------------------------------------
# 2b. sMAPE por fila -- metrica de error relativo del paper de CAPTURe:
#     sMAPE = 100 * |real - pred| / (|real| + |pred|)
#     Simetrica y acotada en [0, 100] (a diferencia de un % de error comun
#     no se rompe si ground_truth=0; solo queda indefinida si real y pred
#     son AMBOS cero a la vez, caso en que el acierto es perfecto -> sMAPE=0).
# ---------------------------------------------------------------------------
denom = df["ground_truth"].abs() + df["prediccion"].abs()
df["smape"] = np.where(denom == 0, 0.0, 100 * (df["ground_truth"] - df["prediccion"]).abs() / denom)

# ---------------------------------------------------------------------------
# 3. Rango_Objetos: 4 buckets por cuartiles de ground_truth, solo en subset "real"
#    (mismo criterio que ya usan tus resultados_CAPTURe_*.txt en
#     DESGLOSE_REAL_POR_BUCKET_MAGNITUD)
# ---------------------------------------------------------------------------
real = df[df["subset"] == "real"].copy()

etiquetas_base = ["1. Chico", "2. Mediano", "3. Grande", "4. Masivo"]
bucket, bins = pd.qcut(real["ground_truth"], q=4, duplicates="drop", retbins=True)
n_bins = len(bins) - 1
etiquetas_base = etiquetas_base[:n_bins]

texto_por_bin = {
    i: f"{etiquetas_base[i]} ({int(bins[i])}-{int(bins[i + 1])})" for i in range(n_bins)
}
real["Rango_Objetos"] = bucket.cat.codes.map(texto_por_bin)
ORDEN_RANGOS = [texto_por_bin[i] for i in range(n_bins)]

print("\nBuckets de Rango_Objetos calculados (bordes de cuartil sobre ground_truth):")
for i in range(n_bins):
    n_bucket = (real["Rango_Objetos"] == ORDEN_RANGOS[i]).sum() // len(ORDEN_MODELOS)
    print(f"  {ORDEN_RANGOS[i]}")
print("(Si no coinciden con los rangos que tienes en Power BI, avisame y ajustamos el criterio.)")

# ---------------------------------------------------------------------------
# 4. Estilo comun
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.grid": True,
    "grid.color": "#e6e6e6",
    "grid.linewidth": 0.6,
    "font.size": 10,
})

# ---------------------------------------------------------------------------
# 5. GRAFICO 1 - Suma de error_abs por modelo y subset
# ---------------------------------------------------------------------------
tab1 = (
    df.groupby(["modelo", "subset"])["error_abs"].sum()
    .unstack("subset").reindex(ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(6, 4))
tab1.plot(kind="bar", ax=ax, color=["#4EA8FF", "#0B1F4B"], width=0.7)
ax.set_title("Suma de error_abs por modelo y subset")
ax.set_xlabel("modelo")
ax.set_ylabel("Suma de error_abs")
ax.legend(title="subset")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "1_error_abs_por_modelo_subset.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 6. GRAFICO 2 - sMAPE promedio por modelo y subset
#    (version en error relativo del grafico 1 -- la metrica que usa el paper
#    de CAPTURe. Compara con el grafico 1: si un modelo tiene error_abs alto
#    pero sMAPE bajo, es que su error viene de imagenes con conteos grandes,
#    no de que "entienda peor" el conteo en si.)
# ---------------------------------------------------------------------------
tab_smape = (
    df.groupby(["modelo", "subset"])["smape"].mean()
    .unstack("subset").reindex(ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(6, 4))
tab_smape.plot(kind="bar", ax=ax, color=["#4EA8FF", "#0B1F4B"], width=0.7)
ax.set_title("sMAPE promedio por modelo y subset")
ax.set_xlabel("modelo")
ax.set_ylabel("sMAPE (%)")
ax.set_ylim(0, 100)
ax.legend(title="subset")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "2_smape_por_modelo_subset.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 7. GRAFICO 3 - Suma de error_abs por Rango_Objetos y modelo (linea)
# ---------------------------------------------------------------------------
tab2 = (
    real.groupby(["Rango_Objetos", "modelo"])["error_abs"].sum()
    .unstack("modelo").reindex(ORDEN_RANGOS).reindex(columns=ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(6, 4))
for modelo in ORDEN_MODELOS:
    ax.plot(tab2.index, tab2[modelo], marker="o", label=modelo, color=COLORES[modelo])
ax.set_title("Suma de error_abs por Rango_Objetos y modelo")
ax.set_xlabel("Rango_Objetos")
ax.set_ylabel("Suma de error_abs")
ax.legend(title="modelo")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(OUT_DIR / "3_error_abs_por_rango.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 8. GRAFICO 4 - Recuento de parse_fail por modelo y parse_fail (True/False)
# ---------------------------------------------------------------------------
tab3 = (
    df.groupby(["modelo", "parse_fail"]).size()
    .unstack("parse_fail").reindex(ORDEN_MODELOS).reindex(columns=[False, True]).fillna(0)
)

fig, ax = plt.subplots(figsize=(6, 4))
tab3.plot(kind="bar", ax=ax, color=["#4EA8FF", "#0B1F4B"], width=0.7)
ax.set_title("Recuento de parse_fail por modelo y parse_fail")
ax.set_xlabel("modelo")
ax.set_ylabel("Recuento de parse_fail")
ax.legend(title="parse_fail", labels=["False", "True"])
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "4_parse_fail_por_modelo.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 9. GRAFICO 5 - % de acierto_exacto por Rango_Objetos y modelo
#    (SUMA/CONTEO de acierto_exacto -> el bug que tenias en Power BI era usar
#     "Recuento" en vez de esto)
# ---------------------------------------------------------------------------
aciertos = (
    real.groupby(["Rango_Objetos", "modelo"])["acierto_exacto"].sum()
    .unstack("modelo").reindex(ORDEN_RANGOS).reindex(columns=ORDEN_MODELOS)
)
n_por_celda = (
    real.groupby(["Rango_Objetos", "modelo"])["acierto_exacto"].count()
    .unstack("modelo").reindex(ORDEN_RANGOS).reindex(columns=ORDEN_MODELOS)
)
tab4 = aciertos / n_por_celda

fig, ax = plt.subplots(figsize=(6, 4))
x = range(len(ORDEN_RANGOS))
width = 0.18
for i, modelo in enumerate(ORDEN_MODELOS):
    ax.bar([xi + i * width for xi in x], tab4[modelo].values * 100,
           width=width, label=modelo, color=COLORES[modelo])
ax.set_xticks([xi + width * 1.5 for xi in x])
ax.set_xticklabels(ORDEN_RANGOS, rotation=15)
ax.set_title("% de acierto_exacto por Rango_Objetos y modelo")
ax.set_xlabel("Rango_Objetos")
ax.set_ylabel("% acierto_exacto")
ax.set_ylim(0, 100)
ax.legend(title="modelo")
plt.tight_layout()
plt.savefig(OUT_DIR / "5_pct_acierto_por_rango.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 10. GRAFICO 6 - sMAPE promedio por num_occluded y modelo (solo subset sintetico)
#     Esta es la variable que el paper de CAPTURe identifica como la que
#     realmente explica la dificultad (no la cantidad total de objetos).
#     El subset "real" no tiene num_occluded en el dataset original, asi que
#     este grafico solo existe para "sintetico".
# ---------------------------------------------------------------------------
sintetico = df[df["subset"] == "sintetico"].copy()
sintetico["num_occluded"] = sintetico["num_occluded"].astype("Int64")

ORDEN_OCLUSION = sorted(sintetico["num_occluded"].dropna().unique().tolist())

tab6 = (
    sintetico.groupby(["num_occluded", "modelo"])["smape"].mean()
    .unstack("modelo").reindex(ORDEN_OCLUSION).reindex(columns=ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(6.5, 4.2))
for modelo in ORDEN_MODELOS:
    ax.plot(ORDEN_OCLUSION, tab6[modelo], marker="o", markersize=4, label=modelo, color=COLORES[modelo])
ax.set_title("[sintetico] sMAPE promedio por num_occluded y modelo")
ax.set_xlabel("num_occluded (objetos tapados por la caja negra)")
ax.set_ylabel("sMAPE (%)")
ax.legend(title="modelo", fontsize=8)
plt.tight_layout()
plt.savefig(OUT_DIR / "6_smape_por_num_occluded.png", dpi=150)
plt.close()

n_occ = sintetico.groupby(["num_occluded", "modelo"]).size().unstack("modelo").reindex(ORDEN_OCLUSION)
print("\nn por num_occluded y modelo en el subset sintetico (para leer el grafico 6 con contexto):")
print(n_occ)

print(f"\nListo. Los 6 graficos quedaron en: {OUT_DIR}")
