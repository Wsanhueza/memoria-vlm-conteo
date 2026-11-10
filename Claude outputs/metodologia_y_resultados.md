# Metodología y resultados — Evaluación de VLMs de escala pequeña en conteo visual y razonamiento espacial

Documento de apoyo para la memoria. Reúne, en un solo lugar y explicado de forma clara e intuitiva, cómo funciona cada pipeline, qué mide cada métrica, qué problemas se encontraron al ejecutar los modelos, y qué dicen los gráficos que ya se generaron. La idea es que sirva como base directa para redactar las secciones de metodología y resultados.

**Modelos evaluados** (los mismos cuatro en los tres benchmarks de la literatura y en el sintético):

| Nombre en los gráficos | Checkpoint real |
|---|---|
| InternVL2_1B | InternVL2-1B |
| moondream2 | moondream2 |
| paligemma2_3b | google/paligemma2-3b-mix-448 |
| qwen2_vl_2b | Qwen2-VL-2B-Instruct |

---

## 1. Cómo funciona cada pipeline (idea general)

Los tres benchmarks de la literatura (CAPTURe, TallyQA, OmniSpatial) y el benchmark sintético propio comparten la misma estructura de ejecución, un notebook de Google Colab por modelo y por benchmark (`piloto_<benchmark>_<modelo>.ipynb`):

1. **Carga del dataset**: se descarga o lee el dataset (desde HuggingFace en el caso de CAPTURe, o desde el generador propio en el caso del sintético).
2. **Muestreo**: se toma una muestra de *n* preguntas/imágenes (con semilla fija, `RANDOM_SEED`, para que la muestra sea reproducible y — en CAPTURe y TallyQA — la misma para los cuatro modelos).
3. **Construcción del prompt**: se arma la pregunta exacta que se le va a mostrar al modelo junto con la imagen.
4. **Inferencia**: el modelo recibe imagen + pregunta y genera una respuesta en texto libre (`model.generate`).
5. **Extracción de la respuesta**: se intenta leer un número (o una letra, en el caso de preguntas de opción múltiple) desde el texto que devolvió el modelo. Si no se puede extraer nada interpretable, la fila queda marcada `parse_fail = True`.
6. **Cálculo de métricas**: por fila se calcula el error (`error_abs`, `sMAPE`, etc.) y si acertó exactamente (`acierto_exacto` / `acierto`).
7. **Salida**: un CSV de detalle (una fila por pregunta, con todas las columnas anteriores) y un `.txt` de resumen con los números agregados.

Los cuatro CSV de detalle (uno por modelo) de cada benchmark son la fuente de datos de todos los gráficos que se describen más abajo — se generan directamente con Python (pandas + matplotlib), sin pasar por Power BI, aunque el contenido es equivalente al del dashboard.

---

## 2. CAPTURe

### 2.1. Qué mide el benchmark

CAPTURe (*Counting Amodal Patterns Through Unseen REgions*) le muestra al modelo una imagen con objetos ordenados en un patrón regular (grilla, círculo, fila), donde una parte de la imagen está tapada por un recuadro negro. La instrucción le pide al modelo que cuente el total de objetos **asumiendo que el patrón continúa detrás del recuadro** — es decir, no basta con contar lo visible, hay que inferir cuántos objetos hay escondidos. Esto se llama *amodal counting* (contar objetos que no se ven directamente, pero cuya existencia se infiere por el patrón).

El benchmark tiene dos partes:

- **`real`**: fotografías reales (vienen del dataset FSC-147), con un recuadro negro superpuesto manualmente. Objetos muy diversos (tazas, clavos, animales, etc.), conteos que van de unas pocas unidades a varios cientos.
- **`sintetico`**: imágenes generadas artificialmente (puntos o cuadrados de colores en patrones simples), donde el número de objetos y el número de objetos tapados están controlados por el generador del propio paper.

**Problema metodológico ya confirmado empíricamente**: el subset `real` **no trae ninguna columna de cantidad de objetos ocluidos** en sus metadatos originales (`real_metadata_df.columns = ['image_file', 'log_prob', 'density_map_sum', 'ground_truth', 'object', 'bbox']`). Esto se verificó corriendo una inspección temporal directamente en el notebook de Colab (con acceso real a HuggingFace, que desde este entorno de trabajo no es alcanzable). Por eso el pipeline deja `num_occluded = None` para las filas `real` — no es un error, es una limitación real del dataset original, y así debe quedar documentado: **el análisis por cantidad de objetos ocluidos solo es posible en el subset sintético**, no en el real.

