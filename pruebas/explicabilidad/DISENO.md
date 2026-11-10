# Diseño del experimento de explicabilidad

*Congelado el 10-11-2026, antes de ejecutar ningún modelo. Cualquier cambio posterior se anota en la sección 9, con fecha y motivo.*

## 1. Pregunta

¿moondream2 **cuenta** las figuras de la imagen, o responde con una heurística (un número favorito, una estimación de densidad)?

## 2. Técnicas

| Técnica | Pregunta que responde | Tipo | Notebook |
|---|---|---|---|
| Oclusión | ¿la respuesta cambia al borrar figuras objetivo? (causa-efecto) | conducta | `01_conducta_moondream2.ipynb` |
| Grounding (`point()`) | ¿el modelo localiza las figuras objetivo cuando se le pide? | conducta | `01_conducta_moondream2.ipynb` |
| Attention rollout | ¿qué parches pesan en el encoder visual? (no depende de la pregunta) | interna | `02_rollout` (pendiente) |
| Grad-CAM | ¿qué parches influyen en la respuesta a esta pregunta? | interna | `03_gradcam` (pendiente) |

Modelo: `vikhyatk/moondream2`, revisión `2025-06-21`, bfloat16, `transformers==4.46.3`.

Por qué moondream2: tiene una grilla fija de 27 × 27 tokens visuales, no duplica tokens entre recortes, trae `point()` incorporado y su código ya está instrumentado. En explicabilidad se elige el modelo que se puede inspeccionar, no necesariamente el de mejor rendimiento.

## 3. Imágenes

**Origen.** Dataset sintético v2 (`benchmark_2d_sintetico_lotes_2400_v2.zip`). Las imágenes se regeneran con el generador original (`benchmark_sintetico/2D.py`) para recuperar la posición de cada figura. Parámetros de v2, comprobados regenerando las 600 imágenes idénticas píxel a píxel: lienzo de 1024 px, figura de 35 px, solapamiento máximo del 30 %, borde de 2 px, semilla 42 + número de imagen.

**Niveles.** 15, 25, 35, 45 y 55 figuras por imagen. Es la zona en que el acierto de moondream2 cae (≈60 % con 5–10 figuras, 10–20 % desde 15).

**Preguntas.** Solo `conteo_forma` y `conteo_color`, y solo con respuesta correcta entre 2 y 10. La forma o el color objetivo se sortea entre los que cumplen esa regla. Se excluyen:
- `conteo_general`, porque no hay figuras no objetivo para el control;
- `conteo_combinado`, porque casi siempre tiene respuesta 0 o 1.

**Muestra.** 12 imágenes por nivel y tipo de pregunta, sorteadas con semilla 2026. Cada imagen se usa en un solo tipo. Total: 5 × 2 × 12 = **120 preguntas**.

**Condiciones por pregunta**, todas redibujadas desde la lista de figuras (no se pinta encima):

| Condición | Qué se borra | Respuesta correcta |
|---|---|---|
| `c0` | nada (idéntica al original) | GT |
| `c1` | 1 figura objetivo | GT − 1 |
| `c2` | 2 figuras objetivo (incluye la de `c1`) | GT − 2 |
| `control` | 1 figura no objetivo | GT |

Se prefieren figuras que no tocan a ninguna otra; en la muestra final fue así en el 100 % de `c1` y `control` y en el 99 % de `c2`.

Lo genera `preparar_conjunto.py`, que escribe `conjunto_v2.zip` con: las imágenes, `preguntas.csv`, `imagenes.csv`, `objetos.json` (posición de cada figura) y `etiquetas/` (mapa de qué figura se ve en cada píxel, para las métricas).

## 4. Cómo se le pregunta al modelo

- `query(imagen_codificada, pregunta + " Respond with only the integer number.", settings={"temperature": 0, "max_tokens": 16})`. Temperatura 0 = sin azar; se comprueba repitiendo 10 preguntas.
- `point(imagen_codificada, objeto, settings={"max_objects": 100})`, con objeto = `"circles"`, `"red shapes"`, etc. Solo en `c0`.
- Lectura del número: el primer entero de la respuesta, ignorando marcadores de lista. Sin entero = formato inválido.

## 5. Grupos (según la respuesta en `c0`)

