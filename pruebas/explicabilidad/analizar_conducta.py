"""Análisis de la corrida 01 (oclusión + grounding de moondream2). CPU, sin modelo.

Uso (desde pruebas/explicabilidad/, después de correr preparar_conjunto.py):
    python analizar_conducta.py

Lee conjunto_v2/ y resultados/01_conducta/; escribe resultados/01_conducta/analisis/.
Las reglas están en DISENO.md (secciones 5 y 6).
"""
import json
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd

from explicabilidad_utils import clasificar_error

AQUI = Path(__file__).resolve().parent
CONJUNTO = AQUI / "conjunto_v2"
RESULTADOS = AQUI / "resultados" / "01_conducta"
SALIDA = RESULTADOS / "analisis"
SEMILLA = 2026
POR_GRUPO = 5
FAVORITOS = {10, 100}
RADIO_PUNTO = 0.75  # un punto pertenece a la figura más cercana si está a menos de 0,75 × su lado del centro


def wilson(k, n, z=1.96):
    """IC 95 % de Wilson para una proporción k/n, en %."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margen = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return round(100 * (centro - margen), 1), round(100 * (centro + margen), 1)


def pct(serie):
    k, n = int(serie.sum()), int(serie.count())
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.1f} % [{lo}–{hi}] (n={n})"


def categoria_oclusion(f):
    d1, d2 = f["c1"] - f["c0"], f["c2"] - f["c0"]
    if d1 == -1 and d2 == -2:
        return "cuenta"
    if d1 == 0 and d2 == 0:
        return "no_reacciona"
    if d2 < 0 and d2 <= d1 <= 0:
        return "direccion_correcta"
    return "otra"


def grounding(p, puntos, objetos):
    """Asigna cada punto a la figura más cercana y mide aciertos sobre las figuras objetivo."""
    clave = "forma" if p["tipo"] == "conteo_forma" else "color"
    objetivo = {i for i, o in enumerate(objetos) if o[clave] == p["objetivo"]}
    centros = np.array([[o["x"] + o["tamano"] / 2, o["y"] + o["tamano"] / 2] for o in objetos])
    lado = objetos[0]["tamano"]
    en_objetivo, en_otra, en_fondo, tocadas = 0, 0, 0, set()
    for pt in puntos:
        xy = np.array([pt["x"] * 1024, pt["y"] * 1024])
        dist = np.linalg.norm(centros - xy, axis=1)
        i = int(dist.argmin())
        if dist[i] > RADIO_PUNTO * lado:
            en_fondo += 1
        elif i in objetivo:
            en_objetivo += 1
            tocadas.add(i)
        else:
            en_otra += 1
    n = len(puntos)
    return dict(n_puntos=n, puntos_en_objetivo=en_objetivo, puntos_en_otra=en_otra, puntos_en_fondo=en_fondo,
                objetivos_encontrados=len(tocadas),
                precision_point=en_objetivo / n if n else math.nan,
                cobertura_point=len(tocadas) / len(objetivo))


def muestra_mapas(tabla):
    """5 por grupo, con semilla; si un grupo no alcanza, lo que falta se reparte en orden acierto → cercano → lejano."""
    rng = random.Random(SEMILLA)
    grupos = {g: sorted(tabla.index[tabla["grupo"] == g]) for g in ["acierto", "cercano", "lejano", "invalido"]}
    for g in grupos:
        rng.shuffle(grupos[g])
    cupo = {g: min(POR_GRUPO, len(v)) for g, v in grupos.items()}
    faltan = 4 * POR_GRUPO - sum(cupo.values())
    while faltan > 0:
        for g in ["acierto", "cercano", "lejano"]:
            if faltan and cupo[g] < len(grupos[g]):
                cupo[g] += 1
                faltan -= 1
    return [(qid, g, k + 1) for g, v in grupos.items() for k, qid in enumerate(v[:cupo[g]])]


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    preg = pd.read_csv(CONJUNTO / "preguntas.csv").set_index("qid")
    objetos = json.load(open(CONJUNTO / "objetos.json", encoding="utf-8"))
    resp = pd.read_csv(RESULTADOS / "respuestas.csv", dtype={"respuesta_cruda": str}, keep_default_na=False)
    resp["prediccion"] = pd.to_numeric(resp["prediccion"], errors="coerce")
    puntos = pd.read_csv(RESULTADOS / "puntos.csv").set_index("qid")

    t = resp.pivot(index="qid", columns="condicion", values="prediccion")
    t = preg[["num_shapes", "tipo", "objetivo", "gt"]].join(t)
    t["error_c0"] = t["c0"] - t["gt"]
    t["grupo"] = [clasificar_error(None if pd.isna(p) else int(p), g) for p, g in zip(t["c0"], t["gt"])]
    t["numero_favorito"] = t["c0"].isin(FAVORITOS)
    t["delta_c1"] = t["c1"] - t["c0"]
    t["delta_c2"] = t["c2"] - t["c0"]
    t["delta_control"] = t["control"] - t["c0"]
    t["oclusion"] = t.apply(categoria_oclusion, axis=1)
    t["control_estable"] = t["delta_control"] == 0
    # pendiente: ajuste lineal de la predicción contra figuras borradas (0, 1, 2)
    t["pendiente"] = [np.polyfit([0, 1, 2], [a, b, c], 1)[0] for a, b, c in zip(t["c0"], t["c1"], t["c2"])]
    g = pd.DataFrame([grounding(preg.loc[q], json.loads(puntos.loc[q, "puntos_json"]), objetos[q]) for q in t.index],
                     index=t.index)
    t = t.join(g)
    t.to_csv(SALIDA / "por_pregunta.csv")

    lineas = ["# Resultados de conducta (oclusión + grounding), moondream2", "",
              "120 preguntas, 480 consultas. IC 95 % de Wilson entre corchetes.",
              "Determinismo: 10/10 respuestas idénticas al repetir (verificado en Colab; info_corrida.json registra 0 por un error de la celda de verificación, ya corregido).", ""]
    def sec(titulo): lineas.extend(["", f"## {titulo}", ""])

    sec("Respuesta en la imagen original (c0)")
    lineas += [f"- Acierto exacto: {pct(t['grupo'] == 'acierto')}",
               f"- Error medio (predicción − correcta): {t['error_c0'].mean():.2f}; mediana {t['error_c0'].median():.0f}",
               f"- Cuenta de menos: {pct(t['error_c0'] < 0)}; cuenta de más: {pct(t['error_c0'] > 0)}",
               f"- Grupos: " + ", ".join(f"{k} {v}" for k, v in t['grupo'].value_counts().items()),
               f"- Número favorito (10 o 100, fijado en DISENO.md): {int(t['numero_favorito'].sum())}",
               f"- Repertorio de respuestas en c0: " + ", ".join(f"{int(k)}×{v}" for k, v in t['c0'].value_counts().sort_index().items()),
               f"- Respuesta máxima en c0: {int(t['c0'].max())} (GT máxima {int(t['gt'].max())})",
               f"- Pendiente de la respuesta contra la respuesta correcta: {np.polyfit(t['gt'], t['c0'], 1)[0]:.2f} (1 = escala correcta)",
               "", "Respuesta en c0 (columnas) según respuesta correcta (filas):", "",
               pd.crosstab(t["gt"], t["c0"]).to_markdown()]

    sec("Oclusión")
    lineas += [f"- Δ1 = −1 (borrar 1 objetivo baja 1): {pct(t['delta_c1'] == -1)}",
               f"- Δ2 = −2 (borrar 2 objetivos baja 2): {pct(t['delta_c2'] == -2)}",
               f"- Control estable (borrar 1 no objetivo no cambia): {pct(t['control_estable'])}",
               f"- La respuesta cambia al borrar 1 objetivo: {pct(t['delta_c1'] != 0)}; al borrar 1 no objetivo: {pct(t['delta_control'] != 0)}",
               f"- Pendiente media: {t['pendiente'].mean():.2f} (ideal −1; 0 = no reacciona)",
               "- Categorías: " + ", ".join(f"{k} {v}" for k, v in t['oclusion'].value_counts().items())]
    for col, nombre in [("num_shapes", "nivel"), ("tipo", "tipo"), ("grupo", "grupo")]:
        tab = t.groupby(col).agg(n=("c0", "size"), cuenta=("oclusion", lambda s: (s == "cuenta").mean() * 100),
                                 no_reacciona=("oclusion", lambda s: (s == "no_reacciona").mean() * 100),
                                 pendiente=("pendiente", "mean"), control_estable=("control_estable", "mean"),
                                 acierto_c0=("grupo", lambda s: (s == "acierto").mean() * 100))
        tab["control_estable"] *= 100
        lineas += ["", f"Por {nombre}:", "", tab.round(1).to_markdown()]

    sec("Grounding (point en c0)")
    lineas += [f"- Puntos por pregunta: media {t['n_puntos'].mean():.2f}; GT media {t['gt'].mean():.2f}; predicción c0 media {t['c0'].mean():.2f}",
               f"- n.º de puntos = GT: {pct(t['n_puntos'] == t['gt'])}",
               f"- n.º de puntos = respuesta de query: {pct(t['n_puntos'] == t['c0'])}",
               f"- Precisión (puntos sobre una figura objetivo): {t['puntos_en_objetivo'].sum() / t['n_puntos'].sum() * 100:.1f} % de {int(t['n_puntos'].sum())} puntos",
               f"- Puntos sobre figura no objetivo: {t['puntos_en_otra'].sum()}; sobre fondo: {t['puntos_en_fondo'].sum()}",
               f"- Cobertura (figuras objetivo encontradas): {t['objetivos_encontrados'].sum() / t['gt'].sum() * 100:.1f} % de {int(t['gt'].sum())}",
               f"- Preguntas sin ningún punto: {int((t['n_puntos'] == 0).sum())}; con 100 puntos (salida degenerada, tope de max_objects): {int((t['n_puntos'] >= 100).sum())}",
               f"- Figuras objetivo encontradas = GT: {pct(t['objetivos_encontrados'] == t['gt'])} (query acierta {pct(t['grupo'] == 'acierto')})",
               f"- Error medio: figuras objetivo encontradas − GT = {(t['objetivos_encontrados'] - t['gt']).mean():.2f}; query − GT = {t['error_c0'].mean():.2f}"]
    tab = t.groupby("tipo")[["gt", "n_puntos", "c0", "precision_point", "cobertura_point"]].mean().round(2)
    lineas += ["", tab.to_markdown()]

    sec("Muestra para los mapas (rollout y Grad-CAM)")
    m = pd.DataFrame(muestra_mapas(t), columns=["qid", "grupo", "orden_en_grupo"]).set_index("qid")
    m = m.join(t[["num_shapes", "tipo", "objetivo", "gt", "c0"]]).join(preg[["pregunta", "imagen_v2"]])
    m.to_csv(SALIDA / "muestra_mapas.csv")
    lineas += [m.reset_index().to_markdown(index=False)]

    (SALIDA / "resumen.md").write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