### 2.2. Métrica: sMAPE

El paper de CAPTURe usa **sMAPE** (*symmetric Mean Absolute Percentage Error*) como métrica principal, en vez de accuracy o error absoluto puro. La fórmula es:

```
sMAPE = 100 · (1/n) · Σ |real_i − predicho_i| / (|real_i| + |predicho_i|)
```

**Intuición**: es un error relativo, expresado en porcentaje, que compara cuánto se equivocó el modelo en proporción al tamaño de la respuesta correcta — no en términos absolutos. Equivocarse por 5 cuando la respuesta correcta es 10 (sMAPE alto, ~50%) es un error mucho más grave que equivocarse por 5 cuando la respuesta correcta es 300 (sMAPE bajo, ~1.6%), aunque el error absoluto (`error_abs`) sea el mismo en ambos casos. Por eso sMAPE es más justo para comparar el desempeño entre imágenes con pocos objetos y con muchos — algo que el error absoluto por sí solo no logra, porque una suma de errores absolutos queda dominada por las imágenes con más objetos, sin que eso signifique que el modelo "entiende peor" esas imágenes.

### 2.3. Rango_Objetos: por qué existe y por qué esos rangos específicos

Para poder graficar "¿el error crece con la cantidad de objetos?" en el subset `real`, se agruparon las imágenes en 4 categorías (Chico, Mediano, Grande, Masivo) usando cuartiles (`pd.qcut`, que corta los límites para que cada grupo tenga la misma cantidad de imágenes).

**Esto no es una técnica del paper de CAPTURe.** El paper solo hace este tipo de análisis (error vs. cantidad de objetos) en el subset *sintético* (su Figura 6), donde el número de objetos es una variable controlada con solo 11 valores posibles (5 a 15) y bastantes imágenes por valor — no necesitan agrupar. En el subset real, el conteo correcto va de 8 hasta 501 objetos, con **59 valores distintos** en una muestra de 100 imágenes (la mayoría de esos valores solo aparece 1 o 2 veces). Graficar el error contra el valor exacto, como hace el paper en el sintético, sería ilegible acá. Por eso se optó por cuartiles: agrupar por cantidad igual de imágenes por grupo, en vez de por ancho fijo de rango — de ahí que "Chico" sea un rango angosto (8-17) y "Masivo" uno enorme (76-501): la distribución real está muy concentrada en conteos bajos.

**Conclusión para la memoria**: esta bucketización es una decisión metodológica propia (una técnica estadística estándar — binning por cuartiles — aplicada a un problema que el paper no resuelve), no algo tomado del paper original. Debe quedar explícito así en el texto.

### 2.4. num_occluded

Es el número de objetos que, en una imagen del subset sintético, quedan tapados por el recuadro negro (solo existe para `sintetico`, por la razón explicada en 2.1). Es el corazón de lo que CAPTURe intenta medir: si el modelo puede inferir cuántos objetos hay detrás del recuadro, no solo contar lo visible.

### 2.5. Problema encontrado: paligemma2_3b se niega a responder más de la mitad de las veces

Al revisar por qué paligemma2_3b mostraba "menos error total" en algunos gráficos pese a tener casi 0% de acierto exacto, se encontró que **108 de sus 200 respuestas (54%) son `parse_fail`** — el modelo no da ningún número. Desglosando por subset:

- **`real` (39/100 fallos)**: el 100% de esos fallos es literalmente el mismo texto: *"Sorry, as a base VLM I am not trained to answer this question."*
- **`sintetico` (69/100 fallos)**: mayormente *"unanswerable"* (61 casos), más algunas descripciones sin número.

Se confirmó que el notebook carga el checkpoint correcto (`google/paligemma2-3b-mix-448`, no la versión base). La explicación más probable es de **formato de prompt**: los prompts oficiales de CAPTURe son instrucciones largas y en lenguaje libre (ej. *"Count the exact number of oranges in the image. Assume the pattern of oranges continues behind any black box..."*), mientras que paligemma2_3b es un modelo chico entrenado sobre todo con prompts cortos y templados — es conocido en la literatura por ser menos robusto que modelos como InternVL2/Qwen2-VL ante instrucciones largas.

