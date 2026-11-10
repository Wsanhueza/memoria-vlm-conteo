"""
Genera 5 graficos de la pestana "tallyQA" directamente desde los CSV de detalle,
sin pasar por Power BI.

Incluye RMSE ademas de MAE (error_abs) -- el paper original de TallyQA reporta
accuracy% Y RMSE por split (Test-Simple/Test-Complex), no solo accuracy.
RMSE penaliza mas los errores grandes que el MAE (los eleva al cuadrado antes
de promediar), asi que un RMSE mucho mayor que el MAE indica que el modelo
tiene algunos errores puntuales muy grandes, no un error moderado y parejo.

Requiere:  pip install pandas matplotlib numpy

Uso:
    python graficos_tallyqa.py

Los PNG quedan en: <BASE_DIR>\\graficos_tallyqa\\
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. CONFIGURACION
# ---------------------------------------------------------------------------
BASE_DIR = Path(r"C:\Users\Home\Desktop\tt\pruebas\Conteo")

# carpeta -> nombre del csv de detalle de TallyQA
MODELOS = {
    "InternVL2_1B":  "detalle_TallyQA_InternVL2-1B.csv",
    "moondream2":    "detalle_TallyQA_moondream2.csv",
    "paligemma2_3b": "detalle_TallyQA_paligemma2-3b.csv",
    "qwen2_vl_2b":   "detalle_TallyQA_Qwen2-VL-2B-Instruct.csv",
}
ORDEN_MODELOS = list(MODELOS.keys())

COLORES = {
    "InternVL2_1B":  "#4EA8FF",
    "moondream2":    "#0B1F4B",
    "paligemma2_3b": "#FF7A45",
    "qwen2_vl_2b":   "#7A3FE0",
}

OUT_DIR = BASE_DIR / "graficos_tallyqa"
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 2. CARGA Y UNION DE LOS 4 CSV
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

for col in ["acierto_exacto", "parse_fail", "timeout", "issimple"]:
    if df[col].dtype != bool:
        df[col] = (
            df[col].astype(str).str.strip().str.lower().map({"true": True, "false": False})
        )

print(f"Filas totales cargadas: {len(df)}  |  filas por modelo:")
print(df["modelo"].value_counts().reindex(ORDEN_MODELOS))
print(
    "\n[AVISO] si paligemma2_3b / qwen2_vl_2b muestran muchas menos filas que los otros dos, "
    "es porque a esos dos les falta re-ejecutar TallyQA con el tamano de muestra actualizado "
    "(pendiente ya identificado, no es un bug de este script)."
)

# ---------------------------------------------------------------------------
# 3. Rango_GT: bucket de ground_truth adaptado a la distribucion de TallyQA (0-12,
#    muy concentrada en 0-2), en vez de usar cada valor exacto como categoria.
# ---------------------------------------------------------------------------
def bucket_gt(x):
    if x == 0:
        return "0"
    if x == 1:
        return "1"
    if x == 2:
        return "2"
    if x <= 5:
        return "3-5"
    return "6+"

df["Rango_GT"] = df["ground_truth"].apply(bucket_gt)
ORDEN_RANGOS = ["0", "1", "2", "3-5", "6+"]
ORDEN_RANGOS = [r for r in ORDEN_RANGOS if r in df["Rango_GT"].unique()]

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


def grafico_barras_agrupadas(tabla, categorias, titulo, ylabel, nombre_archivo, ylim=None):
    fig, ax = plt.subplots(figsize=(6.5, 4))
    x = range(len(categorias))
    width = 0.18
    for i, modelo in enumerate(ORDEN_MODELOS):
        if modelo not in tabla.columns:
            continue
        ax.bar([xi + i * width for xi in x], tabla[modelo].reindex(categorias).values,
               width=width, label=modelo, color=COLORES[modelo])
    ax.set_xticks([xi + width * 1.5 for xi in x])
    ax.set_xticklabels(categorias, rotation=0)
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend(title="modelo", fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / nombre_archivo, dpi=150)
    plt.close()


def grafico_lineas(tabla, categorias, titulo, ylabel, nombre_archivo):
    fig, ax = plt.subplots(figsize=(6.5, 4))
    for modelo in ORDEN_MODELOS:
        if modelo not in tabla.columns:
            continue
        ax.plot(categorias, tabla[modelo].reindex(categorias), marker="o",
                label=modelo, color=COLORES[modelo])
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    ax.legend(title="modelo", fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / nombre_archivo, dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# 5. GRAFICO 1 - Suma de error_abs por modelo e issimple (ya estaba bien construido,
#    se mantiene igual)
# ---------------------------------------------------------------------------
tab1 = (
    df.groupby(["modelo", "issimple"])["error_abs"].sum()
    .unstack("issimple").reindex(ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(6, 4))
tab1.reindex(columns=[False, True]).plot(kind="bar", ax=ax, color=["#FF7A45", "#4EA8FF"], width=0.7)
ax.set_title("Suma de error_abs por modelo e issimple")
ax.set_ylabel("Suma de error_abs")
ax.legend(title="issimple", labels=["False (compleja)", "True (simple)"])
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "1_error_abs_por_modelo_issimple.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 6. GRAFICO 2 - % de acierto_exacto por modelo e issimple
#    (version corregida de "Recuento de acierto_exacto por modelo y issimple":
#     ahora es de verdad un porcentaje de aciertos, no un conteo de filas)
# ---------------------------------------------------------------------------
tab2 = (
    df.groupby(["modelo", "issimple"])["acierto_exacto"].mean() * 100
).unstack("issimple").reindex(ORDEN_MODELOS)

fig, ax = plt.subplots(figsize=(6, 4))
tab2.reindex(columns=[False, True]).plot(kind="bar", ax=ax, color=["#FF7A45", "#4EA8FF"], width=0.7)
ax.set_title("% de acierto_exacto por modelo e issimple")
ax.set_ylabel("% acierto_exacto")
ax.set_ylim(0, 100)
ax.legend(title="issimple", labels=["False (compleja)", "True (simple)"])
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "2_pct_acierto_por_issimple.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 7. GRAFICO 3 - Promedio de error_abs por Rango_GT y modelo
#    (version corregida de "Suma de error_abs por ground_truth y modelo": usa
#     PROMEDIO en vez de SUMA para no que un bucket con mas filas parezca peor
#     solo por acumular mas errores, y agrupa ground_truth en rangos en vez de
#     usar cada valor exacto como categoria del eje)
# ---------------------------------------------------------------------------
tab3 = (
    df.groupby(["Rango_GT", "modelo"])["error_abs"].mean()
    .unstack("modelo").reindex(ORDEN_RANGOS)
)
grafico_lineas(tab3, ORDEN_RANGOS, "Promedio de error_abs por Rango_GT y modelo",
               "Promedio de error_abs", "3_promedio_error_abs_por_rango_gt.png")

# ---------------------------------------------------------------------------
# 8. GRAFICO 4 - % de acierto_exacto por Rango_GT y modelo
#    (version corregida de "Recuento de acierto_exacto y Recuento de modelo por
#     ground_truth": reemplaza el eje ground_truth crudo (desparejo) y el
#     doble eje Recuento/Recuento por un solo % de acierto por rango)
# ---------------------------------------------------------------------------
tab4 = (
    df.groupby(["Rango_GT", "modelo"])["acierto_exacto"].mean() * 100
).unstack("modelo").reindex(ORDEN_RANGOS)
grafico_lineas(tab4, ORDEN_RANGOS, "% de acierto_exacto por Rango_GT y modelo",
               "% acierto_exacto", "4_pct_acierto_por_rango_gt.png")

# ---------------------------------------------------------------------------
# 9. n por celda, para que sepas cuanto pesa cada punto de los graficos 3 y 4
# ---------------------------------------------------------------------------
n_celda = df.groupby(["Rango_GT", "modelo"]).size().unstack("modelo").reindex(ORDEN_RANGOS)
print("\nn por Rango_GT y modelo (para leer los graficos 3 y 4 con contexto):")
print(n_celda)

# ---------------------------------------------------------------------------
# 10. GRAFICO 5 - RMSE por modelo e issimple
#     RMSE = raiz( promedio( error_abs^2 ) ). Comparalo con el grafico 1 (Suma
#     de error_abs): si un modelo tiene RMSE muy por encima de su MAE
#     (= Suma/n), es señal de que tiene algunos errores puntuales grandes,
#     no un error moderado y consistente en todas las preguntas.
# ---------------------------------------------------------------------------
tab5 = (
    df.groupby(["modelo", "issimple"])["error_abs"]
    .apply(lambda s: np.sqrt((s ** 2).mean()))
    .unstack("issimple").reindex(ORDEN_MODELOS)
)

fig, ax = plt.subplots(figsize=(6, 4))
tab5.reindex(columns=[False, True]).plot(kind="bar", ax=ax, color=["#FF7A45", "#4EA8FF"], width=0.7)
ax.set_title("RMSE por modelo e issimple")
ax.set_ylabel("RMSE")
ax.legend(title="issimple", labels=["False (compleja)", "True (simple)"])
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(OUT_DIR / "5_rmse_por_modelo_issimple.png", dpi=150)
plt.close()

# ---------------------------------------------------------------------------
# 11. Tabla resumen accuracy% + RMSE por modelo e issimple, en el mismo
#     formato que la Tabla 3 del paper de TallyQA (ACC, RMSE lado a lado)
# ---------------------------------------------------------------------------
resumen = pd.DataFrame({
    "accuracy_simple_%":  (df[df["issimple"]].groupby("modelo")["acierto_exacto"].mean() * 100),
    "rmse_simple":         df[df["issimple"]].groupby("modelo")["error_abs"].apply(lambda s: np.sqrt((s**2).mean())),
    "accuracy_compleja_%": (df[~df["issimple"]].groupby("modelo")["acierto_exacto"].mean() * 100),
    "rmse_compleja":       df[~df["issimple"]].groupby("modelo")["error_abs"].apply(lambda s: np.sqrt((s**2).mean())),
}).reindex(ORDEN_MODELOS)

print("\nResumen accuracy% + RMSE por modelo (mismo formato que Tabla 3 del paper de TallyQA):")
print(resumen.round(2))

print(f"\nListo. Los 5 graficos quedaron en: {OUT_DIR}")
