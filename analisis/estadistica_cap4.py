"""Recalcula las cifras estadísticas de la memoria (ejemplos de 2.6–2.7 y Capítulo 4) desde los CSV.

No ejecuta ningún modelo ni modifica ningún archivo: solo lee los CSV de detalle y los resultados de
explicabilidad, y escribe dos archivos de salida en esta misma carpeta.

Uso (desde la raíz del repositorio):
    python analisis/estadistica_cap4.py
    python analisis/estadistica_cap4.py --capture pruebas/Conteo/capture_v2      # CAPTURe re-ejecutado
    python analisis/estadistica_cap4.py --explic _t70                              # explicabilidad a 70 px

Salida:
    analisis/estadistica_cap4_resultados.md   una fila por cifra: valor en la memoria v5, valor calculado y estado
    analisis/estadistica_cap4_resultados.csv  lo mismo en CSV
    Con --capture o --explic, los nombres llevan un sufijo (p. ej. _capture_v2) y no pisan la verificación original.

Estados:
    OK        el valor calculado, redondeado como en la memoria, coincide.
    REDONDEO  difiere en una unidad del último decimal (redondeo de un valor intermedio).
    IC-BOOT   intervalo bootstrap que difiere en menos de 1 punto: es el error de Monte Carlo del remuestreo
              (B = 5.000), que depende del orden en que se generaron los números aleatorios.
    DISTINTO  no coincide: revisar el texto o el cálculo.
Al apuntar a corridas nuevas (--capture, --explic), los DISTINTO indican qué cifras hay que actualizar en la memoria.

Requiere: pandas, numpy, scipy.
"""
import argparse
import glob
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
MODELOS = ["InternVL2-1B", "moondream2", "PaliGemma2-3B", "Qwen2-VL-2B"]
CARPETA_CONTEO = {"InternVL2-1B": "InternVL2_1B", "moondream2": "moondream2",
                  "PaliGemma2-3B": "paligemma2_3b", "Qwen2-VL-2B": "qwen2_vl_2b"}
CARPETA_OMNI = {"InternVL2-1B": "InternVL2_1B", "moondream2": "moondream2",
                "PaliGemma2-3B": "paligemma2", "Qwen2-VL-2B": "qwen2vl"}
SEMILLA = 2026


# ─────────────────────────────── Fórmulas de la memoria ───────────────────────────────

def wilson(k, n, z=1.96):
    """Intervalo de Wilson para k aciertos en n preguntas, en % (ecuación 2.13)."""
    p = k / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    semiancho = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return 100 * (centro - semiancho), 100 * (centro + semiancho)


def mcnemar_exacto(n10, n01):
    """Valor p bilateral de la prueba exacta de McNemar (ecuación 2.14): binomial con p = 1/2
    sobre las preguntas discordantes. También sirve como prueba de signos."""
    n = n10 + n01
    if n == 0:
        return 1.0
    return min(1.0, 2 * stats.binom.cdf(min(n10, n01), n, 0.5))


def smape_terminos(y, yhat):
    """Términos de la ecuación (2.4), en %: |ŷ−y| / (|y|+|ŷ|), con 0 si ambos son 0."""
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    den = np.abs(y) + np.abs(yhat)
    return 100 * np.divide(np.abs(yhat - y), den, out=np.zeros_like(den), where=den > 0)


def bootstrap_media(v, rng, B=5000):
    """IC 95 % bootstrap percentil del promedio (ecuación 2.17)."""
    v = np.asarray(v, float)
    idx = rng.integers(0, len(v), (B, len(v)))
    return tuple(np.percentile(v[idx].mean(1), [2.5, 97.5]))


def recta(x, y):
    """Recta de MCO (ecuaciones 2.15 y 2.16): pendiente, intercepto, sus IC 95 % con t de n−2 g.l., y R²."""
    r = stats.linregress(x, y)
    t = stats.t.ppf(0.975, len(x) - 2)
    return dict(b1=r.slope, b1_ic=(r.slope - t * r.stderr, r.slope + t * r.stderr),
                b0=r.intercept, b0_ic=(r.intercept - t * r.intercept_stderr, r.intercept + t * r.intercept_stderr),
                r2=r.rvalue**2)


def ic_media_t(v):
    """IC 95 % de una media con la distribución t (para la pendiente media de la oclusión)."""
    v = np.asarray(v, float)
    t = stats.t.ppf(0.975, len(v) - 1)
    se = v.std(ddof=1) / np.sqrt(len(v))
    return v.mean() - t * se, v.mean() + t * se


# ─────────────────────────────── Registro y comparación ───────────────────────────────

FILAS = []


def chequear(seccion, que, memoria, calculado, dec=1, tipo="normal"):
    """Compara un valor (o una tupla de valores) de la memoria con el calculado, redondeado a `dec` decimales."""
    mem = memoria if isinstance(memoria, (tuple, list)) else (memoria,)
    cal = calculado if isinstance(calculado, (tuple, list)) else (calculado,)
    if memoria is None:
        estado = "INFO"
    else:
        dif = max(abs(float(m) - float(c)) for m, c in zip(mem, cal))
        u = 10 ** -dec
        if dif <= u / 2 + 1e-9:
            estado = "OK"
        elif dif <= 1.5 * u + 1e-9:
            estado = "REDONDEO"
        elif tipo == "boot" and dif < 1.0:
            estado = "IC-BOOT"
        else:
            estado = "DISTINTO"
    fmt = lambda t: "; ".join(f"{float(x):.{dec}f}" if not isinstance(x, str) else x for x in t)
    FILAS.append(dict(seccion=seccion, cifra=que, memoria="—" if memoria is None else fmt(mem),
                      calculado=fmt(cal), estado=estado))


