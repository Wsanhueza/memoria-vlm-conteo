"""Funciones comunes del experimento de explicabilidad (uso local, sin GPU).

Reutiliza el generador original (benchmark_sintetico/2D.py) para regenerar
exactamente las imágenes del dataset v2 y redibujarlas sin algunas figuras.
"""
import importlib.util
import random
import re
import sys
import types
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[2]
RUTA_2D = RAIZ / "benchmark_sintetico" / "2D.py"

# Parámetros con que se generó el dataset v2 (benchmark_2d_sintetico_lotes_2400_v2.zip).
# No quedaron guardados en el zip: se recuperaron regenerando las 600 imágenes
# y comprobando que fueran idénticas píxel a píxel (600/600, 10-11-2026).
PARAMS_V2 = dict(res=1024, tamano=35, solapamiento=0.30, borde=2, semilla_base=42)
FONDO = (200, 200, 200)
COLOR_BORDE = (30, 30, 30)


def cargar_generador():
    """Importa 2D.py sin levantar la interfaz de Gradio."""
    if "gradio" not in sys.modules:
        class _Nada:
            def __init__(self, *a, **k): pass
            def __call__(self, *a, **k): return _Nada()
            def __getattr__(self, nombre): return _Nada()
            def __enter__(self): return self
            def __exit__(self, *a): return False
        falso = types.ModuleType("gradio")
        for nombre in ["Blocks", "Tabs", "Tab", "Row", "Column", "Slider", "Markdown",
                       "Button", "Textbox", "File", "Progress"]:
            setattr(falso, nombre, _Nada)
        sys.modules["gradio"] = falso
    spec = importlib.util.spec_from_file_location("gen2d", RUTA_2D)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


GEN = cargar_generador()


def datos_de_nombre(nombre_archivo):
    """'escena_0114_n035.png' -> (114, 35)."""
    idx = int(re.search(r"escena_(\d+)_", nombre_archivo).group(1))
    n = int(re.search(r"_n(\d+)", nombre_archivo).group(1))
    return idx, n


def regenerar_v2(nombre_archivo):
    """Vuelve a generar una imagen de v2 y devuelve (imagen, lista de objetos en orden de dibujo)."""
    idx, n = datos_de_nombre(nombre_archivo)
    p = PARAMS_V2
    random.seed(p["semilla_base"] + idx)
    img, metadata = GEN.generate_image(p["res"], p["res"], n, p["solapamiento"], p["tamano"], p["borde"])
    return img, metadata["objetos"]


def _dibujar_figura(draw, obj, relleno, borde, grosor):
    x, y, s = obj["x"], obj["y"], obj["tamano"]
    if obj["forma"] == "cuadrado":
        draw.rectangle([x, y, x + s, y + s], fill=relleno, outline=borde, width=grosor)
    elif obj["forma"] == "circulo":
        draw.ellipse([x, y, x + s, y + s], fill=relleno, outline=borde, width=grosor)
    elif obj["forma"] == "triangulo":
        draw.polygon(GEN.get_triangle_points(x, y, s), fill=relleno, outline=borde, width=grosor)
    else:
        draw.polygon(GEN.get_rombo_points(x, y, s), fill=relleno, outline=borde, width=grosor)


def dibujar(objetos, excluir=(), res=PARAMS_V2["res"], grosor=PARAMS_V2["borde"]):
    """Dibuja la escena con las mismas reglas que 2D.py, omitiendo los índices en `excluir`."""
    img = Image.new("RGB", (res, res), FONDO)
    draw = ImageDraw.Draw(img)
    for i, obj in enumerate(objetos):
        if i not in excluir:
            _dibujar_figura(draw, obj, GEN.COLORS[obj["color"]], COLOR_BORDE, grosor)
    return img


def mapa_etiquetas(objetos, excluir=(), res=PARAMS_V2["res"], grosor=PARAMS_V2["borde"]):
    """Matriz res x res: 0 = fondo; i+1 = la figura i es la que se ve en ese píxel."""
    img = Image.new("L", (res, res), 0)
    draw = ImageDraw.Draw(img)
    for i, obj in enumerate(objetos):
        if i not in excluir:
            _dibujar_figura(draw, obj, i + 1, i + 1, grosor)
    return np.asarray(img)


def figuras_aisladas(objetos, res=PARAMS_V2["res"], grosor=PARAMS_V2["borde"]):
    """True para cada figura que no toca a ninguna otra."""
    mascaras = []
    for obj in objetos:
        m = Image.new("1", (res, res), 0)
        _dibujar_figura(ImageDraw.Draw(m), obj, 1, 1, grosor)
        mascaras.append(np.asarray(m))
    conteo = np.sum(mascaras, axis=0)
    return [bool((conteo[m] == 1).all()) for m in mascaras]


def extraer_entero(texto):
    """Primer entero de la respuesta, ignorando marcadores de lista ('1.', '2)') al inicio de línea.
    Devuelve None si no hay ninguno."""
    if texto is None:
        return None
    limpio = re.sub(r"(?m)^\s*\d+[.)]\s+", "", str(texto))
    m = re.search(r"-?\d+", limpio)
    return int(m.group()) if m else None


def clasificar_error(prediccion, gt):
    """Grupos fijos del diseño: acierto (0), cercano (1-2), lejano (>=3), invalido."""
    if prediccion is None:
        return "invalido"
    error = abs(prediccion - gt)
    if error == 0:
        return "acierto"
    return "cercano" if error <= 2 else "lejano"
