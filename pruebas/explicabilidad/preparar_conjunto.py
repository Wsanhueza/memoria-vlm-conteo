"""Arma el conjunto de explicabilidad a partir del dataset v2 (CPU, sin modelo).

Uso (desde la raíz del repositorio):
    python pruebas/explicabilidad/preparar_conjunto.py

Produce pruebas/explicabilidad/conjunto_v2/ y conjunto_v2.zip (este último se sube a Drive).
Las reglas están en DISENO.md (secciones 3 y 4).
"""
import csv
import io
import json
import random
import shutil
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from explicabilidad_utils import (RAIZ, dibujar, figuras_aisladas, mapa_etiquetas,
                                  regenerar_v2, datos_de_nombre, GEN)

SEMILLA = 2026
NIVELES = [15, 25, 35, 45, 55]
POR_NIVEL_Y_TIPO = 12
GT_MIN, GT_MAX = 2, 10

ZIP_V2 = RAIZ / "benchmark_sintetico" / "benchmark_2d_sintetico_lotes_2400_v2.zip"
SALIDA = Path(__file__).resolve().parent / "conjunto_v2"

PLURAL = {"cuadrado": "squares", "circulo": "circles", "triangulo": "triangles", "rombo": "diamonds"}


def opciones_validas(objetos, tipo):
    """Formas o colores cuyo conteo queda entre GT_MIN y GT_MAX."""
    clave = "forma" if tipo == "conteo_forma" else "color"
    valores = GEN.SHAPES if tipo == "conteo_forma" else list(GEN.COLORS)
    conteos = {v: sum(o[clave] == v for o in objetos) for v in valores}
    return [v for v in valores if GT_MIN <= conteos[v] <= GT_MAX], conteos


def elegir(indices, aisladas, k, rng):
    """k índices al azar, prefiriendo figuras que no tocan a otras."""
    preferidos = [i for i in indices if aisladas[i]]
    resto = [i for i in indices if not aisladas[i]]
    rng.shuffle(preferidos)
    rng.shuffle(resto)
    return (preferidos + resto)[:k]


def main():
    rng = random.Random(SEMILLA)
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    (SALIDA / "imagenes").mkdir(parents=True)
    (SALIDA / "etiquetas").mkdir()

    with zipfile.ZipFile(ZIP_V2) as z:
        nombres = sorted(n.split("/")[-1] for n in z.namelist() if n.endswith(".png"))
        originales = {n: z.read(f"images/{n}") for n in nombres}

    preguntas, imagenes, escenas = [], [], {}
    for nivel in NIVELES:
        del_nivel = [n for n in nombres if datos_de_nombre(n)[1] == nivel]
        rng.shuffle(del_nivel)
        usadas = set()  # cada imagen se usa en un solo tipo de pregunta
        for tipo in ["conteo_forma", "conteo_color"]:
            elegidas = 0
            for nombre in del_nivel:
                if elegidas == POR_NIVEL_Y_TIPO:
                    break
                if nombre in usadas:
                    continue
                img, objetos = regenerar_v2(nombre)
                validas, conteos = opciones_validas(objetos, tipo)
                if not validas:
                    continue
                with Image.open(io.BytesIO(originales[nombre])) as ref:
                    assert np.array_equal(np.asarray(img), np.asarray(ref.convert("RGB"))), nombre
                usadas.add(nombre)
                elegidas += 1

                objetivo = rng.choice(validas)
                clave = "forma" if tipo == "conteo_forma" else "color"
                if tipo == "conteo_forma":
                    pregunta = f"How many {GEN.SHAPE_EN[objetivo]}s are there in the image?"
                    objeto_point = PLURAL[objetivo]
                else:
                    pregunta = f"How many {GEN.COLOR_EN[objetivo]} shapes are there in the image?"
                    objeto_point = f"{GEN.COLOR_EN[objetivo]} shapes"

                aisladas = figuras_aisladas(objetos)
                idx_obj = [i for i, o in enumerate(objetos) if o[clave] == objetivo]
                idx_otros = [i for i, o in enumerate(objetos) if o[clave] != objetivo]
                borrar = elegir(idx_obj, aisladas, 2, rng)
                control = elegir(idx_otros, aisladas, 1, rng)
                gt = conteos[objetivo]
                qid = f"q{len(preguntas):03d}"

                condiciones = {"c0": [], "c1": borrar[:1], "c2": borrar, "control": control}
                gt_cond = {"c0": gt, "c1": gt - 1, "c2": gt - 2, "control": gt}
                for cond, excluir in condiciones.items():
                    archivo = f"{qid}_{cond}.png"
                    dibujar(objetos, excluir=set(excluir)).save(SALIDA / "imagenes" / archivo)
                    imagenes.append(dict(qid=qid, condicion=cond, archivo=archivo, gt=gt_cond[cond]))

                np.savez_compressed(SALIDA / "etiquetas" / f"{qid}.npz",
                                    etiquetas=mapa_etiquetas(objetos))
                escenas[qid] = objetos
                preguntas.append(dict(
                    qid=qid, imagen_v2=nombre, num_shapes=nivel, tipo=tipo, objetivo=objetivo,
                    pregunta=pregunta, objeto_point=objeto_point, gt=gt,
                    borrada_c1=borrar[0], borradas_c2=";".join(map(str, borrar)),
                    borrada_control=control[0],
                    c1_aislada=aisladas[borrar[0]], c2_aisladas=all(aisladas[i] for i in borrar),
                    control_aislada=aisladas[control[0]]))

    from collections import Counter
    por_celda = Counter((p["num_shapes"], p["tipo"]) for p in preguntas)
    assert all(v == POR_NIVEL_Y_TIPO for v in por_celda.values()) and len(por_celda) == 2 * len(NIVELES), por_celda

    for nombre, filas in [("preguntas.csv", preguntas), ("imagenes.csv", imagenes)]:
        with open(SALIDA / nombre, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
    with open(SALIDA / "objetos.json", "w", encoding="utf-8") as f:
        json.dump(escenas, f, ensure_ascii=False)

    zip_salida = SALIDA.with_suffix(".zip")
    with zipfile.ZipFile(zip_salida, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta in sorted(SALIDA.rglob("*")):
            if ruta.is_file():
                z.write(ruta, ruta.relative_to(SALIDA.parent))
    print(f"{len(preguntas)} preguntas, {len(imagenes)} imágenes -> {zip_salida}")


if __name__ == "__main__":
    main()
