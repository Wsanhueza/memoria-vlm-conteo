# Evaluación de VLMs de Escala Pequeña en Conteo Visual y Razonamiento Espacial

**Memoria de Título — Ingeniería Civil Informática, Universidad Técnica Federico Santa María**
**Autor:** Walter Sanhueza · **Profesor guía:** Rodrigo Verschae · **Plazo:** 5 meses

> Este documento es la única fuente de verdad del proyecto (reemplaza a `CLAUDE.md` y
> `PROPUESTAS_Y_EXTRAS.md`, que quedaron desactualizados y se eliminaron). Sirve tanto para
> orientarte a ti mismo al volver después de un tiempo, como para cualquier agente de IA que
> retome una tarea puntual. Prioriza la estructura real del proyecto y el estado actual por
> sobre la narrativa — para resultados numéricos detallados, ver la memoria (`borrador_memoria_ICI.docx`)
> o el documento de metodología y resultados.

---

## Índice

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Pregunta de investigación](#2-pregunta-de-investigación)
3. [Modelos evaluados](#3-modelos-evaluados)
4. [Benchmarks](#4-benchmarks)
5. [Metodología del pipeline común](#5-metodología-del-pipeline-común)
6. [Infraestructura: Google Colab + T4](#6-infraestructura-google-colab--t4)
7. [Estructura del repositorio — actual](#7-estructura-del-repositorio--actual)
8. [Estructura del repositorio — objetivo (incluye explicabilidad)](#8-estructura-del-repositorio--objetivo-incluye-explicabilidad)
9. [Estado actual del proyecto](#9-estado-actual-del-proyecto)
10. [Explicabilidad](#10-explicabilidad)
11. [Pendientes priorizados](#11-pendientes-priorizados)
12. [Posibles extensiones futuras](#12-posibles-extensiones-futuras)
13. [Notas técnicas críticas](#13-notas-técnicas-críticas)
14. [Reproducibilidad](#14-reproducibilidad)

---

## 1. Descripción del proyecto

Este proyecto evalúa cuatro modelos de Visión y Lenguaje (*Vision-Language Models*, VLMs) de
**escala pequeña** (1–3B parámetros) en dos capacidades cognitivas: **conteo visual** y
**razonamiento espacial**. La evaluación es zero-shot (sin fine-tuning) sobre tres benchmarks
públicos de la literatura más un cuarto benchmark sintético propio, diseñado específicamente
para aislar el efecto de variables que los benchmarks externos no controlan (cantidad exacta
de elementos, tipo de pregunta).

El trabajo se inscribe en un contexto donde los modelos grandes de frontera (GPT-4o, Gemini,
Qwen-VL2.5-72B) alcanzan buen desempeño en razonamiento visual. La pregunta que motiva el
estudio es si esa capacidad es escalable hacia abajo, o si los modelos pequeños fallan de
forma sistemática y predecible que revela limitaciones arquitectónicas o de entrenamiento.

Incluye además una fase de **explicabilidad visual**, que ya se ejecutó sobre moondream2 y
produjo un hallazgo relevante (ver sección 10).

---

## 2. Pregunta de investigación

> **¿Los VLMs de escala pequeña construyen una representación espacial coherente del mundo,
> o responden por sesgos estadísticos aprendidos en entrenamiento (heurísticas, anclaje,
> memorización de patrones), más que por percepción/razonamiento genuino?**

Se mide en dos ejes:

- **Eje 1 — Conteo visual:** ¿puede el modelo contar objetos cuando hay oclusión, alta
  densidad, o variación de tipo/color? ¿Existe un "techo de respuesta" o un "anclaje" a
  ciertos valores, evidencia de atajo estadístico antes que de conteo genuino?
- **Eje 2 — Razonamiento espacial:** ¿puede el modelo responder preguntas que requieren
  inferencia sobre posición relativa, perspectiva (egocéntrica vs. alocéntrica), y
  razonamiento geométrico?
- **Explicabilidad (transversal):** ¿los mapas de atención del modelo coinciden con las
  regiones relevantes de la imagen, o reflejan otra cosa (p. ej. artefactos posicionales)?

---

## 3. Modelos evaluados

| Modelo | Parámetros | Arquitectura base | Checkpoint HF |
|---|---|---|---|
| **Moondream2** | 1.8B | SigLIP + Phi-1.5 | `vikhyatk/moondream2` (rev. `2025-06-21`) |
| **Qwen2-VL-2B-Instruct** | 2B | Qwen2 + ViT dinámico | `Qwen/Qwen2-VL-2B-Instruct` |
| **InternVL2-1B** | 1B | InternViT + InternLM | `OpenGVLab/InternVL2-1B` |
| **PaliGemma2-3B-mix-448** | 3B | SigLIP + Gemma2 | `google/paligemma2-3b-mix-448` |

Cada modelo requiere una versión de `transformers` distinta e incompatible con las demás —
ver sección 14. Cada uno corre en su propia sesión de Colab independiente.

---

## 4. Benchmarks

Cuatro benchmarks en total: tres de la literatura (conteo y razonamiento espacial) y uno
sintético propio.

### 4.1 CAPTURe — conteo con oclusión

**Fuente:** Paiss et al., 2023 · HF Hub `atinp/CAPTURe`. Muestra una imagen con una parte
tapada por un recuadro negro y pide contar asumiendo que el patrón continúa detrás
(*amodal counting*). Dos subsets: `real` (fotografías de FSC-147, sin columna de objetos
ocluidos en los metadatos — limitación del dataset, no del pipeline) y `sintetico` (formas
geométricas, con `num_occluded` disponible). Métrica principal: sMAPE.

### 4.2 TallyQA — conteo por VQA

**Fuente:** Acharya, Kafle y Kanan, AAAI 2019. Preguntas tipo "How many X are there?" sobre
fotos reales (COCO/Visual Genome), clasificadas por el propio dataset en `simple` (conteo
directo) y `compleja` (requiere filtro adicional). Métricas: accuracy exacta, MAE, RMSE
(igual que el paper original).

### 4.3 OmniSpatial — razonamiento espacial

**Fuente:** Jiang et al., 2025 · HF Hub `qizekun/OmniSpatial`. Opción múltiple (A–D). Benchmark
completo: 50 subtipos / ~1.533 preguntas. **Este proyecto evalúa solo 4 subtipos**
(`Geometric_Reasoning`, `Motion_Analysis`, `Egocentric`, `Allocentric`), no el benchmark
completo — dejar esto explícito en cualquier texto que describa resultados.

### 4.4 Benchmark sintético 2D (generador propio)

Generador propio (PIL + NumPy, interfaz Gradio) que crea imágenes con figuras geométricas
donde la **cantidad de figuras es una variable controlada**, con 4 tipos de pregunta
(`conteo_general`, `conteo_forma`, `conteo_color`, `conteo_combinado`). Permite aislar el
efecto de la densidad de objetos de una forma que los benchmarks reales no permiten (sus
distribuciones de conteo son heterogéneas). Métrica: sMAPE (igual razón que CAPTURe).
Semilla fija por imagen (reproducible). Es la contribución metodológica propia central del
trabajo — ver `benchmark_sintetico/2D.py`.

---

## 5. Metodología del pipeline común

Los 4 benchmarks comparten la misma estructura de notebook (`piloto_<benchmark>_<modelo>.ipynb`):

```
Config (modelo, muestra, seed)
  → reset_peak_memory_stats() antes de cargar el modelo
  → carga del dataset (HF / zip propio / HTTP por pregunta en TallyQA)
  → muestreo (semilla fija)
  → por cada pregunta: construir prompt → predecir() en ThreadPoolExecutor con timeout
      → parsear respuesta → calcular métricas
  → guardar detalle_*.csv (una fila por pregunta) + resultados_*.txt (resumen agregado)
```

**Único punto de variación entre modelos:** la función `predecir(imagen, pregunta) -> str`.
El resto del pipeline (muestreo, timeout, parseo, guardado) es idéntico.

**Parseo:** `extraer_entero()` (regex de dígito → diccionario de números en palabras → `None`)
para los 3 benchmarks de conteo; `parsear_respuesta()` (extrae letra A–D) para OmniSpatial,
con su propio `construir_prompt()` de opción múltiple. Ver diagramas de flujo/secuencia
generados en sesiones anteriores para el detalle visual de estas diferencias.

**Timeout:** 30s por pregunta vía `ThreadPoolExecutor`. Tasa de timeout observada: **0% en
todas las corridas** — toda respuesta inválida es `parse_fail`, nunca timeout.

**Bucketización para análisis:** `Rango_Objetos` (CAPTURe, cuartiles) y `Rango_GT` (TallyQA)
son adaptaciones propias por cuartiles/grupos manuales — **no son técnicas de los papers
originales**, necesarias porque las distribuciones reales de conteo son muy heterogéneas.

---

## 6. Infraestructura: Google Colab + T4

Todo el código de inferencia corre en **Google Colab con GPU T4 gratuita**, nunca localmente
(no hay GPU disponible en el entorno de desarrollo). Walter sube/ejecuta los notebooks en
Colab y trae de vuelta los `.csv`/`.txt` de resultados.

| Limitación | Impacto |
|---|---|
| 15 GB VRAM | Los 4 modelos caben (2.4–6.2 GB en pico cada uno) |
| Sin persistencia de sesión | Usar `files.download()` o montar Drive al final de cada notebook |
| Una GPU por sesión | Cada modelo corre en sesión Colab independiente (versiones de `transformers` incompatibles entre sí) |

---

## 7. Estructura del repositorio — actual

Árbol real tras la limpieza de octubre de 2026 (rutas relativas a la raíz del proyecto):

```
tt/
├── README.md                                    ← este archivo (única fuente de verdad)
├── PROPUESTAS_Y_EXTRAS.md                       ← [ELIMINAR, fusionado aquí]
├── CLAUDE.md                                    ← [ELIMINAR, fusionado aquí]
│
├── benchmark_sintetico/
│   ├── 2D.py                                    ← generador del benchmark sintético
│   ├── 3D.py                                    ← exploración no usada en el alcance final
│   ├── pipeline.py
│   ├── benchmark_2d_sintetico_lotes_2400_v2.zip ← dataset regenerado (2.400 preguntas) — AÚN SIN EVALUAR
│   ├── benchmark_2d_sintetico_lotes_400_v1.zip  ← dataset viejo (400 preguntas) — ya evaluado, resultados abajo
│   ├── benchmark_2d_sintetico/                  ← [REVISAR] carpeta descomprimida del v1, redundante con el zip de al lado
│   └── pruebas/{InternVL2_1B,moondream2,paligemma2_3b,qwen2_vl_2b}/
│       ├── detalle_2Dsintetico_<modelo>.csv
│       ├── piloto_2Dsintetico_<modelo>.ipynb
│       └── resultados_2Dsintetico_<modelo>.txt
│
├── dataset/                                     ← imágenes reales (NO debe ir al repo git, ver nota)
│   ├── capture_real/ · capture_synth/ · omnispatial_dataset/ · tallyqa_imgs/
│   └── capture.ipynb · omnispatial.ipynb · tallyqa.py   ← scripts de descarga/preparación
│
├── pruebas/
│   ├── Conteo/{InternVL2_1B,moondream2,paligemma2_3b,qwen2_vl_2b,yolo_baseline}/
│   │   └── piloto_*.ipynb, detalle_{CAPTURe,TallyQA}_*.csv, resultados_*.txt
│   │   ├── graficos_capture/   (4 PNG)
│   │   └── graficos_tallyqa/   (5 PNG)
│   ├── razonamiento espacial/{InternVL2_1B,moondream2,paligemma2,qwen2vl}/
│   │   └── piloto_omnispatial_*.ipynb, detalle_OmniSpatial_*.csv, resultados_*.txt
│   │   └── graficos_omnispatial/   (4 PNG)
│   └── explicabilidad/                          ← VACÍA — ver sección 8, ahí va a vivir el experimento ya hecho
│
├── Claude outputs/                               ← [REVISAR, ver pendientes] mezcla de cosas vigentes y obsoletas:
│   ├── graficos_capture.py / graficos_omnispatial.py / graficos_sintetico.py / graficos_tallyqa.py  ← VIGENTES, los que realmente se usan
│   ├── metodologia_y_resultados.md              ← [ELIMINAR] copia local vieja; la versión real vive en el proyecto de Claude
│   ├── detalle_CAPTURe_InternVL2-1B.xlsx        ← [¿PARA QUÉ ES?] sin identificar aún
│   ├── capture_fix.ipynb                        ← [¿PARA QUÉ ES?] sin identificar aún
│   └── capture_fix_real_moondream2.ipynb        ← [¿PARA QUÉ ES?] sin identificar aún
│
├── pruebas.zip                                   ← [¿PARA QUÉ ES?] posible respaldo viejo de pruebas/, sin confirmar
│
└── memoria, pressentaciones de avance, bibliografia y otros/
    ├── memoria y propuesta/       (borrador_memoria_ICI.pdf + .docx, propuesta USM, propuesta_memoria.odt)
    ├── presentaciones de avances/ (pptx de avance)
    ├── bibliografia/              (PDFs de los papers citados)
    └── exploracion benchmarks notebooks/  (CV_bench, blink, capture, omnispatial_test, tallyQA — exploración temprana, fuera del alcance final)
```

**Fuera del árbol principal, en otra carpeta conectada (`Desktop\tt`), pendiente de mover:**
```
Claude outputs/
├── piloto_attention_moondream2_v2.ipynb
└── piloto_attention_moondream2_v3.ipynb   ← la versión que SÍ corrió bien (12/12 imágenes)
```

**Convención de nombres de resultados:** `resultados_{benchmark}_{modelo}.txt` (resumen) y
`detalle_{benchmark}_{modelo}.csv` (una fila por pregunta).

---

## 8. Estructura del repositorio — objetivo (incluye explicabilidad)

Meta a converger antes de subir el repo, incorporando la carpeta de explicabilidad como
ciudadana de primera clase (mismo patrón que `Conteo/` y `razonamiento espacial/`):

```
tt/
├── README.md
│
├── benchmark_sintetico/
│   ├── 2D.py
│   ├── datasets/
│   │   ├── benchmark_2d_sintetico_lotes_v1_400q.zip   ← renombrado, ya evaluado
│   │   └── benchmark_2d_sintetico_lotes_v2_2400q.zip  ← el vigente, por evaluar
│   └── pruebas/{modelo}/   (igual que hoy)
│
├── dataset/            ← excluido de git (.gitignore), script de descarga documentado en vez de binarios
│
├── pruebas/
│   ├── Conteo/{modelo,...}/
│   ├── razonamiento_espacial/{modelo,...}/        ← renombrado sin espacio, por consistencia
│   └── explicabilidad/
│       └── moondream2/
│           ├── piloto_attention_moondream2_v3.ipynb   ← movido desde Desktop\tt
│           ├── rollout_resumen.csv
│           └── heatmaps/   (las 12 imágenes PNG resultado)
│
├── graficos/            ← los 4 scripts vigentes, consolidados en un solo lugar (no repartidos en 2 carpetas)
│
├── memoria/
│   ├── borrador_memoria_ICI.docx (+ el .pdf renderizado)
│   └── propuesta/  (los documentos de la propuesta original, histórico)
│
├── bibliografia/        ← PDFs de papers citados (o excluido de git si pesa mucho, con lista de referencias en su lugar)
│
└── anexos/
    └── exploracion_benchmarks_descartados/   ← lo que hoy es "exploracion benchmarks notebooks", claramente marcado como fuera de alcance
```

Diferencias clave respecto al árbol actual:
- `explicabilidad/` deja de estar vacía — el experimento ya ejecutado (notebook v3 + sus
  resultados) se mueve ahí desde la carpeta separada `Desktop\tt`.
- Los dos zip del sintético quedan con nombres que dicen explícitamente cuál es cuál (evita
  la colisión de nombre que ya se corrigió una vez).
- Un solo lugar para los scripts de gráficos (hoy están bien, pero formalizar que `graficos/`
  es ESTE y no el viejo que ya se borró).
- `dataset/` fuera de git por tamaño (~6.3 GB) — reemplazado por un script o instrucciones de
  descarga.
- Carpetas con espacios en el nombre (`razonamiento espacial`, `pruebas.zip` suelto) se
  limpian para que el repo sea más portable entre sistemas operativos.

---

## 9. Estado actual del proyecto

> Resumen cualitativo. Para cifras exactas (accuracy, MAE, sMAPE, RMSE por modelo y
> benchmark), ver la memoria o el documento de metodología y resultados — no se repiten
> aquí para no desincronizar este README cada vez que se re-evalúa algo (como pasó con los
> tres documentos que este README reemplaza).

| Benchmark | Estado | Hallazgo principal (1 línea) |
|---|---|---|
| CAPTURe | ✅ evaluado, 4 modelos | PaliGemma2-3B rechaza responder >50% de las veces en vez de contar mal |
| TallyQA | ✅ evaluado, 4 modelos a n=300 | Un solo outlier explica un RMSE anómalo en preguntas complejas (no es un patrón real) |
| OmniSpatial | ✅ evaluado, 4 subtipos de 50 | Geometric_Reasoning ≈ nivel de azar en todos los modelos; Egocentric es donde sí hay señal real |
| Sintético 2D (v1, n=400) | ✅ evaluado | PaliGemma2-3B se "ancla" al techo de conteo (predice 100 sin que sea la respuesta correcta) |
| Sintético 2D (v2, n=2.400) | ⏳ **pendiente de evaluar** — prioridad #1 | — |
| Explicabilidad (attention rollout, moondream2) | ✅ ejecutado y con hallazgo | Ver sección 10 |
| YOLO-World (baseline sin VLM) | ⚠️ datos existen, sin confirmar si se ejecutó | Ver sección 11 |

---

## 10. Explicabilidad

**Técnica:** attention rollout (Abnar & Zuidema, 2020) sobre el encoder visual de moondream2,
aplicado a una muestra de 12 imágenes (3 por cada uno de los 4 tipos de pregunta del
benchmark sintético).

**Problema técnico resuelto:** los forward hooks no podían funcionar con esta arquitectura —
la atención real se calcula con `F.scaled_dot_product_attention` (kernel fusionado) dentro
de una función de Python suelta, no de un `nn.Module`, así que un hook nunca se dispara ni
expone los pesos aunque lo hiciera. Solución: monkey-patch de la función `attn()` de
`vision.py` (reimplementación manual con softmax explícito). Ver
`pruebas/explicabilidad/moondream2/piloto_attention_moondream2_v3.ipynb` para la versión que
corrió con éxito (12/12 imágenes).

**Hallazgo:** la atención no se concentra en las figuras contadas. Aparece un patrón de 2–3
puntos calientes en posiciones casi idénticas en las 12 imágenes, sin importar el contenido
ni el tipo de pregunta — consistente con el fenómeno de *attention sinks* documentado en
Darcet et al. (2023), *"Vision Transformers Need Registers"*. Es un hallazgo de explicabilidad
real (el modelo no "mira" lo que cuenta), no un error del experimento.

**Técnicas investigadas y descartadas** (documentadas en la última celda del notebook, con
su razón): Attention Flow, Integrated Gradients, atención cruzada texto-imagen.

---

## 11. Pendientes priorizados

1. **Evaluar el dataset sintético regenerado** (`benchmark_2d_sintetico_lotes_2400_v2.zip`,
   2.400 preguntas, rango real de `num_shapes` 5–195) en los 4 modelos — máximo impacto,
   reemplaza resultados con ruido conocido (dataset v1 tenía solo 5 imágenes/nivel).
2. **Mover los notebooks de explicabilidad** a `pruebas/explicabilidad/moondream2/` dentro
   del árbol principal (hoy viven en una carpeta separada, `Desktop\tt`).
3. **Confirmar o descartar el baseline YOLO-World**: existe un CSV/resumen de una corrida,
   pero el notebook no tiene metadata de ejecución guardada — no se puede confirmar que se
   corrió tal cual está. Decidir si re-correr o excluir de la memoria.
4. **Cerrar la memoria formal**: incorporar los resultados del punto 1 y el hallazgo de
   explicabilidad (ya ejecutado) a los capítulos 4/5; completar placeholders de portada
   (profesor guía ya está confirmado: Rodrigo Verschae), dedicatoria, y agregar el link del
   repositorio al Anexo C una vez publicado.
5. Revalidar `baseline_azar`/`baseline_mayoria` de OmniSpatial contra el código real de la
   celda de métricas (el texto de la memoria y el código no coinciden en la fórmula).
6. Investigar la discrepancia de versión de `transformers` entre notebooks de distintos
   benchmarks (podría ser deriva de versión en el tiempo, sin confirmar).
7. **Limpieza de directorio restante** (ver sección 7): identificar qué son
   `capture_fix.ipynb`, `capture_fix_real_moondream2.ipynb` y
   `detalle_CAPTURe_InternVL2-1B.xlsx` en `Claude outputs/`; confirmar o eliminar
   `pruebas.zip` y la carpeta descomprimida vieja del sintético.

---

## 12. Posibles extensiones futuras

No priorizadas para esta entrega, pero valiosas si queda tiempo/cómputo después de cerrar
los pendientes de la sección 11:

- **Baseline YOLO-World de detección clásica** (sin VLM): permitiría separar si el error de
  los VLMs viene de no "ver" los objetos o de no saber contarlos aunque los vea. Requiere
  decidir primero el punto 3 de la sección 11.
- **Comparación con modelos de mayor escala** (p. ej. Qwen2-VL-7B, InternVL2-8B): si la
  brecha se cierra con más parámetros, sugiere que el sesgo es de entrenamiento más que
  arquitectónico. Requiere Colab Pro+ (A100) o cuantización int4 — no cabe en la T4 gratuita
  sin pérdida de calidad.
- **Benchmarks adicionales de proximidad** (near/far, left/right): OmniSpatial los descarta
  por saturación en modelos grandes, pero esa saturación no aplicaría a modelos 1–3B.
  Candidatos: EmbSpatial-Bench, SpatialBot-Bench.
- **Extender la explicabilidad a razonamiento espacial** (OmniSpatial Geometric_Reasoning,
  el track que da resultados a nivel de azar): ver si el modelo "mira" alguna parte de la
  imagen o si la atención es uniforme — complementaría el hallazgo ya obtenido en conteo.

---

## 13. Notas técnicas críticas

- **`predecir(imagen_pil, prompt_texto) -> str`** es el único punto que cambia entre modelos
  en todo el pipeline. El resto (muestreo, timeout, parseo, guardado) es idéntico.
- **`baseline_azar` vs. `baseline_mayoria`:** los archivos de resultados usan el nombre
  `baseline_azar`, pero el código real calcula la frecuencia de la clase mayoritaria de
  `ground_truth` por track (`value_counts(normalize=True).max()`), no 1/n_opciones uniforme.
  Son conceptos distintos — ver pendiente #5.
- **El campo `id` de OmniSpatial no es único globalmente** (se repite una vez por
  `task_type`) — usar siempre `task_type` + índice de fila, nunca el campo `id` solo, para
  evitar emparejar imagen/pregunta incorrectas (error ya detectado y corregido una vez).
- **Medición de VRAM:** siempre `torch.cuda.max_memory_allocated()` con
  `reset_peak_memory_stats()` llamado *antes* de cargar el modelo. No usar `nvidia-smi` —
  puede incluir residuos de sesiones anteriores si la sesión de Colab no está limpia.
- **`parse_fail` ≠ `timeout`:** ambos se excluyen de las métricas de error, pero significan
  cosas distintas (el modelo respondió algo no parseable vs. no respondió a tiempo). La tasa
  de timeout fue 0% en todas las corridas de este proyecto — toda inválida es `parse_fail`.
- **Entorno de ejecución:** todo el código de inferencia corre en Colab, nunca localmente.
  Un agente de IA sin GPU puede diseñar/editar notebooks y leer `.ipynb` ya ejecutados (con
  outputs) que el usuario traiga de vuelta, pero nunca debe asumir que puede re-ejecutarlos.

---

## 14. Reproducibilidad

Todas las corridas usan `RANDOM_SEED = 42`. Dependencias por modelo (incompatibles entre sí,
cada una en sesión de Colab independiente):

| Modelo | `transformers` | Nota |
|---|---|---|
| Moondream2 | `==4.46.3`* | API propia `.query()`, `trust_remote_code=True` |
| InternVL2-1B | `==4.37.2` | `trust_remote_code=True`, `model.chat()` |
| Qwen2-VL-2B | `>=4.46.2` | requiere `qwen_vl_utils` adicional |
| PaliGemma2-3B | `>=4.46.2` | modelo gated, requiere `HF_TOKEN` en Secretos de Colab |

*Hay una discrepancia sin resolver entre notebooks que pinan `4.57.6` vs. `4.46.3` para
moondream2 — ver pendiente #6.