def cargar_modulo(ruta, nombre):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def un_archivo(patron):
    archivos = sorted(glob.glob(str(patron)))
    if len(archivos) != 1:
        raise FileNotFoundError(f"Se esperaba un archivo para {patron}, hay {len(archivos)}: {archivos}")
    return archivos[0]


def validas(d):
    return d[(~d["parse_fail"].astype(bool)) & (~d["timeout"].astype(bool)) & d["prediccion"].notna()]


# ─────────────────────────────── 2.6–2.7: ejemplos numéricos ───────────────────────────────

def ejemplos_cap2():
    s = "2.6.2"
    chequear(s, "Ejemplo ec. (2.5): (61·23,8 + 39·100)/100", 53.5, (61 * 23.8 + 39 * 100) / 100)
    s = "2.7.1"
    chequear(s, "Wilson con k = 0, n = 25", (0.0, 13.3), wilson(0, 25))
    chequear(s, "Semiancho de Wald, n = 100, p = 0,27 (puntos)", 8.7, 100 * 1.96 * np.sqrt(0.27 * 0.73 / 100))
    chequear(s, "Semiancho de Wald, n = 100, p = 0,5 (puntos)", 9.8, 100 * 1.96 * np.sqrt(0.25 / 100))


# ─────────────────────────────── 4.1 CAPTURe ───────────────────────────────

