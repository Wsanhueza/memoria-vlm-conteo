"""Uso: python <script>.py  (35 px)  ·  python <script>.py _t70  (figuras de 70 px)
Análisis de la corrida 02 (attention rollout del encoder visual de moondream2). CPU.

Uso (desde pruebas/explicabilidad/): python analizar_rollout.py
Lee conjunto_v2/ y resultados/02_rollout/; escribe resultados/02_rollout/analisis/.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
SUF = sys.argv[1] if len(sys.argv) > 1 else ""  # "" = figuras de 35 px (original); "_t70" = 70 px
CONJUNTO = AQUI / ("conjunto_v2" if SUF == "" else f"conjunto{SUF}")
RES = AQUI / "resultados" / f"02_rollout{SUF}"
SALIDA = RES / "analisis"
LADO = 27  # tokens por lado del recorte global (378 px / parche de 14 px)


def fraccion_por_token(mascara):
    """Fracción de cada token (27 x 27) cubierta por la máscara 1024 x 1024 (la vista global es la imagen entera)."""
    bordes = np.linspace(0, mascara.shape[0], LADO + 1).round().astype(int)
    f = np.zeros((LADO, LADO))
    for i in range(LADO):
        for j in range(LADO):
            f[i, j] = mascara[bordes[i]:bordes[i + 1], bordes[j]:bordes[j + 1]].mean()
    return f.ravel()


def enriquecimiento(mapa, fraccion, quitar=()):
    """(masa del mapa sobre la máscara) / (área de la máscara), sobre los tokens que quedan. 1 = no distingue."""
    m = mapa.astype(float).copy()
    f = fraccion.copy()
    keep = np.ones(len(m), bool)
    keep[list(quitar)] = False
    m, f = m[keep], f[keep]
    m = m / m.sum()
    area = f.sum() / len(f)
    return float((m * f).sum() / area) if area > 0 else np.nan


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    z = np.load(RES / "mapas_rollout.npz")
    preg = {p["qid"]: p for p in csv.DictReader(open(CONJUNTO / "preguntas.csv", encoding="utf-8"))}
    objetos = json.load(open(CONJUNTO / "objetos.json", encoding="utf-8"))
    resumen = pd.read_csv(RES / "resumen.csv")
    ids = list(resumen["id"])
    muestra = [i for i in ids if i in preg]

    gris = z["gris_recibido"]
    # tokens "sumidero": los 5 de mayor rollout y los 4 de mayor norma en la imagen gris
    sinks_rollout = np.argsort(gris)[::-1][:5]
    sinks_norma = np.argsort(z["gris_normas"].astype(float)[-1])[::-1][:4]
    sinks = sorted(set(sinks_rollout) | set(sinks_norma))

    filas = []
    for q in muestra:
        mapa = z[f"{q}_recibido"]
        etiquetas = np.load(CONJUNTO / "etiquetas" / f"{q}.npz")["etiquetas"]
        p = preg[q]
        clave = "forma" if p["tipo"] == "conteo_forma" else "color"
        idx_obj = [i + 1 for i, o in enumerate(objetos[q]) if o[clave] == p["objetivo"]]
        f_obj = fraccion_por_token(np.isin(etiquetas, idx_obj))
        f_fig = fraccion_por_token(etiquetas > 0)
        sin_sinks = np.delete(mapa, sinks)
        filas.append(dict(
            qid=q, grupo=resumen.set_index("id").loc[q, "grupo"], num_shapes=int(p["num_shapes"]), tipo=p["tipo"],
            masa_en_sinks_pct=round(100 * mapa[sinks].sum() / mapa.sum(), 2),
            corr_con_gris=round(float(np.corrcoef(mapa, gris)[0, 1]), 4),
            corr_con_gris_sin_sinks=round(float(np.corrcoef(sin_sinks, np.delete(gris, sinks))[0, 1]), 4),
            enriq_figuras=round(enriquecimiento(mapa, f_fig), 3),
            enriq_objetivo=round(enriquecimiento(mapa, f_obj), 3),
            enriq_figuras_sin_sinks=round(enriquecimiento(mapa, f_fig, sinks), 3),
            enriq_objetivo_sin_sinks=round(enriquecimiento(mapa, f_obj, sinks), 3),
            area_figuras_pct=round(100 * f_fig.mean(), 2), area_objetivo_pct=round(100 * f_obj.mean(), 2)))
    t = pd.DataFrame(filas).set_index("qid")
    t.to_csv(SALIDA / "por_imagen.csv")

    a_rc = lambda k: f"fila {k // LADO}, col {k % LADO}"
    ruido = z["ruido_recibido"]
    lineas = [
        "# Attention rollout del encoder visual de moondream2: resultados", "",
        "20 imágenes de la muestra + 2 controles (gris, ruido). Verificación de la reimplementación: diferencia máxima 0, coseno mínimo 0,9999996.", "",
        "## Tokens sumidero", "",
        "- Top-5 del rollout en la imagen gris: " + "; ".join(f"{k} ({a_rc(k)})" for k in sinks_rollout),
        "- Top-4 de norma en la imagen gris: " + "; ".join(f"{k} ({a_rc(k)})" for k in sinks_norma),
        f"- Masa del rollout en esos {len(sinks)} tokens ({100 * len(sinks) / LADO**2:.1f} % de los tokens): "
        f"media {t['masa_en_sinks_pct'].mean():.1f} % en la muestra; {100 * gris[sinks].sum() / gris.sum():.1f} % en gris; {100 * ruido[sinks].sum() / ruido.sum():.1f} % en ruido",
        f"- Correlación de cada mapa con el de la imagen gris: media {t['corr_con_gris'].mean():.3f} (mín {t['corr_con_gris'].min():.3f})",
        f"- La misma correlación quitando los sumideros: media {t['corr_con_gris_sin_sinks'].mean():.3f} (mín {t['corr_con_gris_sin_sinks'].min():.3f})",
        "", "## ¿El mapa distingue las figuras? (enriquecimiento; 1 = igual que el fondo)", "",
        f"- Todas las figuras: {t['enriq_figuras'].mean():.2f} (sin sumideros {t['enriq_figuras_sin_sinks'].mean():.2f})",
        f"- Figuras objetivo: {t['enriq_objetivo'].mean():.2f} (sin sumideros {t['enriq_objetivo_sin_sinks'].mean():.2f})",
        f"- Área media cubierta: figuras {t['area_figuras_pct'].mean():.1f} %, objetivo {t['area_objetivo_pct'].mean():.1f} %",
        "", "Por grupo:", "",
        t.groupby("grupo")[["enriq_figuras", "enriq_objetivo", "enriq_figuras_sin_sinks", "enriq_objetivo_sin_sinks", "corr_con_gris"]].mean().round(3).to_markdown(),
        "", "Por imagen:", "", t.to_markdown()]
    (SALIDA / "resumen.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas[:22]))


if __name__ == "__main__":
    main()