**Consecuencia para el análisis**: las comparaciones de error total (`Suma de error_abs`) entre modelos en CAPTURe **no están hechas sobre la misma cantidad de respuestas válidas** — paligemma2_3b solo aporta 92 filas contra las ~197-199 de los demás. Cualquier comparación de error acumulado entre modelos debe ir acompañada del % de `parse_fail` por modelo, o el lector puede interpretar "menor error total" como "más preciso", cuando en realidad es "respondió a mucho menos preguntas".

### 2.6. Resultados de los 6 gráficos (`graficos_capture/`)

1. **`1_error_abs_por_modelo_subset.png`** — Suma de error_abs por modelo y subset. InternVL2_1B acumula el error más alto en ambos subsets; paligemma2_3b el más bajo — pero por la razón de 2.5 (responde muchas menos preguntas), no por ser más preciso.
2. **`2_smape_por_modelo_subset.png`** — sMAPE promedio por modelo y subset (métrica relativa, corrige el sesgo del gráfico 1). InternVL2_1B es el peor en ambos subsets (~65% sMAPE), moondream2 el mejor en sintético (~24%), paligemma2_3b/qwen2_vl_2b quedan en un rango intermedio (~40-49%).
3. **`3_error_abs_por_rango.png`** — Suma de error_abs por Rango_Objetos. Crece fuerte con la magnitud de objetos (esperable — confunde escala con precisión, ver 2.2), paligemma2_3b queda más bajo pero de nuevo por el sesgo de 2.5.
4. **`4_parse_fail_por_modelo.png`** — Cantidad de parse_fail por modelo. paligemma2_3b muy por encima del resto (ver 2.5); moondream2 con un nivel intermedio (~44/200); InternVL2_1B y qwen2_vl_2b prácticamente sin fallos.
5. **`5_pct_acierto_por_rango.png`** — % de acierto exacto por Rango_Objetos. Ningún modelo supera ~20% en el rango más fácil ("Chico"), y todos caen a 0% desde "Grande" en adelante. Revisando el detalle del bucket "Chico" (25 imágenes iguales para los 4 modelos): moondream2 acierta 5/25 (20%), InternVL2_1B 4/25 (16%), qwen2_vl_2b 3/25 (12%) — pese a que qwen2_vl_2b es el mejor en sMAPE. La razón: acierto_exacto es todo-o-nada (estar a 1 de diferencia vale lo mismo que estar a 15), mientras sMAPE da crédito parcial por estar cerca; qwen2_vl_2b tiende a "anclarse" en números redondos (ej. responde "10" muy seguido), lo que le da buen sMAPE pero pocos aciertos exactos. Con solo 25 imágenes por bucket, además, la diferencia entre 12% y 20% son apenas 2 respuestas — no es una diferencia estadísticamente robusta.
6. **`6_smape_por_num_occluded.png`** — sMAPE promedio por num_occluded (solo aplica al subset sintético). Es ruidoso a partir de num_occluded≥5: la mayoría de las imágenes sintéticas tapan solo 1 o 3 objetos (~38-39 imágenes por modelo en esos niveles); en niveles altos (7, 9, 10) hay literalmente **una sola imagen por modelo**, así que esos puntos del gráfico no representan una tendencia real, solo el resultado de un único intento. Solo el tramo 1-3 tiene suficientes datos para ser interpretado con confianza.

---

## 3. TallyQA

### 3.1. Qué mide el benchmark

TallyQA es un benchmark de conteo por VQA (Visual Question Answering): se le hacen al modelo preguntas tipo *"How many X are there?"* sobre fotos reales. El propio dataset clasifica cada pregunta en dos tipos (`issimple`, heredado del paper original, no es una categoría inventada en este trabajo):

- **`issimple = True` (simple)**: conteo directo de una categoría, ej. *"How many umbrellas are there?"*
- **`issimple = False` (compleja)**: requiere un filtro adicional antes de contar, ej. *"How many people are cooking food near the window?"*