def capture(carpeta_capture):
    s = "4.1"
    if carpeta_capture:
        rutas = {m: un_archivo(Path(carpeta_capture) / f"detalle_CAPTURe_*{k}*.csv")
                 for m, k in zip(MODELOS, ["InternVL2-1B", "moondream2", "paligemma2-3b", "qwen2vl-2b"])}
    else:
        rutas = {m: un_archivo(RAIZ / "pruebas/Conteo" / CARPETA_CONTEO[m] / "detalle_CAPTURe_*.csv") for m in MODELOS}
    d = {m: pd.read_csv(r) for m, r in rutas.items()}

    # Validez y parse_fail
    mem_validas = {"InternVL2-1B": (100, 97), "moondream2": (95, 61), "PaliGemma2-3B": (61, 31), "Qwen2-VL-2B": (100, 99)}
    for m in MODELOS:
        v = validas(d[m])
        chequear(s, f"{m}: respuestas válidas (real; sint.)", mem_validas[m],
                 ((v.subset == "real").sum(), (v.subset == "sintetico").sum()), 0)
    pf = d["PaliGemma2-3B"]["parse_fail"].sum()
    chequear(s, "PaliGemma2-3B: parse_fail de 200 (texto: 108, 54 %)", 108, pf, 0)

    # Tabla 4, parser original: sMAPE solo válidas y con inválidas = 100 %, con IC bootstrap (ec. 2.4, 2.5, 2.17)
    mem_t4 = {  # (real válidas, IC), (real inv100, IC), (sint válidas, IC), (sint inv100, IC)
        "InternVL2-1B": [(65.0, 58.3, 71.3), (65.0, 58.4, 71.2), (65.7, 61.2, 70.1), (66.8, 62.3, 71.0)],
        "moondream2": [(38.9, 33.3, 44.8), (41.9, 35.9, 47.9), (23.8, 17.7, 30.4), (53.5, 45.3, 61.8)],
        "PaliGemma2-3B": [(43.6, 36.5, 50.9), (65.6, 58.5, 72.5), (46.1, 35.6, 57.0), (83.3, 77.3, 89.0)],
        "Qwen2-VL-2B": [(37.3, 32.0, 42.8), (37.3, 32.0, 42.7), (49.0, 42.1, 55.8), (49.5, 42.6, 56.5)],
    }
    for m in MODELOS:
        k = 0
        for sub in ["real", "sintetico"]:
            x = d[m][d[m].subset == sub]
            ok = (~x.parse_fail.astype(bool)) & (~x.timeout.astype(bool)) & x.prediccion.notna()
            t_val = smape_terminos(x.ground_truth[ok], x.prediccion[ok])
            t_all = np.where(ok, smape_terminos(x.ground_truth, x.prediccion.fillna(0)), 100.0)
            for nombre, t in [("solo válidas", t_val), ("inválidas = 100 %", t_all)]:
                mv, lo, hi = mem_t4[m][k]
                chequear(s, f"Tabla 4 · {m} · {sub} · {nombre} · sMAPE", mv, t.mean())
                chequear(s, f"Tabla 4 · {m} · {sub} · {nombre} · IC 95 %", (lo, hi),
                         bootstrap_media(t, np.random.default_rng(SEMILLA)), tipo="boot")
                k += 1

    # Tabla 4, parser estricto y constante: se reproduce exactamente reparsear_capture.py (mismo orden de remuestreo)
    rep = cargar_modulo(RAIZ / "pruebas/Conteo/reparseo_capture/reparsear_capture.py", "reparsear_capture")
    rng = np.random.default_rng(SEMILLA)
    mem_estricto = {
        "InternVL2-1B": [65, (45.4, 38.8, 51.9), (64.5, 57.9, 71.0), 27, (25.9, 19.7, 33.1), (80.0, 73.1, 86.6)],
        "moondream2": [91, (37.1, 31.5, 42.9), (42.8, 36.6, 49.2), 20, (7.9, 4.7, 11.2), (81.6, 74.3, 88.8)],
        "PaliGemma2-3B": [61, (43.6, 36.3, 50.6), (65.6, 58.6, 72.4), 6, (12.6, 6.4, 17.8), (94.8, 90.4, 98.4)],
        "Qwen2-VL-2B": [91, (31.6, 27.3, 36.1), (37.8, 32.2, 43.4), 35, (15.7, 10.9, 21.3), (70.5, 62.5, 78.7)],
    }
    # el script original recorre los archivos en orden alfabético de ruta
    orden = sorted(MODELOS, key=lambda m: rutas[m])
    for m in orden:
        x0 = d[m].copy()
        r = x0.respuesta_cruda.astype(str).map(rep.parse_estricto)
        x0["nuevo"] = [a[0] for a in r]
        for j, sub in enumerate(["real", "sintetico"]):
            x = x0[x0.subset == sub]
            ok = x.nuevo.notna()
            v_val = rep.smape(x.ground_truth[ok], x.nuevo[ok])
            v_all = np.where(ok, rep.smape(x.ground_truth, x.nuevo.fillna(1)), 100)
            ic_val, ic_all = rep.boot(v_val, rng), rep.boot(v_all, rng)
            mem = mem_estricto[m][3 * j:3 * j + 3]
            chequear(s, f"Tabla 4 · {m} (parser estricto) · {sub} · válidas", mem[0], int(ok.sum()), 0)
            chequear(s, f"Tabla 4 · {m} (parser estricto) · {sub} · solo válidas", mem[1], (v_val.mean(), *ic_val))
            chequear(s, f"Tabla 4 · {m} (parser estricto) · {sub} · inválidas = 100 %", mem[2], (v_all.mean(), *ic_all))
    x = d[orden[0]]
    for sub, c, mem_v, mem_a in [("real", 33, (37.0, 32.4, 41.5), (37.0, 32.6, 41.5)),
                                 ("sintetico", 10, (13.7, 11.9, 15.4), (13.7, 11.8, 15.4))]:
        g = x[x.subset == sub].ground_truth
        chequear(s, f"Constante · {sub} · mediana de la muestra", c, int(g.median()), 0)
        v = rep.smape(g, [int(g.median())] * len(g))
        chequear(s, f"Tabla 4 · constante ({c}) · {sub} · col. solo válidas", mem_v, (v.mean(), *rep.boot(v, rng)))
        chequear(s, f"Tabla 4 · constante ({c}) · {sub} · col. inválidas = 100 %", mem_a, (v.mean(), *rep.boot(v, rng)))

    # Predicción = 1 (4.1 y 4.6.2)
    for m, mem_tot, mem_sub in [("InternVL2-1B", 104, (45, 59)), ("Qwen2-VL-2B", 55, None)]:
        u = d[m][d[m].prediccion == 1]
        chequear(s, f"{m}: filas con predicción = 1 (de 200)", mem_tot, len(u), 0)
        if mem_sub:
            chequear(s, f"{m}: predicción = 1 (real; sint.)", mem_sub,
                     ((u.subset == "real").sum(), (u.subset == "sintetico").sum()), 0)
        else:
            chequear("4.6.2", f"{m}: predicción = 1 en el subset sintético", 49, (u.subset == "sintetico").sum(), 0)
        chequear(s, f"{m}: de esas, con respuesta correcta = 1", 0, int((u.ground_truth == 1).sum()), 0)
    i = d["InternVL2-1B"]
    lista = i[(i.prediccion == 1) & i.respuesta_cruda.astype(str).str.contains(r"(?m)^\s*1[.)]")]
    chequear("4.6.2", "InternVL2-1B: de las 104, cuántas comienzan una lista numerada", 87, len(lista), 0)

    # 3.2: cuartiles y grupos de Rango_Objetos
    g = d[orden[0]][d[orden[0]].subset == "real"].ground_truth
    chequear("3.2", "Rango de la respuesta correcta en CAPTURe real", (8, 501), (g.min(), g.max()), 0)
    chequear("3.2", "Valores distintos de la respuesta correcta", 59, g.nunique(), 0)
    q = np.percentile(g, [25, 50, 75])
    chequear("3.2", "Cuartiles q0,25; q0,50; q0,75", (17.75, 33, 76.5), tuple(q), 2)
    grupo = pd.cut(g, [-np.inf, q[0], q[1], q[2], np.inf], labels=["Chico", "Mediano", "Grande", "Masivo"])
    chequear("3.2", "Tamaño de los grupos (Chico; Mediano; Grande; Masivo)", (25, 27, 23, 25),
             tuple(grupo.value_counts().reindex(["Chico", "Mediano", "Grande", "Masivo"])), 0)

    # 4.1: acierto por Rango_Objetos (Figura 13), con Wilson
    for m in MODELOS:
        x = d[m][d[m].subset == "real"].copy()
        x["grupo"] = pd.cut(x.ground_truth, [-np.inf, q[0], q[1], q[2], np.inf], labels=["Chico", "Mediano", "Grande", "Masivo"])
        a = x.groupby("grupo", observed=False).acierto_exacto.agg(["sum", "count"])
        chequear(s, f"{m}: aciertos por grupo, sobre todas (Chico; Mediano; Grande; Masivo)", None,
                 tuple(f"{int(r['sum'])}/{int(r['count'])}" for _, r in a.iterrows()), 0)
    x = d["moondream2"][d["moondream2"].subset == "real"]
    k = int(x[x.ground_truth <= q[0]].acierto_exacto.sum())
    chequear(s, "moondream2: acierto en Chico (texto: 20 %, 5 de 25)", 20.0, 100 * k / 25)
    chequear(s, "moondream2: Wilson en Chico", (8.9, 39.1), wilson(k, 25))
    chequear(s, "Límite superior de Wilson con 0 aciertos (n = 23; n = 25)", (14.3, 13.3), (wilson(0, 23)[1], wilson(0, 25)[1]))
    return d


