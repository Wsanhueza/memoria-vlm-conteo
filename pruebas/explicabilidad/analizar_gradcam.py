"""Uso: python <script>.py  (35 px)  ·  python <script>.py _t70  (figuras de 70 px)
Análisis de la corrida 03 (Grad-CAM de moondream2) y cruce con la oclusión. CPU.

Uso (desde pruebas/explicabilidad/): python analizar_gradcam.py
Lee conjunto_v2/, resultados/01_conducta/analisis/por_pregunta.csv y resultados/03_gradcam/;
escribe resultados/03_gradcam/analisis/.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from analizar_rollout import LADO, enriquecimiento, fraccion_por_token

AQUI = Path(__file__).resolve().parent
SUF = sys.argv[1] if len(sys.argv) > 1 else ""  # "" = figuras de 35 px (original); "_t70" = 70 px
CONJUNTO = AQUI / ("conjunto_v2" if SUF == "" else f"conjunto{SUF}")
RES = AQUI / "resultados" / f"03_gradcam{SUF}"
SALIDA = RES / "analisis"
MAPAS = ["gradcam_llm", "gradcam_enc"]


def token_de_figura(obj):
    """Token (0..728) donde cae el centro de una figura en la grilla 27 x 27."""
    cx, cy = obj["x"] + obj["tamano"] / 2, obj["y"] + obj["tamano"] / 2
    return int(cy * LADO // 1024) * LADO + int(cx * LADO // 1024)


def percentil(mapa, i):
    """Percentil (0-100) del valor del token i dentro del mapa."""
    return float((mapa < mapa[i]).mean() * 100)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    z = np.load(RES / "mapas_gradcam.npz")
    preg = {p["qid"]: p for p in csv.DictReader(open(CONJUNTO / "preguntas.csv", encoding="utf-8"))}
    objetos = json.load(open(CONJUNTO / "objetos.json", encoding="utf-8"))
    cond = pd.read_csv(AQUI / "resultados" / f"01_conducta{SUF}" / "analisis" / "por_pregunta.csv", index_col=0)
    resumen = pd.read_csv(RES / "resumen.csv").set_index("id")
    muestra = [i for i in resumen.index if i in preg]

    filas = []
    for q in muestra:
        p, objs = preg[q], objetos[q]
        etiquetas = np.load(CONJUNTO / "etiquetas" / f"{q}.npz")["etiquetas"]
        clave = "forma" if p["tipo"] == "conteo_forma" else "color"
        idx_obj = [i + 1 for i, o in enumerate(objs) if o[clave] == p["objetivo"]]
        idx_otro = [i + 1 for i, o in enumerate(objs) if o[clave] != p["objetivo"]]
        f_obj = fraccion_por_token(np.isin(etiquetas, idx_obj))
        f_otro = fraccion_por_token(np.isin(etiquetas, idx_otro))
        f_fondo = fraccion_por_token(etiquetas == 0)
        fila = dict(qid=q, grupo=resumen.loc[q, "grupo"], num_shapes=int(p["num_shapes"]), tipo=p["tipo"],
                    prediccion=resumen.loc[q, "prediccion"], gt=int(p["gt"]),
                    delta_c1=cond.loc[q, "delta_c1"], delta_control=cond.loc[q, "delta_control"])
        for m in MAPAS:
            mapa = z[f"{q}_{m}"].astype(float)
            fila[f"{m}_enriq_objetivo"] = round(enriquecimiento(mapa, f_obj), 3)
            fila[f"{m}_enriq_otras"] = round(enriquecimiento(mapa, f_otro), 3)
            fila[f"{m}_enriq_fondo"] = round(enriquecimiento(mapa, f_fondo), 3)
            # figuras borradas en la oclusión: ¿qué tan "pintadas" estaban?
            fila[f"{m}_pct_borrada_c1"] = round(percentil(mapa, token_de_figura(objs[int(p["borrada_c1"])])), 1)
            fila[f"{m}_pct_borrada_control"] = round(percentil(mapa, token_de_figura(objs[int(p["borrada_control"])])), 1)
        gxi = z[f"{q}_gxi_llm"].astype(float)
        w = lambda f: float((gxi * f).sum() / f.sum())  # contribución media por token cubierto (con signo)
        fila["gxi_objetivo"], fila["gxi_otras"], fila["gxi_fondo"] = w(f_obj), w(f_otro), w(f_fondo)
        filas.append(fila)
    t = pd.DataFrame(filas).set_index("qid")
    t.to_csv(SALIDA / "por_imagen.csv")

    def prom(col): return f"{t[col].mean():.2f} (mediana {t[col].median():.2f})"
    lineas = ["# Grad-CAM de moondream2: resultados y cruce con la oclusión", "",
              "20 preguntas de la muestra + 2 controles. Verificación: la pasada con gradientes elige el mismo número que query() (5/5).",
              "Enriquecimiento: fracción del mapa sobre la región / fracción del área que ocupa (1 = sin preferencia).", ""]
    for m in MAPAS:
        lineas += [f"## {m}", "",
                   f"- Figuras objetivo: {prom(f'{m}_enriq_objetivo')}",
                   f"- Otras figuras: {prom(f'{m}_enriq_otras')}",
                   f"- Fondo: {prom(f'{m}_enriq_fondo')}",
                   f"- Objetivo > otras figuras en {int((t[f'{m}_enriq_objetivo'] > t[f'{m}_enriq_otras']).sum())}/20 imágenes",
                   f"- Percentil del token de la figura borrada en c1: {prom(f'{m}_pct_borrada_c1')}; de la borrada en control: {prom(f'{m}_pct_borrada_control')}",
                   ""]
    lineas += ["## Grad × entrada (con signo): contribución media por token", "",
               f"- Objetivo {prom('gxi_objetivo')}; otras figuras {prom('gxi_otras')}; fondo {prom('gxi_fondo')}",
               f"- Objetivo > fondo en {int((t['gxi_objetivo'] > t['gxi_fondo']).sum())}/20; otras > fondo en {int((t['gxi_otras'] > t['gxi_fondo']).sum())}/20",
               "", "## Cruce con la oclusión (¿la respuesta cambió al borrar 1 objetivo?)", "",
               t.assign(cambio=t["delta_c1"] != 0).groupby("cambio")[[
                   "gradcam_llm_pct_borrada_c1", "gradcam_llm_enriq_objetivo", "gxi_objetivo"]].agg(["mean", "count"]).round(2).to_markdown(),
               "", "## Por grupo", "",
               t.groupby("grupo")[["gradcam_llm_enriq_objetivo", "gradcam_llm_enriq_otras", "gradcam_llm_enriq_fondo"]].mean().round(2).to_markdown(),
               "", "## Por imagen", "", t.round(2).to_markdown()]
    (SALIDA / "resumen.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas[:40]))


if __name__ == "__main__":
    main()