### 3.2. Métricas: MAE, RMSE y accuracy

El paper de TallyQA reporta accuracy y **RMSE** (*Root Mean Squared Error*) por split (Test-Simple / Test-Complex), no solo accuracy — se replicó ese mismo formato (Tabla 3 del paper).

```
RMSE = raíz( promedio( error² ) )
```

**Intuición**: a diferencia del MAE (que promedia el tamaño del error tal cual), el RMSE **eleva cada error al cuadrado antes de promediar**. Elevar al cuadrado hace que los errores grandes pesen desproporcionadamente más que los chicos — un solo error enorme puede dominar el RMSE aunque el resto de las respuestas sean casi perfectas. Por eso, cuando el RMSE de un modelo es mucho más alto que su MAE, es una señal de que tiene uno o pocos errores puntuales muy grandes, no un error moderado y parejo en todas las preguntas.

### 3.3. Rango_GT: qué es y por qué esos grupos

"GT" es *ground truth* — la respuesta correcta. Rango_GT agrupa las preguntas **según cuál era el número correcto** (no según si son simples o complejas — es un eje de análisis distinto), para responder: ¿el modelo se equivoca más cuando la respuesta correcta es un número más grande?

Los grupos usados son "0", "1", "2", "3-5", "6+". Se eligieron así porque el 87% de las preguntas del dataset tienen respuesta correcta 0, 1 o 2 (muy común en VQA: muchas preguntas terminan en "no hay ninguno" o "hay uno"), así que esos tres valores se dejaron individuales, con harta muestra cada uno. Los conteos altos (7 en adelante) son raros (3-4 preguntas cada uno), así que agruparlos en "3-5" y "6+" evita puntos del gráfico sostenidos por un puñado de preguntas. **Tampoco es una técnica del paper** — el paper de TallyQA solo reporta el desglose simple/complejo, no por magnitud del conteo; es, igual que Rango_Objetos en CAPTURe, una adaptación propia para visualizar una tendencia.

### 3.4. Problema encontrado: el RMSE de paligemma2_3b en preguntas complejas es un solo dato, no un patrón

El gráfico de RMSE mostraba a paligemma2_3b con un RMSE de ~30 en preguntas complejas, muy por encima de todos los demás modelos/splits (<1.2). Se revisó fila por fila y el resultado quedó aislado a **una sola pregunta** de 121: *"How many yellow numbers on the far green wall are odd?"* (respuesta correcta: 2), donde el modelo respondió **330** — una alucinación puntual, no un fallo de parseo (`respuesta_cruda` y `prediccion` coinciden en 330).

Se recalculó el RMSE sacando esa única fila:

| | Con el outlier | Sin el outlier |
|---|---|---|
| MAE (complejas) | 3.31 | 0.60 |
| RMSE (complejas) | 29.84 | 1.17 |

Sin esa fila, paligemma2_3b queda en línea con los demás modelos. Es un buen ejemplo concreto, para la memoria, de por qué RMSE es sensible a outliers de una forma que MAE no lo es — vale la pena reportar ambos valores (con y sin el caso extremo) en vez de solo el RMSE crudo.

### 3.5. Estado de las muestras (n) por modelo

InternVL2_1B y moondream2 están ejecutados a n=300. paligemma2_3b **ya fue re-ejecutado a n=300** (121 complejas + 179 simples, confirmado en los datos más recientes). qwen2_vl_2b sigue pendiente en n=50 — el usuario está evaluando volver a ejecutarlo a n=300.

### 3.6. Resultados de los 5 gráficos (`graficos_tallyqa/`)