# ─────────────────────────────── 4.2 TallyQA ───────────────────────────────

def tallyqa():
    s = "4.2"
    d = {m: pd.read_csv(un_archivo(RAIZ / "pruebas/Conteo" / CARPETA_CONTEO[m] / "detalle_TallyQA_*.csv")) for m in MODELOS}
    mem = {"InternVL2-1B": [(78.8, 72.2, 84.1), 0.81, (63.6, 54.8, 71.7), 0.89],
           "moondream2": [(87.7, 82.1, 91.7), 0.59, (74.4, 65.9, 81.3), 0.76],
           "PaliGemma2-3B": [(75.4, 68.6, 81.1), 1.02, (60.3, 51.4, 68.6), 29.84],
           "Qwen2-VL-2B": [(86.0, 80.2, 90.4), 0.57, (74.4, 65.9, 81.3), 0.77]}
    for m in MODELOS:
        for j, simple in enumerate([True, False]):
            x = d[m][d[m].issimple == simple]
            k, n = int(x.acierto_exacto.sum()), len(x)
            v = validas(x)
            rmse = np.sqrt(((v.prediccion - v.ground_truth) ** 2).mean())
            tipo = "simple" if simple else "compleja"
            chequear(s, f"Tabla 5 · {m} · {tipo} · n", 179 if simple else 121, n, 0)
            chequear(s, f"Tabla 5 · {m} · {tipo} · acierto [Wilson]", mem[m][2 * j], (100 * k / n, *wilson(k, n)))
            chequear(s, f"Tabla 5 · {m} · {tipo} · RMSE", mem[m][2 * j + 1], rmse, 2)

    # McNemar moondream2 vs Qwen2-VL-2B, emparejando por question_id
    a = d["moondream2"].set_index("question_id")
    b = d["Qwen2-VL-2B"].set_index("question_id").loc[a.index]
    for simple, mem_n, mem_p in [(True, (9, 6), 0.61), (False, (10, 10), 1.0)]:
        idx = a.index[a.issimple == simple]
        x, y = a.loc[idx, "acierto_exacto"].astype(bool), b.loc[idx, "acierto_exacto"].astype(bool)
        n10, n01 = int((x & ~y).sum()), int((~x & y).sum())
        tipo = "simples" if simple else "complejas"
        chequear(s, f"McNemar moondream2 vs Qwen2-VL-2B · {tipo} · (solo moondream2; solo Qwen)", mem_n, (n10, n01), 0)
        chequear(s, f"McNemar moondream2 vs Qwen2-VL-2B · {tipo} · p", mem_p, mcnemar_exacto(n10, n01), 2)

    # Outlier de PaliGemma2-3B
    x = validas(d["PaliGemma2-3B"][d["PaliGemma2-3B"].issimple == False])
    e = (x.prediccion - x.ground_truth).abs()
    fila = x.loc[e.idxmax()]
    chequear(s, "PaliGemma2-3B · outlier: (respuesta correcta; respuesta)", (2, 330), (fila.ground_truth, fila.prediccion), 0)
    sin = x.drop(e.idxmax())
    e2 = sin.prediccion - sin.ground_truth
    chequear(s, "PaliGemma2-3B · compleja · MAE con y sin outlier", (3.31, 0.60), (e.mean(), e2.abs().mean()), 2)
    chequear(s, "PaliGemma2-3B · compleja · RMSE sin outlier", 1.17, np.sqrt((e2**2).mean()), 2)
    chequear(s, "Cota (2.10): 328/√121", 29.8, 328 / np.sqrt(121), 1)
    chequear(s, "Aporte del outlier al MAE: 328/121", 2.71, 328 / 121, 2)
    chequear(s, "n válidas en compleja (PaliGemma2-3B)", 121, len(x), 0)

    # Comparación con RCN (71,8 % simple; 56,2 % compleja): límite inferior de Wilson
    for m in MODELOS:
        lims = []
        for simple in [True, False]:
            x = d[m][d[m].issimple == simple]
            lims.append(wilson(int(x.acierto_exacto.sum()), len(x))[0])
        chequear(s, f"{m}: límites inferiores de Wilson (simple; compleja) vs RCN 71,8 y 56,2", None, tuple(lims))
    return d


# ─────────────────────────────── 4.3 OmniSpatial ───────────────────────────────