| Grupo | Regla |
|---|---|
| Acierto | \|predicción − GT\| = 0 |
| Error cercano | \|predicción − GT\| = 1 o 2 |
| Error lejano | \|predicción − GT\| ≥ 3 |
| Formato inválido | no se pudo leer un número |

Columna aparte: `numero_favorito` = la predicción es 10 o 100.

**Muestra para los mapas (rollout y Grad-CAM):** 20 preguntas, 5 por grupo, sorteadas con semilla 2026 entre las 120. Si un grupo tiene menos de 5, lo que falta se reparte en orden entre acierto, cercano y lejano. Además van 2 imágenes de control: una completamente gris (fondo 200) y una de ruido.

**Ejemplos para la memoria:** el primer caso de cada grupo según el orden del sorteo.

## 6. Métricas

**Oclusión.** Δ1 = pred(c1) − pred(c0), Δ2 = pred(c2) − pred(c0), Δcontrol = pred(control) − pred(c0). Cada pregunta cae en una categoría:
- **reacciona como si contara:** Δ1 = −1, Δ2 = −2 y Δcontrol = 0;
- **dirección correcta:** Δ2 < 0 y Δ2 ≤ Δ1 ≤ 0, sin ser la anterior;
- **no reacciona:** Δ1 = Δ2 = 0;
- **inespecífica:** Δcontrol ≠ 0 (se reporta aparte);
- **otra:** cualquier otro caso.

Además, la **pendiente**: ajuste lineal de la predicción contra figuras borradas (0, 1, 2). Lo ideal es −1. Todo se reporta por nivel, por tipo de pregunta y por grupo.

**Grounding.**
- n.º de puntos vs. GT vs. predicción de `query()`;
- precisión: % de puntos que caen sobre una figura objetivo;
- cobertura: % de figuras objetivo con al menos un punto.

**Mapas (rollout, Grad-CAM).**
- *Enriquecimiento*: fracción del mapa (normalizado a suma 1) que cae sobre las figuras objetivo, dividida por la fracción del área que ocupan. 1 = no las distingue del fondo.
- Lo mismo para las figuras no objetivo, como comparación.
- Sinks: si los puntos más altos del mapa caen en las mismas posiciones en la imagen gris.

**Incertidumbre.** Porcentajes con IC 95 % de Wilson. Con 120 preguntas, el margen es de unos ±9 puntos.

## 7. Lectura de resultados

| ¿Localiza? (grounding) | ¿La respuesta reacciona? (oclusión) | Conclusión |
|---|---|---|
| sí | sí | cuenta, al menos en este rango |
| sí | no | ve, pero no agrega bien el conteo |
| no | sí | usa una señal parcial o difusa |
| no | no | heurística |

## 8. Límites que se declaran

- Un solo modelo para los mapas; la oclusión en los otros 3 modelos queda para después, si hay tiempo.
- Conteos bajos (2–10) y figuras de 35 px, más chicas que un token de moondream2 (~38 px). Por eso los mapas serán gruesos. Más adelante se repetirá con figuras más grandes.
- `point()` es una habilidad distinta de `query()`.
- Solo imágenes sintéticas.

## 9. Cambios respecto al plan del 10-11

- La oclusión se corre sobre las **120 preguntas** y no sobre 80: cuesta ~10 minutos más y da más precisión.
- La preparación de imágenes se hace fuera de Colab (`preparar_conjunto.py`). Así Colab solo hace preguntas, y las imágenes no dependen de la versión de Pillow de Colab.

### Anotaciones después de la corrida 01 (10-11-2026)

Las reglas no cambiaron. Se dejan anotadas cuatro cosas observadas:
- **No hubo respuestas con formato inválido.** El grupo "invalido" quedó vacío, así que la muestra de 20 para los mapas quedó en 7 aciertos, 7 errores cercanos y 6 errores lejanos (regla de reparto de la sección 5).
- **"Número favorito" (10 o 100) no aparece.** Las respuestas en c0 usan solo los valores 1, 2, 3, 4 y 6, con techo en 6. Se reporta como hallazgo; la columna `numero_favorito` se mantiene tal como se definió.
- **Grounding:** 2 de 120 llamadas a `point()` llegaron al tope de 100 puntos (salida degenerada). Se informan aparte.
- **Determinismo:** `info_corrida.json` registra 0/10 por un error de tipos en la celda de verificación. Repetido con la celda corregida, dio 10/10.