1. **`1_error_abs_por_modelo_issimple.png`** — Suma de error_abs por modelo e issimple. **Cuidado al leerlo**: es una suma, no un promedio, y mientras qwen2_vl_2b siga en n=50 (contra n=300 del resto), sus barras se ven artificialmente más bajas solo por tener menos filas sumadas — no comparar directamente hasta emparejar las muestras.
2. **`2_pct_acierto_por_issimple.png`** — % de acierto exacto por modelo e issimple. Todos los modelos aciertan más en preguntas simples que en complejas (confirma que la distinción simple/compleja del dataset representa dificultad real). paligemma2_3b es el que más cae en complejas (45%, el más bajo de los cuatro) — consistente con el hallazgo de 3.4.
3. **`3_promedio_error_abs_por_rango_gt.png`** — Promedio de error_abs por Rango_GT. Error bajo y parejo en 0, 1 y 2 (donde está la mayoría de las preguntas), crece en 3-5 y sobre todo en 6+ — coherente con que contar más es más difícil, aunque en 6+ hay pocas preguntas por modelo (más aún en qwen2_vl_2b/paligemma2_3b), así que ese extremo hay que leerlo con cautela.
4. **`4_pct_acierto_por_rango_gt.png`** — % de acierto exacto por Rango_GT. qwen2_vl_2b cae a 0% en "6+" después de ser el mejor en todos los rangos anteriores — con qwen2_vl_2b en n=50 total, es muy probable que ese bucket tenga solo 1-2 preguntas, así que no se puede leer como "el modelo colapsa con conteos altos" hasta reejecutar a n=300.
5. **`5_rmse_por_modelo_issimple.png`** — RMSE por modelo e issimple. Ver 3.4 — el pico de paligemma2_3b es un outlier de una sola pregunta, no un patrón sistemático.

---

## 4. OmniSpatial

### 4.1. Qué mide el benchmark, y qué parte se usó realmente

OmniSpatial es un benchmark grande de razonamiento espacial, organizado en **4 categorías principales y 50 subtipos específicos** en total (Dynamic Reasoning: Manipulation/Motion Analysis; Complex Spatial Logic: Pattern Recognition/Geometric Reasoning; Spatial Interaction: Locate/Geospatial Strategy/Traffic Analysis; Perspective-Taking: Egocentric/Allocentric/Hypothetical).

**Este trabajo evalúa solo 4 de esos 50 subtipos** (Geometric_Reasoning, Motion_Analysis, Egocentric, Allocentric), que además pertenecen a 3 de las 4 categorías principales (no incluye nada de Spatial Interaction). **Esto debe quedar explícito en el texto de la memoria**: los resultados hablan de esos 4 "tracks" puntuales, no del benchmark OmniSpatial completo — presentarlo como "evaluamos OmniSpatial" sin esta aclaración sería engañoso respecto al alcance real de la evaluación.

### 4.2. baseline_azar

Es el porcentaje de acierto que lograría alguien **respondiendo al azar**, calculado como el promedio de `1/número_de_opciones` de las preguntas de cada track. Depende únicamente del dataset (cuántas alternativas tiene cada pregunta), no del modelo — por eso es idéntico para los 4 modelos evaluados. Sirve como piso de comparación: un modelo que responde cerca del baseline_azar no está demostrando razonamiento real en ese track, está adivinando. Valores usados: Geometric_Reasoning=27%, Motion_Analysis=31%, Egocentric=36%, Allocentric=28%.

### 4.3. Resultados de los 4 gráficos (`graficos_omnispatial/`)

1. **`1_pct_acierto_por_track.png`** — % de acierto por track y modelo, con el baseline_azar superpuesto. **Geometric_Reasoning es el track más débil**: InternVL2_1B (25%) y paligemma2_3b (25%) están prácticamente empatados con el azar (27%) — no muestran razonamiento geométrico real en este track; solo qwen2_vl_2b (35%) se despega un poco. **Egocentric es donde los 4 modelos muestran capacidad real** (49%-60%, muy por encima del 36% de azar). En Allocentric, moondream2 (27%) queda por debajo del baseline (28%) — ahí adivinar al azar le habría ido mejor que responder de verdad.
2. **`2_pct_parse_fail_por_track.png`** — Casi vacío en general (buena señal), salvo **InternVL2_1B en Motion_Analysis: 23% de parse_fail**. Se revisaron esas filas: son preguntas de opción múltiple tipo *"Si el bus llega al fotógrafo en 2 s, ¿cuál es su velocidad?"*, y en vez de elegir una de las alternativas dadas (una letra), InternVL2_1B se pone a hacer el cálculo matemático en texto libre (ej. *"The speed of the bus is 0.36m/s."*), sin ninguna letra que el parser pueda extraer. No es un error del pipeline: es que el modelo no está respetando el formato de opción múltiple en ese track específico.
3. **`3_pct_acierto_global.png`** — Ranking general: qwen2_vl_2b (43%) ≈ paligemma2_3b (42%) > moondream2 (37%) > InternVL2_1B (35%). A diferencia de los benchmarks de conteo, acá la diferencia entre modelos es chica (8 puntos de rango) — ninguno se despega claramente del resto.
4. **`4_geometric_con_sin_opciones.png`** — Compara, dentro de Geometric_Reasoning, acierto con preguntas de opción múltiple (`con_opts`) vs. abiertas (`sin_opts`). paligemma2_3b y qwen2_vl_2b parecen empeorar con opciones, pero **la muestra de `con_opts` es de solo 14 preguntas** (contra 86 de `sin_opts`) — con una base tan chica, la diferencia no es confiable y no debería presentarse como un hallazgo real sin ampliar esa muestra.