def omnispatial():
    s = "4.3"
    d = {m: pd.read_csv(un_archivo(RAIZ / "pruebas/razonamiento espacial" / CARPETA_OMNI[m] / "detalle_OmniSpatial_*.csv")) for m in MODELOS}
    tracks = ["Geometric_Reasoning", "Motion_Analysis", "Egocentric", "Allocentric"]
    ref = d["InternVL2-1B"]
    iguales = all((d[m].id.values == ref.id.values).all() for m in MODELOS)
    chequear(s, "Las 4 corridas usan las mismas 400 preguntas (1 = sí)", 1, int(iguales), 0)

    mem_may = {"Geometric_Reasoning": 27, "Motion_Analysis": 31, "Egocentric": 36, "Allocentric": 28}
    mem_acc = {"Geometric_Reasoning": (25, 29, 25, 35), "Motion_Analysis": (30, 33, 45, 43),
               "Egocentric": (49, 60, 58, 59), "Allocentric": (37, 27, 41, 36)}
    for tr in tracks:
        x = ref[ref.track == tr]
        bmay = 100 * x.ground_truth.value_counts().max() / len(x)       # ecuación (2.11)
        chequear(s, f"Tabla 6 · {tr} · clase mayoritaria (%)", mem_may[tr], bmay, 0)
        accs = tuple(100 * d[m][d[m].track == tr].acierto.mean() for m in MODELOS)
        chequear(s, f"Tabla 6 · {tr} · acierto (InternVL; moondream; PaliGemma; Qwen)", mem_acc[tr], accs, 0)
        for m in MODELOS:
            y = d[m][d[m].track == tr]
            k, n = int(y.acierto.sum()), len(y)
            lo, hi = wilson(k, n)
            supera = "SUPERA" if lo > bmay else "no supera"
            chequear(s, f"{tr} · {m}: {k}/{n}, Wilson y criterio 2.7.5 vs mayoritaria", None, (lo, hi, supera))
    chequear(s, "Tabla 6 · acierto global (InternVL; moondream; PaliGemma; Qwen)", (35.2, 37.2, 42.2, 43.2),
             tuple(100 * d[m].acierto.mean() for m in MODELOS))

    # Cifras citadas con su intervalo
    def w(m, tr):
        y = d[m][d[m].track == tr]
        k = int(y.acierto.sum())
        return (100 * k / len(y), *wilson(k, len(y)))
    chequear(s, "Allocentric · PaliGemma2-3B [Wilson]", (41, 31.9, 50.8), w("PaliGemma2-3B", "Allocentric"))
    chequear(s, "Allocentric · moondream2 [Wilson]", (27, 19.3, 36.4), w("moondream2", "Allocentric"))
    chequear(s, "Motion_Analysis · PaliGemma2-3B [Wilson]", (45, 35.6, 54.8), w("PaliGemma2-3B", "Motion_Analysis"))
    chequear(s, "Motion_Analysis · Qwen2-VL-2B [Wilson]", (43, 33.7, 52.8), w("Qwen2-VL-2B", "Motion_Analysis"))
    chequear(s, "Geometric_Reasoning · Qwen2-VL-2B [Wilson]", (35, 26.4, 44.7), w("Qwen2-VL-2B", "Geometric_Reasoning"))
    y = d["Qwen2-VL-2B"][d["Qwen2-VL-2B"].track == "Geometric_Reasoning"]
    p = stats.binomtest(int(y.acierto.sum()), len(y), 0.27, alternative="greater").pvalue
    chequear(s, "Geometric · Qwen2-VL-2B · binomial unilateral exacta vs 27 % (p)", 0.048, p, 3)
    chequear(s, "Allocentric · InternVL2-1B [Wilson] (el texto dice que solo PaliGemma supera)", None,
             w("InternVL2-1B", "Allocentric"))
    y = d["InternVL2-1B"]
    chequear(s, "InternVL2-1B · parse_fail en Motion_Analysis (%)", 23, 100 * y[y.track == "Motion_Analysis"].parse_fail.mean(), 0)
    # Cobertura de las muestras (disponibles: 155, 346, 102, 376 de 1.533)
    chequear(s, "Cobertura de la muestra (%): 100/155; 100/346; 100/102; 100/376; 400/1533", (65, 29, 98, 27, 26),
             (100 / 1.55, 100 / 3.46, 100 / 1.02, 100 / 3.76, 40000 / 1533), 0)
    # Información para la frase de 5.1 sobre el sesgo hacia una alternativa
    for m in MODELOS:
        y = d[m][d[m].pred_letra.notna()]
        chequear("5.1", f"{m}: % de respuestas 'A' por track (Geo; Mot; Ego; Allo)", None,
                 tuple(100 * (y[y.track == tr].pred_letra == "A").mean() for tr in tracks), 0)
    return d


# ─────────────────────────────── 4.4 y 4.6 sintético v1 ───────────────────────────────

