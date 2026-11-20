"""Re-extracción de las respuestas de CAPTURe desde `respuesta_cruda` (no requiere GPU).

Uso:  python reparsear_capture.py <carpeta con los 4 detalle_CAPTURe_*.csv>  [salida.csv]

Regla estricta (fijada antes de calcular las métricas):
  R1. La respuesta completa es un entero.
  R2. El modelo enuncia su conteo de forma explícita ("final count is N", "total number ... is N",
      "there are N ...", "count is N", "the answer is N", "total of N"); se toma el ÚLTIMO enunciado
      y se descartan los conteos parciales (por fila, columna, anillo...).
  En cualquier otro caso la fila queda sin conteo (se trata como respuesta inválida).
Los dígitos de marcadores de lista ("1.", "2)") y de descripciones del patrón NO se interpretan como conteo.
sMAPE = 100 * mean(|y - yhat| / (|y| + |yhat|)), como en 2.6.2 y en [Poth25]; IC bootstrap B = 5000, semilla 2026.
"""
import re, sys, glob, os
import numpy as np, pandas as pd

W = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10,
     'eleven':11,'twelve':12,'thirteen':13,'fourteen':14,'fifteen':15,'sixteen':16,'seventeen':17,
     'eighteen':18,'nineteen':19,'twenty':20}
NUM = r'(\d{1,4}|' + '|'.join(W) + r')'
PATS = [
 r'final\s+count\s*(?:is|:|=|would be|of)?\s*(?:approximately\s+|about\s+)?' + NUM + r'\b',
 r'total\s+(?:count|number)[^.\n\d]{0,60}?\b(?:is|are|=|:)\s*(?:approximately\s+|about\s+)?' + NUM + r'\b',
 r'\bthere\s+(?:are|were|is)\s+(?:a\s+total\s+of\s+|approximately\s+|about\s+|exactly\s+)?' + NUM + r'\b(?!\s*(?:rows?|columns?|rings?|circles? in the|per))',
 r'\bcount\s+(?:is|of)\s+(?:approximately\s+)?' + NUM + r'\b',
 r'\bthe\s+answer\s+is\s+' + NUM + r'\b',
 r'\btotal\s+of\s+' + NUM + r'\b',
]
PARCIAL = re.compile(r'\b(?:in|per|on|for|of)\s+(?:the\s+|each\s+|every\s+)?(?:\w+\s+)?(?:rows?|columns?|rings?|lines?|layers?|sides?|groups?|section)\b|\beach\s+(?:row|column)', re.I)

def tonum(s):
    s = s.lower(); return int(s) if s.isdigit() else W[s]

def parse_estricto(txt):
    t = str(txt).strip()
    m = re.fullmatch(r'(\d{1,4})\s*\.?', t)
    if m: return int(m.group(1)), 'R1'
    best = None
    for p in PATS:
        for m in re.finditer(p, t, flags=re.I):
            resto = re.split(r'[.\n]', t[m.end():m.end() + 90])[0]
            if PARCIAL.search(resto): continue
            if best is None or m.start() > best[0]: best = (m.start(), tonum(m.group(1)))
    return (best[1], 'R2') if best else (None, 'sin_conteo')

def smape(y, p):
    y = np.asarray(y, float); p = np.asarray(p, float)
    return 100 * np.abs(y - p) / (np.abs(y) + np.abs(p))

def boot(v, rng, B=5000):
    v = np.asarray(v, float); idx = rng.integers(0, len(v), (B, len(v)))
    return np.percentile(v[idx].mean(1), [2.5, 97.5])

if __name__ == '__main__':
    carpeta = sys.argv[1]; salida = sys.argv[2] if len(sys.argv) > 2 else 'tabla4_reparseo.csv'
    nombres = {'InternVL2-1B': 'InternVL2', 'moondream2': 'moondream2', 'paligemma2-3b': 'PaliGemma2-3B', 'qwen2vl-2b': 'Qwen2-VL-2B'}
    rng = np.random.default_rng(2026); filas = []
    for f in sorted(glob.glob(os.path.join(carpeta, 'detalle_CAPTURe_*.csv'))):
        modelo = [v for k, v in nombres.items() if k in f][0]
        d = pd.read_csv(f); r = d.respuesta_cruda.astype(str).map(parse_estricto)
        d['nuevo'] = [x[0] for x in r]; d['regla'] = [x[1] for x in r]
        for s in ['real', 'sintetico']:
            x = d[d.subset == s]; ok = x.nuevo.notna()
            v_val = smape(x.ground_truth[ok], x.nuevo[ok]); v_all = np.where(ok, smape(x.ground_truth, x.nuevo.fillna(1)), 100)
            filas.append(dict(modelo=modelo, subset=s, validas=int(ok.sum()), smape_validas=v_val.mean(),
                              ic_validas=tuple(boot(v_val, rng)), smape_inv100=v_all.mean(), ic_inv100=tuple(boot(v_all, rng)),
                              acierto_exacto_pct=100 * float((x.nuevo == x.ground_truth).mean())))
        # baseline constante: la mediana de la muestra (en la muestra, por lo que es optimista)
    d0 = pd.read_csv(sorted(glob.glob(os.path.join(carpeta, 'detalle_CAPTURe_*.csv')))[0])
    for s in ['real', 'sintetico']:
        g = d0[d0.subset == s].ground_truth; c = int(g.median()); v = smape(g, [c] * len(g))
        filas.append(dict(modelo=f'Constante ({c})', subset=s, validas=len(g), smape_validas=v.mean(), ic_validas=tuple(boot(v, rng)),
                          smape_inv100=v.mean(), ic_inv100=tuple(boot(v, rng)), acierto_exacto_pct=100 * float((g == c).mean())))
    pd.DataFrame(filas).to_csv(salida, index=False); print(pd.DataFrame(filas).round(1).to_string())