---

## 5. Benchmark sintético 2D (generador propio)

### 5.1. Motivación

Los tres benchmarks anteriores usan datos reales o semi-controlados, con distribuciones heterogéneas de cantidad de objetos (sobre todo CAPTURe-real, que va de 8 a 501). Eso dificulta sacar conclusiones limpias sobre "¿cómo se comporta la precisión del modelo a medida que aumenta estrictamente la cantidad de elementos?", porque el conteo no es una variable controlada — se mezcla con el tipo de objeto, el contexto de la foto, etc.

El generador sintético 2D nace para resolver eso: crea imágenes con figuras geométricas simples (círculos, cuadrados, triángulos, de distintos colores) donde **la cantidad de figuras es una variable controlada por el propio generador**, permitiendo aislar el efecto de la cantidad de elementos sobre la precisión del modelo, sin la heterogeneidad de un dataset real. Es, en ese sentido, el benchmark con mejor capacidad de mostrar una curva de dificultad limpia — pero, como se discutió en el chat, sus métricas solo son comparables de forma referencial con las de CAPTURe/TallyQA/OmniSpatial, porque estos últimos evalúan tareas y distribuciones distintas y no fueron diseñados en función de "cantidad controlada de elementos".

### 5.2. Diseño del dataset y tipos de pregunta

Cada imagen sintética varía en `num_shapes` (cantidad de figuras) y se le hacen 4 tipos de pregunta (`tipo_pregunta`):

- `conteo_general`: cuántas figuras hay en total.
- `conteo_forma`: cuántas figuras de una forma específica hay.
- `conteo_color`: cuántas figuras de un color específico hay.
- `conteo_combinado`: cuántas figuras de una forma **y** color específicos hay.

**Limitación conocida, aún no corregida**: el dataset compartido por los 4 modelos se generó con solo **5 imágenes por nivel de `num_shapes`**, en vez de las 30 que se habían acordado como objetivo. Esto es la causa directa del ruido visible en el gráfico 2 (ver 5.4) — con tan pocas imágenes por punto, el resultado es muy sensible a 1-2 aciertos/fallos puntuales. Regenerar el dataset con `imgs_por_lote=30` es la mejora pendiente de mayor impacto para esta parte del trabajo.

### 5.3. Métrica: sMAPE

Se usa la misma métrica sMAPE que en CAPTURe (ver 2.2), por la misma razón: el error absoluto crudo queda sesgado por el tipo de pregunta (`conteo_general` permite ground_truth hasta 100, mientras que `conteo_forma`/`conteo_color`/`conteo_combinado` casi siempre dan números chicos), así que el error absoluto de `conteo_general` domina cualquier gráfico de suma sin que eso signifique necesariamente que el modelo "entiende peor" esa tarea específica.

### 5.4. Resultados de los 5 gráficos (`graficos_sintetico/`)