def sintetico():
    d = {}
    for m, pat in [("InternVL2-1B", "InternVL2_1B"), ("moondream2", "moondream2"),
                   ("PaliGemma2-3B", "paligemma2_3b"), ("Qwen2-VL-2B", "qwen2_vl_2b")]:
        d[m] = pd.read_csv(un_archivo(RAIZ / "benchmark_sintetico/pruebas" / pat / "detalle_2Dsintetico_*.csv"))
    s = "4.6.1"
    for m, mem in [("PaliGemma2-3B", (31, 85.97, 5)), ("Qwen2-VL-2B", (36, 81.4, 3))]:
        x = d[m][d[m].tipo_pregunta == "conteo_general"]
        c = x[x.prediccion == 100]
        chequear(s, f"{m}: responde 100 (n); GT media; GT = 100", mem,
                 (len(c), c.ground_truth.mean(), (c.ground_truth == 100).sum()), 2 if m.startswith("Pali") else 1)
        dec = 1
        v = validas(x)
        t = smape_terminos(v.ground_truth, v.prediccion)
        es100 = (v.prediccion == 100).values
        mem_t = (7.9, 22.5) if m.startswith("Pali") else (10.7, 6.4)
        chequear(s, f"{m}: término sMAPE medio (respuestas = 100; resto)", mem_t, (t[es100].mean(), t[~es100].mean()), dec)
    chequear(s, "Ejemplo: 14/186 (%)", 7.5, 100 * 14 / 186)
    x = d["PaliGemma2-3B"][d["PaliGemma2-3B"].tipo_pregunta == "conteo_general"]
    chequear(s, "conteo_general: rango de la respuesta correcta", (5, 100), (x.ground_truth.min(), x.ground_truth.max()), 0)

    s = "4.6.2"
    i = d["InternVL2-1B"]
    m_ = i.respuesta_cruda.astype(str).str.startswith("To determine")
    chequear(s, "InternVL2-1B · sintético · filas con razonamiento paso a paso (de 400)", 35, int(m_.sum()), 0)
    chequear(s, "… de ellas en conteo_general", 30, int((m_ & (i.tipo_pregunta == "conteo_general")).sum()), 0)
    chequear(s, "… con predicción = 1", 35, int((i[m_].prediccion == 1).sum()), 0)
    rec = i[m_].respuesta_cruda.str.extract(r"[Tt]here are (\d+)")[0]
    chequear(s, "… sin 'there are N' recuperable", 23, int(rec.isna().sum()), 0)
    ok_rec = (rec.dropna().astype(int) == i[m_].ground_truth[rec.notna()]).sum()
    chequear(s, "… valores recuperados correctos", 0, int(ok_rec), 0)
    gtmin = i[m_ & (i.tipo_pregunta == "conteo_general")].ground_truth.min()
    chequear(s, "… mínima respuesta correcta en conteo_general afectado (texto: ≥ 15)", 15, gtmin, 0)

    s = "4.4"
    for m in MODELOS:
        acc = d[m].groupby("tipo_pregunta").acierto_exacto.mean() * 100
        sm = {}
        for tp, x in d[m].groupby("tipo_pregunta"):
            v = validas(x)
            sm[tp] = smape_terminos(v.ground_truth, v.prediccion).mean()
        orden = ["conteo_general", "conteo_forma", "conteo_color", "conteo_combinado"]
        chequear(s, f"{m}: acierto % (general; forma; color; combinado)", None, tuple(acc[orden]), 0)
        chequear(s, f"{m}: sMAPE % (general; forma; color; combinado)", None, tuple(sm[o] for o in orden), 0)
    # Respaldo de la "inversión de ranking" (4.4 y 5.1.1): MAE contra sMAPE, en total y con 80 figuras o más
    for m in MODELOS:
        v = validas(d[m])
        e = (v.prediccion - v.ground_truth).abs()
        t = smape_terminos(v.ground_truth, v.prediccion)
        alto = (v.num_shapes >= 80).values
        chequear(s, f"{m}: MAE total; sMAPE total; MAE con ≥ 80 figuras; sMAPE con ≥ 80 figuras", None,
                 (e.mean(), t.mean(), e[alto].mean(), t[alto].mean()))
    return d


# ─────────────────────────────── 4.5 Tabla 7: costo ───────────────────────────────

def costo(dcap, dtal, domni, dsin):
    s = "4.5"
    archivos_txt = {
        "InternVL2-1B": ["pruebas/Conteo/InternVL2_1B/resultados_*.txt", "pruebas/razonamiento espacial/InternVL2_1B/resultados_*.txt",
                         "benchmark_sintetico/pruebas/InternVL2_1B/resultados_*.txt"],
        "moondream2": ["pruebas/Conteo/moondream2/resultados_*.txt", "pruebas/razonamiento espacial/moondream2/resultados_*.txt",
                       "benchmark_sintetico/pruebas/moondream2/resultados_*.txt"],
        "PaliGemma2-3B": ["pruebas/Conteo/paligemma2_3b/resultados_*.txt", "pruebas/razonamiento espacial/paligemma2/resultados_*.txt",
                          "benchmark_sintetico/pruebas/paligemma2_3b/resultados_*.txt"],
        "Qwen2-VL-2B": ["pruebas/Conteo/qwen2_vl_2b/resultados_*.txt", "pruebas/razonamiento espacial/qwen2vl/resultados_*.txt",
                        "benchmark_sintetico/pruebas/qwen2_vl_2b/resultados_*.txt"]}
    mem_vram = {"InternVL2-1B": (1.8, 2.3), "moondream2": (4.9, 5.2), "PaliGemma2-3B": (6.0, 6.0), "Qwen2-VL-2B": (4.7, 8.5)}
    mem_lat = {"InternVL2-1B": [(3.15, 0.17), (3.14, 0.09), (0.71, 0.04), (1.02, 0.05)],
               "moondream2": [(3.38, 0.29), (2.08, 0.08), (4.94, 0.08), (5.02, 0.02)],
               "PaliGemma2-3B": [(2.95, 0.06), (2.72, 0.01), (2.81, 0.01), (2.90, 0.02)],
               "Qwen2-VL-2B": [(2.18, 0.09), (1.36, 0.07), (2.59, 0.04), (11.22, 0.02)]}
    for m in MODELOS:
        vram = []
        for pat in archivos_txt[m]:
            for f in glob.glob(str(RAIZ / pat)):
                for linea in open(f, encoding="utf-8"):
                    if linea.startswith("VRAM_PICO_MB"):
                        vram.append(float(linea.split(":")[1]) / 1024)
        chequear(s, f"Tabla 7 · {m} · VRAM pico, GB (mín; máx), {len(vram)} corridas", mem_vram[m], (min(vram), max(vram)))
        for j, (nombre, d) in enumerate([("CAPTURe", dcap[m]), ("TallyQA", dtal[m]), ("OmniSpatial", domni[m]), ("sintético", dsin[m])]):
            t = d[~d.timeout.astype(bool)].tiempo_seg
            semi = 1.96 * t.std(ddof=1) / np.sqrt(len(t))
            chequear(s, f"Tabla 7 · {m} · latencia {nombre} (media; ± semiancho)", mem_lat[m][j], (t.mean(), semi), 2)
    for m in MODELOS:
        for d, nombre in [(dcap[m], "CAPTURe"), (dtal[m], "TallyQA"), (domni[m], "OmniSpatial"), (dsin[m], "sintético")]:
            chequear("2.6.5", f"{m} · timeout en {nombre} (texto: 0 %)", 0, 100 * d.timeout.astype(bool).mean(), 0)


