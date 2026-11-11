"""Figuras de explicabilidad para la memoria (CPU).

Uso (desde pruebas/explicabilidad/): python generar_figuras.py
Escribe resultados/figuras/fig_{oclusion,grounding,rollout,gradcam}.png.
Ejemplos elegidos por regla (DISENO.md §5): oclusión = primer caso de la categoría "cuenta";
grounding y Grad-CAM = primer caso de cada grupo de la muestra (q002 acierto, q099 lejano).
"""
import csv
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, PowerNorm, TwoSlopeNorm
from matplotlib.patches import Rectangle
from PIL import Image

AQUI = Path(__file__).resolve().parent
CONJ = AQUI / "conjunto_v2"
RES = AQUI / "resultados"
SAL = RES / "figuras"
LADO = 27
AZUL, NARANJO, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA2, GRILLA = "#0b0b0b", "#52514e", "#e4e3df"
SECUENCIAL = LinearSegmentedColormap.from_list("azul", ["#f4f8fd", "#9cc3ef", "#2a78d6", "#0d3a73"])
DIVERGENTE = LinearSegmentedColormap.from_list("div", [NARANJO, "#f2f1ee", AZUL])

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": TINTA2,
                     "axes.labelcolor": TINTA, "xtick.color": TINTA2, "ytick.color": TINTA2,
                     "axes.titlesize": 9, "axes.titlecolor": TINTA, "figure.dpi": 100})

preg = {p["qid"]: p for p in csv.DictReader(open(CONJ / "preguntas.csv", encoding="utf-8"))}
objetos = json.load(open(CONJ / "objetos.json", encoding="utf-8"))
cond = pd.read_csv(RES / "01_conducta" / "analisis" / "por_pregunta.csv", index_col=0)
puntos = pd.read_csv(RES / "01_conducta" / "puntos.csv").set_index("qid")


def es_objetivo(q, o):
    p = preg[q]
    return o["forma" if p["tipo"] == "conteo_forma" else "color"] == p["objetivo"]


def imagen(q, c="c0"):
    return np.asarray(Image.open(CONJ / "imagenes" / f"{q}_{c}.png").convert("RGB"))


def contornos(ax, q, escala=1.0, solo_objetivo=False, lw=1.2):
    for o in objetos[q]:
        obj = es_objetivo(q, o)
        if solo_objetivo and not obj:
            continue
        ax.add_patch(Rectangle((o["x"] * escala - 0.5, o["y"] * escala - 0.5), o["tamano"] * escala, o["tamano"] * escala,
                               fill=False, ec=TINTA if obj else TINTA2, lw=lw if obj else 0.5, alpha=1 if obj else 0.6))


def marca_borrada(ax, q, cual, escala=1.0, color=NARANJO):
    o = objetos[q][cual]
    cx, cy = (o["x"] + o["tamano"] / 2) * escala, (o["y"] + o["tamano"] / 2) * escala
    ax.add_patch(plt.Circle((cx, cy), o["tamano"] * 1.1 * escala, fill=False, ec=color, lw=1.6, ls="--"))


def limpiar(ax):
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(GRILLA)


def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return 100 * p, 100 * (c - m), 100 * (c + m)