1. **`1_error_abs_por_modelo_tipo.png`** — Suma de error_abs por modelo y tipo_pregunta. `conteo_general` domina el total en los 4 modelos (por el sesgo de escala explicado en 5.3); qwen2_vl_2b tiene el menor error acumulado.
2. **`2_pct_acierto_por_num_shapes.png`** — % de acierto exacto por num_shapes. Es un zigzag sin tendencia clara — consecuencia directa de la limitación de 5.2 (solo 5 imágenes por nivel), no un comportamiento real del modelo.
3. **`3_promedio_error_abs_por_num_shapes.png`** — Promedio de error_abs por num_shapes. Al usar promedio en vez de %, el ruido baja bastante y aparece una tendencia clara y creciente: qwen2_vl_2b se mantiene con el error más bajo y plano; InternVL2_1B y moondream2 son los peores y quedan casi empatados; paligemma2_3b queda al medio pero diverge hacia arriba después de num_shapes≈35.
4. **`4_pct_acierto_por_tipo.png`** — % de acierto exacto por tipo_pregunta. InternVL2_1B colapsa casi a 0% en `conteo_combinado`; paligemma2_3b es ahí el mejor (~34%) y también el mejor en `conteo_color` — su comportamiento depende mucho del tipo de pregunta, no es "malo en general" como podría sugerir capture.
5. **`5_smape_por_num_shapes.png`** — sMAPE por num_shapes. **Hallazgo clave, invierte el ranking del gráfico 3**: en términos relativos, qwen2_vl_2b es claramente el mejor (~15-25% sMAPE en todo el rango), mientras que paligemma2_3b — que en el gráfico 3 (error absoluto) parecía "estabilizarse bien" — es en realidad el peor a alta densidad de figuras (~50-60% sMAPE). Es la evidencia más concreta, dentro de todo lo analizado, de que la métrica elegida (absoluta vs. relativa) puede cambiar la conclusión sobre qué modelo es "mejor".

---

## 6. Limitaciones metodológicas transversales (para dejar explícitas en la memoria)

- **Las bucketizaciones por rango (`Rango_Objetos` en CAPTURe, `Rango_GT` en TallyQA) son adaptaciones propias**, no técnicas descritas en los papers originales — necesarias porque los datasets reales tienen distribuciones muy heterogéneas de conteo, a diferencia de los subsets sintéticos controlados que sí analizan los papers.
- **OmniSpatial solo se evaluó en 4 de sus 50 subtipos** (3 de sus 4 categorías principales) — los resultados no representan el desempeño en el benchmark completo.
- **La comparación de métricas entre CAPTURe/TallyQA/OmniSpatial y el benchmark sintético es solo referencial**: los primeros tres evalúan distribuciones reales/heterogéneas con sus propias métricas de paper; el sintético fue diseñado específicamente en función de una "cantidad controlada de elementos" que los otros tres no comparten.
- **Las comparaciones de error/accuracy entre modelos no siempre están hechas sobre el mismo n**: en CAPTURe, por la tasa de `parse_fail` muy distinta entre modelos (paligemma2_3b 54% vs. ~1% del resto); en TallyQA, porque qwen2_vl_2b aún corre a n=50 mientras el resto corre a n=300. Cualquier comparación de sumas (no promedios/porcentajes) debe leerse con esto en cuenta.
- **Cuidado con las conclusiones basadas en muestras chicas**: varios puntos puntuales de los gráficos (num_occluded≥5 en CAPTURe, `con_opts` en Geometric_Reasoning de OmniSpatial, el bucket "6+" de TallyQA para los modelos con n=50, y el gráfico 2 completo del sintético) dependen de muy pocas observaciones y no deberían presentarse como hallazgos robustos sin más datos.

---

## 7. Pendientes identificados

- Reejecutar TallyQA para qwen2_vl_2b a n=300 (en curso, a cargo del usuario).
- Regenerar el dataset sintético 2D compartido con `imgs_por_lote=30` (actualmente 5) — mejora de mayor impacto pendiente para el benchmark sintético.
- Evaluar extender `figuras_max` más allá de 100 en el generador sintético, para probar si hay un efecto de "anclaje al techo" del benchmark (modelos adivinando cerca del máximo conocido).
- Otros ajustes del generador sintético discutidos: tamaño de figuras/canvas a alta densidad (legibilidad visual), balance de color/forma entre las 32 combinaciones, y posible re-ponderación hacia más preguntas `conteo_general` por imagen.
- Corregir en el texto de la memoria el alcance real de OmniSpatial (4/50 subtipos, no el benchmark completo).
- Corrección de Power Query (tipo de columna `respuesta_cruda`) en el archivo de Power BI — quedó documentada la causa y la solución, no es prioridad mientras los gráficos en Python sigan funcionando.