# ─────────────────────────────── 4.7 Explicabilidad ───────────────────────────────

def explicabilidad(suf):
    res = RAIZ / "pruebas/explicabilidad/resultados"
    for carpeta in [f"01_conducta{suf}", f"02_rollout{suf}", f"03_gradcam{suf}"]:
        if not (res / carpeta / "analisis").exists():
            raise SystemExit(f"Falta {res / carpeta / 'analisis'}: corre antes los scripts analizar_*.py de esa corrida.")
    t = pd.read_csv(res / f"01_conducta{suf}/analisis/por_pregunta.csv")  # ojo: t["gt"], porque t.gt es un método de pandas
    n = len(t)
    s = "4.7.1"
    k = int((t.c0 == t["gt"]).sum())
    chequear(s, "Acierto en c0 [Wilson] (%)", (12.5, 7.7, 19.6), (100 * k / n, *wilson(k, n)))
    chequear(s, "Cuenta de menos en c0 (%)", 85.8, 100 * (t.c0 < t["gt"]).mean())
    chequear(s, "Error medio en c0", -2.3, (t.c0 - t["gt"]).mean())
    chequear(s, "Repertorio de respuestas en c0", None, tuple(str(int(v)) for v in sorted(t.c0.dropna().unique())))
    r = recta(t["gt"], t.c0)
    chequear("Tabla 8", "Pendiente β̂1 [IC t]", (0.445, 0.368, 0.523), (r["b1"], *r["b1_ic"]), 3)
    chequear("Tabla 8", "Intercepto β̂0 [IC t]", (0.92, 0.43, 1.42), (r["b0"], *r["b0_ic"]), 2)
    chequear(s, "R² lineal y R² contra log(respuesta correcta)", (0.52, 0.50), (r["r2"], recta(np.log(t["gt"]), t.c0)["r2"]), 2)
    b = (t.c2 - t.c0) / 2                                                       # ecuación (3.7)
    chequear(s, "Ec. (3.7) coincide con la pendiente guardada (1 = sí)", 1, int(np.allclose(b, t.pendiente)), 0)
    chequear("Tabla 8", "Pendiente media de la oclusión [IC t]", (-0.433, -0.513, -0.354), (b.mean(), *ic_media_t(b)), 3)
    c1 = t.c1 != t.c0
    ct = t.control != t.c0
    chequear(s, "Cambia al borrar 1 objetivo [Wilson] (%)", (42.5, 34.0, 51.4), (100 * c1.mean(), *wilson(int(c1.sum()), n)))
    chequear(s, "Cambia al borrar 1 no objetivo [Wilson] (%)", (10.8, 6.4, 17.7), (100 * ct.mean(), *wilson(int(ct.sum()), n)))
    n10, n01 = int((c1 & ~ct).sum()), int((~c1 & ct).sum())
    chequear(s, "McNemar c1 vs control (solo c1; solo control)", (43, 5), (n10, n01), 0)
    chequear(s, "McNemar c1 vs control · p (×10⁻⁸)", 1.4, 1e8 * mcnemar_exacto(n10, n01), 1)
    cat = t.oclusion.value_counts()
    chequear(s, "Categorías: cuenta; dirección correcta; no reacciona; otra", (11, 63, 42, 4),
             tuple(int(cat.get(c, 0)) for c in ["cuenta", "direccion_correcta", "no_reacciona", "otra"]), 0)

    s = "4.7.2"
    chequear(s, "Puntos totales; % sobre figura objetivo", (790, 77.0),
             (t.n_puntos.sum(), 100 * t.puntos_en_objetivo.sum() / t.n_puntos.sum()))
    chequear(s, "Figuras objetivo; % encontradas (cobertura)", (701, 68.6),
             (t["gt"].sum(), 100 * t.objetivos_encontrados.sum() / t["gt"].sum()))
    pt = t.objetivos_encontrados == t["gt"]
    q = t.c0 == t["gt"]
    chequear(s, "Conteo por puntos exacto vs respuesta escrita (%)", (27.5, 12.5), (100 * pt.mean(), 100 * q.mean()))
    n10, n01 = int((pt & ~q).sum()), int((~pt & q).sum())
    chequear(s, "McNemar puntos vs escrita (solo puntos; solo escrita) y p", (25, 7, 0.002), (n10, n01, mcnemar_exacto(n10, n01)), 3)
    sd = t[t.n_puntos < 100]
    chequear(s, "Sin llamadas degeneradas: preguntas; puntos; precisión %; cobertura %", (118, 590, 81.9, 69.1),
             (len(sd), sd.n_puntos.sum(), 100 * sd.puntos_en_objetivo.sum() / sd.n_puntos.sum(),
              100 * sd.objetivos_encontrados.sum() / sd["gt"].sum()))

    s = "4.7.3"
    ro = pd.read_csv(res / f"02_rollout{suf}/analisis/por_imagen.csv")
    chequear(s, "Masa del rollout en los 8 tokens fijos (%) y 8/729 (%)", (19.4, 1.1), (ro.masa_en_sinks_pct.mean(), 800 / 729))
    chequear(s, "Correlación con la imagen gris (con; sin tokens fijos)", (0.997, 0.957),
             (ro.corr_con_gris.mean(), ro.corr_con_gris_sin_sinks.mean()), 3)
    chequear(s, "Enriquecimiento de las figuras (con; sin tokens fijos)", (1.5, 1.8),
             (ro.enriq_figuras.mean(), ro.enriq_figuras_sin_sinks.mean()))
    rs = pd.read_csv(res / f"02_rollout{suf}/resumen.csv")
    tops = rs.top5_rollout.map(lambda x: tuple(sorted(x.split())))
    chequear(s, "Imágenes con el mismo top-5 de rollout (de 22)", 22, int((tops == tops.iloc[-2]).sum()), 0)
    fondo = 100 - ro.area_figuras_pct.mean()
    chequear("3.4", "Área media del fondo (%) y cota 1/fondo", (97.4, 1.03), (fondo, 100 / fondo), 2 if False else 1)
    chequear("3.4", "Área media de las figuras objetivo (%)", 0.38, ro.area_objetivo_pct.mean(), 2)

    s = "4.7.4"
    g = pd.read_csv(res / f"03_gradcam{suf}/analisis/por_imagen.csv")
    chequear(s, "Grad-CAM: enriquecimiento mediano (objetivo; otras; fondo)", (0.08, 0.23, 1.02),
             (g.gradcam_llm_enriq_objetivo.median(), g.gradcam_llm_enriq_otras.median(), g.gradcam_llm_enriq_fondo.median()), 2)
    mayor = int((g.gxi_objetivo > g.gxi_otras).sum())
    chequear(s, "Grad × entrada: objetivo > otras (de 20) y prueba de signos p", (15, 0.041),
             (mayor, mcnemar_exacto(mayor, len(g) - mayor)), 3)
    chequear(s, "Wilcoxon pareado (p)", 0.070, stats.wilcoxon(g.gxi_objetivo, g.gxi_otras).pvalue, 3)
    camb = g.delta_c1 != 0
    pa, pb = g.gradcam_llm_pct_borrada_c1[camb], g.gradcam_llm_pct_borrada_c1[~camb]
    chequear(s, "Percentil de la figura borrada (cambió; no cambió): n y medias", (12, 8, 26, 5),
             (len(pa), len(pb), pa.mean(), pb.mean()), 0)
    chequear(s, "Medianas del percentil (cambió; no cambió)", (0, 0), (pa.median(), pb.median()), 0)
    chequear(s, "Mann-Whitney (p)", 0.29, stats.mannwhitneyu(pa, pb, alternative="two-sided").pvalue, 2)