def fig_oclusion(q="q004"):
    p, fila = preg[q], cond.loc[q]
    fig = plt.figure(figsize=(6.6, 5.9))
    gs = fig.add_gridspec(2, 4, height_ratios=[1, 1.25], hspace=0.38, wspace=0.12)
    titulos = {"c0": "Original", "c1": "Sin 1 objetivo", "c2": "Sin 2 objetivos", "control": "Sin 1 no objetivo"}
    borradas = {"c1": [int(p["borrada_c1"])], "c2": [int(x) for x in p["borradas_c2"].split(";")],
                "control": [int(p["borrada_control"])]}
    gt = {"c0": fila["gt"], "c1": fila["gt"] - 1, "c2": fila["gt"] - 2, "control": fila["gt"]}
    for k, c in enumerate(titulos):
        ax = fig.add_subplot(gs[0, k])
        ax.imshow(imagen(q, c))
        for b in borradas.get(c, []):
            marca_borrada(ax, q, b, color=NARANJO if c == "control" else AZUL)
        ax.set_title(titulos[c], pad=3)
        ax.set_xlabel(f"correcta {int(gt[c])}\nresponde {int(fila[c])}", color=TINTA, fontsize=8)
        limpiar(ax)
    fig.text(0.12, 0.885, f"A. Ejemplo ({q}): \"{p['pregunta']}\"", ha="left", fontsize=9, color=TINTA, weight="bold")

    sub = gs[1, :].subgridspec(1, 2, wspace=0.35, width_ratios=[1.15, 1])
    ax = fig.add_subplot(sub[0])
    tabla = pd.crosstab(cond["gt"], cond["c0"]).reindex(index=range(2, 11), columns=range(0, 11), fill_value=0)
    ax.imshow(tabla.values, cmap=SECUENCIAL, aspect="auto", origin="lower")
    for i, g in enumerate(tabla.index):
        for j, r in enumerate(tabla.columns):
            v = tabla.loc[g, r]
            if v:
                ax.text(j, i, v, ha="center", va="center", fontsize=7, color="white" if v > 6 else TINTA)
        ax.add_patch(Rectangle((g - 0.5, i - 0.5), 1, 1, fill=False, ec=NARANJO, lw=1.2))
    ax.set_xticks(range(0, 11)); ax.set_yticks(range(9)); ax.set_yticklabels(range(2, 11))
    ax.set_xlabel("Respuesta del modelo (imagen original)"); ax.set_ylabel("Respuesta correcta")
    ax.set_title("B. Respuesta vs. correcta (n = 120)", loc="left", weight="bold")
    ax.text(10.3, -0.3, "recuadro naranjo = acierto", ha="right", va="bottom", fontsize=7, color=NARANJO)

    ax = fig.add_subplot(sub[1])
    datos = [("Borrar 1 figura\nobjetivo", (cond["delta_c1"] != 0).sum(), AZUL),
             ("Borrar 1 figura\nno objetivo", (cond["delta_control"] != 0).sum(), NARANJO)]
    for i, (et, k, col) in enumerate(datos):
        v, lo, hi = wilson(k, len(cond))
        ax.barh(i, v, color=col, height=0.5)
        ax.errorbar(v, i, xerr=[[v - lo], [hi - v]], color=TINTA, capsize=3, lw=1)
        ax.text(hi + 2, i, f"{v:.1f} %", va="center", color=TINTA)
        ax.text(0.5, i - 0.36, et.replace("\n", " "), va="bottom", color=TINTA, fontsize=8)
    ax.set_yticks([]); ax.set_ylim(1.6, -0.75)
    ax.set_xlim(0, 70); ax.set_xlabel("% de preguntas (IC 95 %)")
    ax.grid(axis="x", color=GRILLA, lw=0.6); ax.set_axisbelow(True)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.set_title("C. La respuesta cambia al borrar", loc="left", weight="bold")
    fig.savefig(SAL / "fig_oclusion.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_grounding(q="q099"):
    p, fila = preg[q], cond.loc[q]
    pts = json.loads(puntos.loc[q, "puntos_json"])
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(6.6, 3.2), gridspec_kw=dict(width_ratios=[1, 1.25], wspace=0.28))
    ax.imshow(imagen(q))
    contornos(ax, q, solo_objetivo=True)
    xs = [pt["x"] * 1024 for pt in pts]; ys = [pt["y"] * 1024 for pt in pts]
    ax.scatter(xs, ys, s=28, c=AZUL, edgecolors="white", linewidths=1.2, zorder=3)
    ax.set_title(f"A. Ejemplo ({q})", loc="left", fontsize=8.5, weight="bold")
    ax.set_xlabel(f"\"{p['pregunta']}\"\ncorrecta {int(fila['gt'])} · puntos sobre objetivo {int(fila['puntos_en_objetivo'])} · responde {int(fila['c0'])}",
                  color=TINTA, fontsize=7.5)
    limpiar(ax)

    g = cond.groupby("gt")[["c0", "objetivos_encontrados"]].mean()
    ax2.plot([2, 10], [2, 10], ls="--", color=TINTA2, lw=1)
    ax2.text(8.6, 9.3, "ideal", ha="right", color=TINTA2, fontsize=7.5)
    ax2.plot(g.index, g["objetivos_encontrados"], marker="o", ms=4, lw=2, color=AQUA)
    ax2.plot(g.index, g["c0"], marker="o", ms=4, lw=2, color=AZUL)
    ax2.text(10.15, g["objetivos_encontrados"].iloc[-1], "figuras objetivo\nseñaladas (point)", va="center", fontsize=7.5, color=TINTA)
    ax2.text(10.15, g["c0"].iloc[-1] - 0.4, "respuesta\n(query)", va="center", fontsize=7.5, color=TINTA)
    ax2.set_xlim(1.6, 12.6); ax2.set_ylim(0, 10.5); ax2.set_xticks(range(2, 11))
    ax2.set_xlabel("Respuesta correcta"); ax2.set_ylabel("Promedio")
    ax2.grid(color=GRILLA, lw=0.6); ax2.set_axisbelow(True)
    for s in ["top", "right"]:
        ax2.spines[s].set_visible(False)
    ax2.set_title("B. Señala más figuras de las que dice (n = 120)", loc="left", fontsize=8.5, weight="bold")
    fig.savefig(SAL / "fig_grounding.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_rollout(q="q002"):
    z = np.load(RES / "02_rollout" / "mapas_rollout.npz")
    gris = z["gris_recibido"]
    sinks = np.argsort(gris)[::-1][:5]
    fig, axs = plt.subplots(1, 3, figsize=(6.6, 2.6), gridspec_kw=dict(wspace=0.08))
    for ax, (ident, titulo) in zip(axs, [(q, f"Imagen de la muestra ({q})"), ("gris", "Imagen gris (sin figuras)"),
                                          ("ruido", "Ruido")]):
        m = z[f"{ident}_recibido"].reshape(LADO, LADO)
        ax.imshow(m / m.max(), cmap=SECUENCIAL, norm=PowerNorm(0.5, 0, 1), interpolation="nearest")
        if ident == q:
            contornos(ax, q, escala=LADO / 1024, lw=0.8)
        for s in sinks:
            ax.add_patch(Rectangle((s % LADO - 0.5, s // LADO - 0.5), 1, 1, fill=False, ec=NARANJO, lw=1.4))
        ax.set_title(titulo); limpiar(ax)
    fig.savefig(SAL / "fig_rollout.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig_gradcam(casos=("q002", "q099")):
    z = np.load(RES / "03_gradcam" / "mapas_gradcam.npz")
    t = pd.read_csv(RES / "03_gradcam" / "analisis" / "por_imagen.csv", index_col=0)
    fig = plt.figure(figsize=(6.6, 7.2))
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1.05], hspace=0.45, wspace=0.08)
    for r, q in enumerate(casos):
        fila = cond.loc[q]
        ax = fig.add_subplot(gs[r, 0]); ax.imshow(imagen(q)); contornos(ax, q, solo_objetivo=True)
        marca_borrada(ax, q, int(preg[q]["borrada_c1"]), color=NARANJO)
        cambio = "cambia" if fila["delta_c1"] != 0 else "no cambia"
        ax.set_title(f"{q}: correcta {int(fila['gt'])}, responde {int(fila['c0'])}", fontsize=8)
        ax.set_xlabel(f"al borrar la figura marcada, {cambio}", fontsize=7.5, color=TINTA); limpiar(ax)
        m = z[f"{q}_gradcam_llm"].reshape(LADO, LADO)
        ax = fig.add_subplot(gs[r, 1]); ax.imshow(m, cmap=SECUENCIAL, interpolation="nearest")
        contornos(ax, q, escala=LADO / 1024, lw=0.9); limpiar(ax)
        if r == 0: ax.set_title("Grad-CAM")
        g = z[f"{q}_gxi_llm"].reshape(LADO, LADO)
        lim = np.percentile(np.abs(g), 99)
        ax = fig.add_subplot(gs[r, 2]); ax.imshow(g, cmap=DIVERGENTE, norm=TwoSlopeNorm(0, -lim, lim), interpolation="nearest")
        contornos(ax, q, escala=LADO / 1024, lw=0.9); limpiar(ax)
        if r == 0: ax.set_title("Gradiente × entrada")
    ax = fig.add_subplot(gs[2, :])
    orden = t.sort_values("gxi_objetivo").index
    y = np.arange(len(orden))
    for i, q in enumerate(orden):
        ax.plot([t.loc[q, "gxi_otras"], t.loc[q, "gxi_objetivo"]], [i, i], color=GRILLA, lw=1.5, zorder=1)
    ax.scatter(t.loc[orden, "gxi_otras"], y, s=22, color=NARANJO, zorder=2, label="otras figuras")
    ax.scatter(t.loc[orden, "gxi_objetivo"], y, s=22, color=AZUL, zorder=3, label="figuras objetivo")
    ax.axvline(0, color=TINTA2, lw=0.8)
    ax.set_xlim(-0.3, 0.3); ax.set_yticks([]); ax.set_ylabel("20 preguntas\n(ordenadas)")
    ax.set_xlabel("Contribución media por token (gradiente × entrada; + empuja la respuesta hacia arriba)")
    k = int((t["gxi_objetivo"] > t["gxi_otras"]).sum())
    ax.set_title(f"Objetivo > otras figuras en {k} de 20 preguntas (prueba de signos, p = 0,04)", loc="left", weight="bold")
    ax.legend(frameon=False, loc="lower right", fontsize=7.5)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    xs_obj = t.loc[orden, "gxi_objetivo"].clip(-0.3, 0.3); xs_otr = t.loc[orden, "gxi_otras"].clip(-0.3, 0.3)
    ax.collections[0].set_offsets(np.c_[xs_otr, y]); ax.collections[1].set_offsets(np.c_[xs_obj, y])
    for line, a, b in zip(ax.lines, xs_otr, xs_obj):
        line.set_xdata([a, b])
    fig.savefig(SAL / "fig_gradcam.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    SAL.mkdir(parents=True, exist_ok=True)
    fig_oclusion(); fig_grounding(); fig_rollout(); fig_gradcam()
    print("Figuras en", SAL)