# ─────────────────────────────── Principal ───────────────────────────────

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # consola de Windows
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capture", default=None, help="carpeta con los 4 detalle_CAPTURe_*.csv (por defecto, la corrida original)")
    ap.add_argument("--explic", default="", help="sufijo de las carpetas de resultados de explicabilidad, p. ej. _t70")
    a = ap.parse_args()

    ejemplos_cap2()
    dcap = capture(a.capture)
    dtal = tallyqa()
    domni = omnispatial()
    dsin = sintetico()
    costo(dcap, dtal, domni, dsin)
    explicabilidad(a.explic)

    df = pd.DataFrame(FILAS)
    etiqueta = ""                     # con corridas nuevas, la salida lleva otro nombre y no pisa la verificación original
    if a.capture:
        etiqueta += "_" + Path(a.capture).name
    if a.explic:
        etiqueta += a.explic
    salida_md = AQUI / f"estadistica_cap4_resultados{etiqueta}.md"
    df.to_csv(AQUI / f"estadistica_cap4_resultados{etiqueta}.csv", index=False, encoding="utf-8")
    cuenta = df.estado.value_counts()
    lineas = ["# Verificación de las cifras estadísticas de la memoria", "",
              f"CAPTURe: {a.capture or 'corrida original'} · explicabilidad: resultados/*{a.explic or ''}", "",
              "Resumen: " + " · ".join(f"{k} {v}" for k, v in cuenta.items()), ""]
    for sec, grupo in df.groupby("seccion", sort=False):
        lineas += [f"## {sec}", "", "| Cifra | Memoria v5 | Calculado | Estado |", "|---|---|---|---|"]
        lineas += [f"| {r.cifra} | {r.memoria} | {r.calculado} | {r.estado} |" for r in grupo.itertuples()]
        lineas.append("")
    salida_md.write_text("\n".join(lineas), encoding="utf-8")
    print("\n".join(lineas[:6]))
    malos = df[df.estado == "DISTINTO"]
    if len(malos):
        print("DISTINTO:")
        print(malos[["seccion", "cifra", "memoria", "calculado"]].to_string(index=False))
    print(f"\nEscrito: {salida_md}")


if __name__ == "__main__":
    main()
