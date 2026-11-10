# Evaluación de VLMs de Escala Pequeña en Conteo Visual y Razonamiento Espacial

**Memoria de Título — Ingeniería Civil Informática, Universidad Técnica Federico Santa María**  
**Autor:** Walter Sanhueza · **Profesor guía:** Rodrigo Verschae · **Plazo:** 5 meses

---

## Índice

1. [Descripción del proyecto](#1-descripción-del-proyecto)
2. [Pregunta de investigación](#2-pregunta-de-investigación)
3. [Modelos evaluados](#3-modelos-evaluados)
4. [Benchmarks](#4-benchmarks)
5. [Metodología de evaluación](#5-metodología-de-evaluación)
6. [Infraestructura: Google Colab + T4](#6-infraestructura-google-colab--t4)
7. [Estructura del repositorio](#7-estructura-del-repositorio)
8. [Resultados actuales](#8-resultados-actuales)
9. [Tamaños de muestra y confiabilidad](#9-tamaños-de-muestra-y-confiabilidad)
10. [Estado del proyecto](#10-estado-del-proyecto)

---

## 1. Descripción del proyecto

Este proyecto evalúa un conjunto de modelos de Visión y Lenguaje (*Vision-Language Models*, VLMs) de **escala pequeña** (1–3B parámetros) en dos capacidades cognitivas de alto nivel: **conteo visual** y **razonamiento espacial**. La evaluación se realiza sobre benchmarks estándar públicos, sin fine-tuning adicional, para medir el desempeño de modelos que pueden ejecutarse en hardware de consumo o en la capa gratuita de servicios de cómputo en la nube.

El trabajo se inscribe en un contexto donde los modelos grandes de frontera (GPT-4o, Gemini 2.5 Pro, Claude 3.7 Sonnet) alcanzan resultados cercanos a la saturación en varios benchmarks de razonamiento visual. La pregunta que motiva este estudio es si esa capacidad es escalable hacia abajo, o si los modelos pequeños —con órdenes de magnitud menos parámetros— fallan de manera sistemática y predecible que revela sus limitaciones arquitectónicas o de entrenamiento.

Se incluye además una fase de **explicabilidad visual** (*grounding*) que busca verificar si los modelos realmente "miran" las regiones relevantes al generar sus respuestas, o si aciertan por inercia estadística.

---

## 2. Pregunta de investigación

> **¿Los VLMs de escala pequeña construyen una representación espacial 3D coherente del mundo, o responden por sesgos estadísticos bidimensionales aprendidos durante el entrenamiento?**

La pregunta se operacionaliza en dos ejes medibles:

**Eje 1 — Conteo visual:** ¿puede el modelo contar objetos en una imagen cuando hay oclusión, densidad alta, o cuando los objetos no son fácilmente distinguibles? Se evalúa si existe un "techo de respuesta" (el modelo nunca predice más de N objetos, independiente de la cantidad real), lo que sería evidencia de memorización estadística antes que de percepción genuina.

**Eje 2 — Razonamiento espacial:** ¿puede el modelo responder correctamente preguntas que requieren inferencia sobre posición relativa, perspectiva egocéntrica vs. alocéntrica, y transformaciones geométricas? La distinción entre perspectiva propia (egocéntrica) y de terceros (alocéntrica) es un discriminador directo de representación 3D: un modelo que solo aprende asociaciones 2D debería fallar en la condición alocéntrica.

**Fase de explicabilidad:** complementa los dos ejes anteriores verificando, mediante técnicas de atribución visual, si los patrones de atención del modelo coinciden con las regiones que un humano señalaría como relevantes para la respuesta.

---

## 3. Modelos evaluados

Se seleccionaron cuatro modelos open-weight con entre 1B y 3B parámetros, priorizando diversidad arquitectónica y de estrategia de entrenamiento:

| Modelo | Parámetros | Arquitectura base | Entrenamiento visual | HF Hub |
|---|---|---|---|---|
| **Moondream2** | 1.8B | SigLIP + Phi-1.5 | Propio (datos curados) | `vikhyatk/moondream2` |
| **Qwen2-VL-2B-Instruct** | 2B | Qwen2 + Vision Transformer dinámico | Instrucciones multimodales | `Qwen/Qwen2-VL-2B-Instruct` |
| **InternVL2-1B** | 1B | InternViT + InternLM | Contrastivo + instrucciones | `OpenGVLab/InternVL2-1B` |
| **PaliGemma2-3B-mix-448** | 3B | SigLIP + Gemma2 | Mezcla de tareas (mix) | `google/paligemma2-3b-mix-448` |

> **Nota sobre InternVL2-2B:** existe una versión de 2B de la misma arquitectura InternVL2. Se corrió en OmniSpatial (resultados disponibles) pero se descartó del eje de conteo por redundancia con el InternVL2-1B. Sus resultados espaciales se incluyen en tablas comparativas para completitud.

### Caracterización por uso de VRAM

| Modelo | VRAM al cargar | VRAM pico (inferencia) | Versión transformers |
|---|---|---|---|
| InternVL2-1B | ~2.0 GB | ~2.4 GB | 4.37.2 |
| Qwen2-VL-2B | ~4.2 GB | ~4.9 GB | ≥4.46.2 (5.13.1) |
| Moondream2 | ~3.7 GB | ~5.3 GB | 4.57.6 (fork propio) |
| InternVL2-2B | ~4.6 GB | ~5.0 GB | 4.37.2 |
| PaliGemma2-3B | ~5.8 GB | ~6.1 GB | ≥4.46.2 (5.13.1) |

Los tres últimos modelos operan con margen ajustado en una T4 (15 GB). Moondream2 requiere una versión de `transformers` que es un fork propio y no es compatible con los otros modelos; cada modelo se ejecuta en una sesión de Colab independiente.

---

## 4. Benchmarks

### 4.1 TallyQA — Conteo simple y complejo

**Fuente:** COCO + Visual Genome · **Referencia:** Acharya et al., 2019  
**HF / descarga:** archivo `test.json` (38,589 preguntas, ~300 MB)

TallyQA contiene preguntas de conteo sobre imágenes naturales divididas en dos tipos:
- **Simple:** el objeto a contar es visualmente prominente ("How many dogs are there?")
- **Compleja:** requiere comprensión de contexto o relaciones ("How many people are wearing hats?")

Cada pregunta tiene un ground truth entero. El rango real de conteos en el split de test va de 0 a 15 (propiedad del dataset, no del pipeline). La métrica principal es *exact match accuracy* y el error absoluto medio (MAE).

**Por qué es relevante:** permite medir si el modelo colapsa en magnitudes altas (GT > 5) o si mantiene precisión a lo largo del rango, lo que discrimina entre memorización estadística (sesgo hacia valores bajos frecuentes en entrenamiento) y conteo genuino.

### 4.2 CAPTURe — Conteo con oclusión

**Fuente:** Paiss et al., 2023 · **HF Hub:** `atinp/CAPTURe`

CAPTURe está diseñado específicamente para medir conteo bajo oclusión y densidad alta. Tiene dos subsets:

**Real (`real/`):** 824 imágenes fotográficas de objetos cotidianos (ropa, alimentos, objetos de tienda, etc.) con conteos que van de 8 a 907 objetos (media ~60). Las oclusiones son naturales (objetos parcialmente tapados por otros, perspectiva, iluminación).

**Sintético (`synthetic/`):** 1,150 imágenes generadas con formas geométricas de colores (círculos, cuadrados) sobre fondo blanco, con conteos entre 5 y 15 objetos. Incluye el campo `num_occluded`, que indica cuántos objetos están parcialmente tapados por otros, lo que permite analizar el efecto de la oclusión de forma controlada.

El subset `real/` incluye coordenadas de bounding box para cada objeto, lo que habilita la fase de explicabilidad (se puede verificar si el modelo atiende las regiones donde están los objetos).

**Por qué es relevante:** los modelos grandes (GPT-4V, Gemini) fallan en CAPTURe real de manera similar a los modelos pequeños, con un colapso claro en densidades altas. En modelos pequeños se espera que el techo de respuesta sea aún más bajo y ocurra antes.

### 4.3 OmniSpatial — Razonamiento espacial y perspectiva

**Fuente:** Ye et al., 2025 · **HF Hub:** `qizekun/OmniSpatial`  
**Tamaño del repositorio completo:** ~16.5 GB (solo se descarga `OmniSpatial-test.zip`)

OmniSpatial es un benchmark de opción múltiple (4 opciones: A/B/C/D) para razonamiento espacial. El split de test público contiene **1,533 preguntas** distribuidas en **10 sub_task_types** agrupados en 4 categorías (`task_type`). El dataset cubre desde razonamiento geométrico abstracto hasta perspectiva egocéntrica y alocéntrica.

**Tracks seleccionados para evaluación (4 de 10):**

| Track (`sub_task_type` en JSON) | Descripción | n preguntas (total) |
|---|---|---|
| `Geometric_Reasoning` | Rotación mental, proyecciones, unfolding de poliedros | 155 |
| `Motion_Analysis` | Trayectorias, predicción de movimiento, dinámica temporal | 200 |
| `Egocentric` | Relaciones espaciales desde el punto de vista del observador | 453 |
| `Allocentric` | Relaciones espaciales desde el punto de vista de un tercero | 362 |

La justificación de esta selección está alineada con la pregunta central: `Geometric_Reasoning` prueba representación 3D abstracta pura; `Egocentric` y `Allocentric` contrastan la misma escena desde perspectivas distintas, siendo el paso de egocéntrica a alocéntrica el test más directo de si el modelo puede adoptar un punto de vista diferente al del observador visual.

**Nota sobre `Geometric_Reasoning`:** 133 de 155 preguntas tienen `options = []` (lista vacía). Las opciones son figuras geométricas embebidas en la imagen que deben responderse visualmente (A/B/C/D). El harness usa un prompt distinto para estos casos: en lugar de listar opciones de texto, pide directamente la letra correspondiente a la figura.

**Nota sobre nombres en el JSON:** los nombres exactos de los tracks difieren del paper original. Siempre se usa el nombre del JSON para filtrar:

| Nombre en el paper | Nombre real en `data.json` |
|---|---|
| "Ego-Centric" | `Egocentric` |
| "Allo-Centric" | `Allocentric` |
| "Manipulate" | `Manipulation` |

---

## 5. Metodología de evaluación

### 5.1 Protocolo general

Cada modelo se evalúa en cada benchmark mediante un notebook de Jupyter independiente que sigue el siguiente flujo fijo:

```
Configuración (MODEL_ID, SAMPLE_SIZE, RANDOM_SEED)
    ↓
Instalación de dependencias (versión de transformers específica por modelo)
    ↓
Carga del modelo con torch.cuda.reset_peak_memory_stats() previo
    ↓
Descarga del benchmark
    ↓
Muestreo estratificado (preserva distribución de categorías o magnitudes)
    ↓
Loop de inferencia con timeout por pregunta
    ↓
Parseo de respuesta → entero (conteo) o letra A/B/C/D (espacial)
    ↓
Cálculo de métricas + desglose por subgrupo
    ↓
Guardado de resultados en .txt (resumen) y .csv (detalle por pregunta)
```

### 5.2 Abstracción del modelo — función `predecir()`

El único componente que cambia entre modelos es la función `predecir(imagen_pil, prompt_texto) -> str`. El resto del harness (muestreo, timeout, parseo, métricas, guardado) es idéntico. Esto garantiza que las diferencias en resultados son atribuibles al modelo y no al pipeline.

Cada modelo requiere una implementación distinta:
- **Moondream2:** usa `model.query(image, question)` (API propia, no disponible en otros modelos)
- **Qwen2-VL:** requiere `process_vision_info()` del paquete `qwen_vl_utils` + `apply_chat_template()` + `model.generate()`; el parámetro `max_pixels=401408` en el dict de imagen es crítico para evitar OOM en imágenes de alta resolución
- **InternVL2:** requiere preprocesamiento manual de imagen (`_dynamic_preprocess()` para conteo, single-tile 448×448 para razonamiento espacial donde el contexto global prima sobre el detalle)
- **PaliGemma2:** el procesador requiere que el prompt incluya el token `<image>` explícitamente; la respuesta puede incluir texto libre antes del número, por lo que el parser aplica regex antes del fallback

### 5.3 Manejo de timeouts

Cada llamada a `predecir()` se ejecuta en un `ThreadPoolExecutor` con un timeout configurable (default: 60 segundos para conteo, 60 segundos para espacial). Si el modelo no responde en ese tiempo, la pregunta se registra como timeout y se excluye de las métricas de accuracy y MAE. La tasa de timeout se reporta explícitamente.

En la práctica, todos los modelos evaluados han tenido **0% de timeouts** en todas las corridas.

### 5.4 Parseo de respuestas

#### Conteo (TallyQA, CAPTURe)

El parser aplica tres estrategias en orden:

1. **Dígito directo:** regex `\b(\d+)\b` extrae el primer número entero de la respuesta
2. **Número en palabras:** diccionario `{"one": 1, "two": 2, ..., "fifteen": 15}` aplicado sobre la respuesta en minúsculas
3. **Parse fail:** si ninguna estrategia extrae un número, la pregunta se registra como `parse_fail=True` y se excluye de accuracy y MAE (pero se contabiliza en la tasa de fallo)

Los parse fails observados no son errores de parseo sino **negativas del modelo**: PaliGemma2 ocasionalmente responde *"Sorry, as a base VLM I am not trained to answer this question"* para preguntas de conteo (6% en TallyQA, pilot n=50).

#### Razonamiento espacial (OmniSpatial)

El parser busca la primera letra válida (A, B, C o D) en la respuesta, ignorando mayúsculas/minúsculas. Si la respuesta contiene justificación textual, se extrae solo la letra. Todos los modelos evaluados tuvieron **0% de parse fails** en OmniSpatial.

### 5.5 Muestreo estratificado

**TallyQA:** el muestreo preserva la proporción de preguntas simples vs. complejas del dataset completo (~60% simple, ~40% compleja). El dataset completo de test tiene 38,589 preguntas; se muestrea con `random.seed(42)`.

**CAPTURe:** se muestrea independientemente del subset `real` y `synthetic`, preservando la distribución de magnitudes (buckets: 8-15, 16-28, 29-67, 68-907 para `real`; distribución uniforme por GT para `synthetic`).

**OmniSpatial:** 100 preguntas por track (400 total por modelo), muestreadas con semilla fija. Para `Geometric_Reasoning`, el muestreo preserva la proporción de preguntas con opciones de texto vs. opciones visuales (22% / 78%).

### 5.6 Métricas reportadas

#### Conteo

| Métrica | Descripción |
|---|---|
| `ACCURACY_EXACTA` | Proporción de predicciones iguales al ground truth (exact match) |
| `MAE` | Error absoluto medio: $\frac{1}{N}\sum|pred_i - gt_i|$ |
| `VARIANZA_ERROR` | Varianza del error absoluto |
| `PARSE_FAIL_RATE` | Proporción de preguntas sin respuesta parseable |
| `TIMEOUT_RATE` | Proporción de preguntas que excedieron el límite de tiempo |
| Desglose por rango GT | Accuracy y MAE separados por rango de conteo (0-2, 3-5, 6-15) |
| Desglose por tipo | Simple vs. compleja (TallyQA) |
| Desglose por `num_occluded` | Accuracy y MAE por nivel de oclusión (CAPTURe sintético) |

#### Razonamiento espacial

| Métrica | Descripción |
|---|---|
| `ACCURACY_GLOBAL` | Exact match sobre todas las preguntas |
| Accuracy por track | Desglose por `Geometric_Reasoning`, `Motion_Analysis`, `Egocentric`, `Allocentric` |
| `baseline_mayoria` | Frecuencia de la clase más común por track (referencia de azar sesgado) |
| Detalle `Geometric_Reasoning` | Separado entre preguntas con y sin opciones de texto |

> **Nota terminológica:** los archivos de resultados generados previamente llaman `baseline_azar` a esta métrica. En rigor es la frecuencia de la clase mayoritaria, no el azar uniforme (25%). Las tablas en este README usan la denominación correcta.

### 5.7 Medición de VRAM

```python
# Antes de cargar el modelo:
torch.cuda.reset_peak_memory_stats()

# Cargar modelo...

# Después de completar la inferencia:
vram_pico_mb = torch.cuda.max_memory_allocated() / 1024**2
```

`reset_peak_memory_stats()` resetea el contador de máximo histórico, garantizando que `max_memory_allocated()` solo cuenta lo que usó esta sesión desde ese punto. La cifra incluye el peso del modelo + activaciones durante la inferencia. **Importante:** si la sesión de Colab tenía memoria residual de una corrida anterior (ej. por un crash), `nvidia-smi` mostrará un valor mayor que `torch.cuda.max_memory_allocated()` — en ese caso la métrica de PyTorch es la correcta, pero la sesión no estaba limpia. Siempre usar sesión de Colab nueva para comparaciones válidas de VRAM entre modelos.

---

## 6. Infraestructura: Google Colab + T4

### Por qué Colab y no local

Todo el código de inferencia (carga de modelos, forward pass, benchmarks) corre en **Google Colab con GPU Tesla T4 gratuita**. Esto es una decisión deliberada de diseño del proyecto:

- Los modelos evaluados (1–3B parámetros) requieren entre 2.4 GB y 6.2 GB de VRAM en pico, todos dentro de los 15 GB de la T4
- El hardware local disponible (Dell Inspiron 5510 sin GPU discreta; torre con RX 6700 XT bajo Windows) no tiene soporte práctico para inferencia de VLMs: la RX 6700 XT requiere ROCm en Linux para ML, no disponible en Windows
- Colab permite reproducibilidad: cualquier evaluador puede correr los notebooks con las mismas condiciones de hardware

### Limitaciones de la T4 gratuita

| Limitación | Impacto en el proyecto |
|---|---|
| 15 GB de VRAM | PaliGemma2 (6.1 GB) deja ~9 GB de margen; todos los modelos caben |
| Sesiones de ~12 horas | Las corridas actuales (n=50–400 preguntas) terminan en 5–30 minutos; no es un cuello de botella |
| Sin persistencia de sesión | Los archivos generados en `/content/` se pierden al cerrar. **Solución:** usar `files.download()` al final de cada notebook, o montar Google Drive con `drive.mount('/content/drive')` |
| Una GPU por sesión | No hay paralelismo entre modelos; cada modelo se corre en sesión independiente |

### Flujo de trabajo con Colab

```
Editar notebook localmente (carpeta sincronizada con Drive o subida manual)
    ↓
Abrir notebook en Colab → Runtime → Change runtime type → T4 GPU
    ↓
Ejecutar todas las celdas (Run All)
    ↓
Los archivos .txt y .csv de resultados se descargan automáticamente
vía files.download() al final del notebook
    ↓
Mover archivos descargados a la carpeta correspondiente en este repositorio
```

Si la carpeta del proyecto está sincronizada con Google Drive, se puede montar Drive al inicio del notebook para leer/escribir directamente sin paso manual de subida/descarga:

```python
from google.colab import drive
drive.mount('/content/drive')
# Luego apuntar OUTPUT_PATH a la carpeta de Drive correspondiente
```

---

## 7. Estructura del repositorio

```
tt/
├── README.md                          ← Este archivo
├── CLAUDE.md                          ← Notas de contexto del proyecto (no editar sin avisar)
├── PROPUESTA SJ Walter_Sanhueza.pdf   ← Registro formal USM
├── propuesta_memoria.docx             ← Memoria en desarrollo
│
├── benchmarks/                        ← EDA de datasets
│   ├── eda_tallyqa.ipynb
│   ├── eda_capture.ipynb
│   └── eda_omnispatial.ipynb
│
├── pruebas/
│   ├── Conteo/                        ← Evaluación TallyQA + CAPTURe
│   │   ├── moondream2/
│   │   │   ├── piloto_tallyqa_moondream2.ipynb
│   │   │   ├── piloto_capture_moondream2 (2).ipynb
│   │   │   ├── resultados_TallyQA_moondream2.txt
│   │   │   ├── resultados_CAPTURe_moondream2.txt
│   │   │   ├── detalle_TallyQA_moondream2.csv
│   │   │   ├── detalle_CAPTURe_moondream2.csv
│   │   │   └── versiones_completas/   ← CAPTURe sobre dataset completo
│   │   ├── qwen2_vl_2b/
│   │   ├── InternVL2_1B/
│   │   ├── InternVL2_2B/              ← Solo estructura; inferencia no completada
│   │   └── paligemma2_3b/
│   │
│   ├── razonamiento espacial/         ← Evaluación OmniSpatial
│   │   ├── moondream2/
│   │   ├── internvl2/                 ← Contiene notebooks de 1B y 2B
│   │   ├── qwen2vl/
│   │   └── paligemma2/
│   │
│   └── explicabilidad/                ← Fase aún no iniciada
│
└── (resultados consolidados — pendiente)
```

**Convención de nombres de archivos de resultados:**
```
resultados_{benchmark}_{nombre_modelo}.txt    ← resumen de métricas
detalle_{benchmark}_{nombre_modelo}.csv       ← una fila por pregunta
```

---

## 8. Resultados actuales

### 8.1 TallyQA — Conteo simple y complejo

> **Muestra:** n=50 preguntas por modelo (piloto). Semilla=42. Ver sección 9 para discusión sobre confiabilidad con esta muestra.

| Modelo | Accuracy | MAE | Parse fail | Tiempo/q | VRAM pico |
|---|---|---|---|---|---|
| Moondream2 | 90.0% | 0.36 | 0.0% | 2.27s ±0.89 | 5,020 MB |
| Qwen2-VL-2B | 86.0% | 0.40 | 0.0% | 1.17s ±0.33 | 5,003 MB |
| InternVL2-1B | 80.0% | 0.46 | 0.0% | 3.13s ±0.95 | 2,350 MB |
| PaliGemma2-3B | 72.3%* | 0.57 | 6.0%† | 2.53s ±0.37 | 6,104 MB |

*Calculado sobre 47 preguntas válidas (3 excluidas por parse_fail)  
†Las 3 preguntas sin parseo son negativas del modelo: *"Sorry, as a base VLM I am not trained to answer this question"*, no errores de parseo

**Desglose por rango de conteo:**

| Modelo | GT=0-2 (n≈43) | GT=3-5 (n≈5) | GT=6-15 (n≈2) |
|---|---|---|---|
| Moondream2 | 97.7% (MAE=0.02) | 40.0% (MAE=1.40) | 50.0% (MAE=5.00) |
| Qwen2-VL-2B | 95.3% (MAE=0.05) | 40.0% (MAE=1.40) | 0.0% (MAE=5.50) |
| InternVL2-1B | 88.4% (MAE=0.12) | 40.0% (MAE=1.20) | 0.0% (MAE=6.00) |
| PaliGemma2-3B | 78.0% (MAE=0.27) | 50.0% (MAE=1.25) | 0.0% (MAE=5.50) |

> El rango GT=6-15 tiene solo n=2 preguntas en el piloto de 50. Las conclusiones sobre este rango **no son estadísticamente confiables**. Se requiere n≥300 para tener n≥10 en ese rango con distribución natural del dataset.

**Desglose por tipo de pregunta:**

| Modelo | Simple | Compleja |
|---|---|---|
| Moondream2 | 93.3% | 85.0% |
| Qwen2-VL-2B | 90.0% | 80.0% |
| InternVL2-1B | 86.7% | 70.0% |
| PaliGemma2-3B | 83.3% | 52.9% |

---

### 8.2 CAPTURe — Conteo con oclusión

> **Muestra:** n=50 real + n=50 sintético por modelo (piloto), excepto Moondream2 que tiene dataset completo (n=824 real + n=1,150 sintético).

#### Subset real (objetos cotidianos, GT rango 8–907)

| Modelo | n | Accuracy exacta | MAE | VRAM pico |
|---|---|---|---|---|
| Moondream2 | 824 | 4.0% | 50.20 | 5,304 MB |
| Qwen2-VL-2B | 50 | 10.0% | 23.56 | 4,785 MB |
| InternVL2-1B | 50 | 2.0% | 41.90 | 2,350 MB |
| PaliGemma2-3B | 50 | 0.0% | 32.28 | 6,099 MB |

**Desglose por magnitud (CAPTURe real, todos los modelos a n=50 o n=824):**

| Bucket GT | Moondream2 (n=824) | Qwen2-VL (n=50) | InternVL2-1B (n=50) | PaliGemma2 (n=50) |
|---|---|---|---|---|
| 8–15 | 13.4% acc, MAE=4.9 | 33.3% acc, MAE=2.9 | 8.3% acc, MAE=4.8 | 0.0% acc, MAE=7.8 |
| 16–28 | 0.0% acc, MAE=10.6 | 0.0% acc, MAE=7.3 | 0.0% acc, MAE=10.4 | 0.0% acc, MAE=9.3 |
| 29–67 | 0.0% acc, MAE=30.5 | 0.0% acc, MAE=20.9 | 0.0% acc, MAE=23.6 | 0.0% acc, MAE=25.2 |
| 68–907 | 1.5% acc, MAE=155.4 | 6.3% acc, MAE=52.9 | 0.0% acc, MAE=104.8 | 0.0% acc, MAE=72.3 |

**Patrón de "techo de respuesta":** los modelos pequeños no generan predicciones mayores a cierto umbral, independiente de la cantidad real de objetos. Los techos observados por modelo:

| Modelo | Techo de respuesta observado |
|---|---|
| Moondream2 | ~12–14 (nunca supera 15 en las corridas vistas) |
| InternVL2-1B | ~12 (respuesta "12" aparece en múltiples errores grandes) |
| PaliGemma2-3B | ~10–50 (rango variable, sin valor fijo claro) |
| Qwen2-VL-2B | ~100 (puede generar tres dígitos; predijo correctamente GT=104) |

Qwen2-VL es cualitativamente distinto: no tiene un techo duro bajo, sino que satura en valores redondos (~100). El hecho de que predijo GT=104 correctamente indica que el modelo puede generar números de tres dígitos, pero su representación de densidades muy altas es imprecisa.

#### Subset sintético (formas geométricas, GT rango 5–15, con `num_occluded`)

| Modelo | n | Accuracy exacta | MAE |
|---|---|---|---|
| Moondream2 | 1,150 | 15.3% | 2.01 |
| InternVL2-1B | 50 | 10.0% | 3.42 |
| PaliGemma2-3B | 50 | 6.0% | 2.38 |
| Qwen2-VL-2B | 50 | 6.0% | 3.64 |

**Efecto de oclusión (`num_occluded`) — Moondream2 (n=1,150, único con muestra suficiente):**

| Objetos ocluidos | n | Accuracy | MAE |
|---|---|---|---|
| 1 | 402 | 17.7% | 1.19 |
| 2 | 154 | 30.5% | 1.62 |
| 3 | 368 | 13.6% | 2.02 |
| 4 | 55 | 7.3% | 3.02 |
| 5 | 75 | 2.7% | 3.03 |
| ≥6 | 96 | ~2% | 4–7 |

El patrón es no-monótono: `num_occluded=2` es más fácil que `num_occluded=1`, posiblemente porque dos objetos parcialmente tapados crean un patrón visual más reconocible que uno solo. A partir de `num_occluded=4` la accuracy colapsa hacia cero.

---

### 8.3 OmniSpatial — Razonamiento espacial

> **Muestra:** n=100 preguntas por track (400 total por modelo). Semilla=42. Se incluyen los 5 modelos que corrieron el benchmark.

| Modelo | Global | Geometric | Motion | Egocentric | Allocentric | VRAM pico | t/q |
|---|---|---|---|---|---|---|---|
| *Baseline mayoría* | — | 27.0% | 31.0% | 36.0% | 28.0% | — | — |
| InternVL2-1B | 33.2% | 25.0% | 26.0% | 49.0% | 33.0% | 2,403 MB | 0.61s |
| Moondream2 | 35.8% | 32.0% | 31.0% | 60.0% | 20.0% | 5,304 MB | 3.13s |
| Qwen2-VL-2B | 39.2% | 27.0% | 37.0% | 59.0% | 34.0% | 4,874 MB | 1.66s |
| InternVL2-2B† | 39.2% | 27.0% | 42.0% | 60.0% | 28.0% | 4,969 MB | 0.96s |
| PaliGemma2-3B | **44.5%** | **32.0%** | 40.0% | 58.0% | **48.0%** | 6,102 MB | 2.84s |

†InternVL2-2B descartado del eje de conteo; sus resultados espaciales se incluyen para referencia.

**Observaciones clave:**

**Geometric_Reasoning — todos los modelos al nivel del azar.** El rango es 25–32% con un baseline de mayoría de 27%. Ningún modelo muestra señal real de razonamiento geométrico 3D abstracto (rotación mental, proyecciones, unfolding de poliedros). Es el resultado más limpio del estudio y el que mejor apoya la hipótesis de sesgo 2D.

**Egocentric — todos los modelos significativamente sobre el azar.** Rango 49–60% vs. baseline 36%. Las preguntas desde el punto de vista del observador aprovechan representaciones que el entrenamiento en imágenes 2D sí desarrolla bien.

**Allocentric — el discriminador más informativo.** Baseline 28%. La mayoría de modelos cae cerca del azar (28–34%), con dos excepciones: **PaliGemma2 alcanza 48%** — la única señal real de razonamiento de perspectiva de terceros — y **Moondream2 cae a 20%**, por debajo del azar, lo que sugiere confusión sistemática (el modelo invierte perspectivas consistentemente).

**Geometric_Reasoning — detalle por tipo de pregunta:**

| Modelo | Con opciones texto (n=14) | Sin opciones texto / visual (n=86) |
|---|---|---|
| Moondream2 | 28.6% | 32.6% |
| InternVL2-1B | 28.6% | 24.4% |
| InternVL2-2B | 42.9% | 24.4% |
| Qwen2-VL-2B | 28.6% | 26.7% |
| PaliGemma2-3B | 28.6% | 32.6% |

No hay diferencia sistemática entre preguntas con y sin opciones de texto: ambos subtipos quedan en el rango 25–35%, confirmando que el problema no es de formato sino de capacidad de razonamiento geométrico.

---

## 9. Tamaños de muestra y confiabilidad

### Conteo (TallyQA y CAPTURe)

El tamaño de muestra actual para conteo es **n=50 por modelo** (salvo Moondream2 CAPTURe, que tiene el dataset completo). Este tamaño es suficiente para establecer el patrón grueso (todos los modelos tienen accuracy alta en GT=0-2 y colapsan en magnitudes altas), pero insuficiente para análisis fino:

| Problema con n=50 | Consecuencia |
|---|---|
| Solo ~2 preguntas en GT=6-15 | Conclusiones sobre magnitudes altas son anecdóticas |
| Intervalos de confianza amplios | Un modelo con 86% ± ~10% no es significativamente distinto de uno con 80% ± ~11% |
| Desglose por tipo (simple/compleja) con n=20-30 | Poca potencia estadística por subgrupo |

**Cambio recomendado para TallyQA:** escalar a **n=300** por modelo. Con el muestreo estratificado actual, n=300 garantiza ~12 preguntas en el rango GT=6-15 (distribución natural del dataset). El código existente solo requiere cambiar `SAMPLE_SIZE = 300`; el tiempo de corrida estimado es 10–15 minutos adicionales por modelo en la T4.

**CAPTURe real:** el patrón de 0% accuracy en todos los modelos para buckets GT>28 es tan consistente que n=50 es suficiente para esta conclusión. Sin embargo, si se quiere analizar el efecto de `num_occluded` en el subset sintético con granularidad, también se recomienda escalar a n=200–300.

### Razonamiento espacial (OmniSpatial)

El tamaño actual es **n=100 por track** (400 total por modelo). Este es un tamaño razonable para el alcance del estudio:

- Con 100 preguntas por track y 4 opciones, el baseline teórico de azar uniforme es 25%. La mayoría de los resultados están a más de 5 puntos porcentuales del baseline.
- Los patrones observados (Geometric ~ azar, Egocentric claramente sobre azar, Allocentric discriminante) son robustos y consistentes en todos los modelos.
- Escalar OmniSpatial requeriría rebalancear los tracks (algunos tienen pocos ejemplos en total), y no es prioritario dado que los resultados actuales ya soportan las conclusiones centrales.

**En resumen:** el trabajo pendiente de escalar n se concentra principalmente en **TallyQA** (todos los modelos de n=50 a n=300). CAPTURe y OmniSpatial son secundarios.

---

## 10. Estado del proyecto

### Progreso de evaluaciones

| Modelo | TallyQA | CAPTURe | OmniSpatial |
|---|---|---|---|
| Moondream2 | ✅ n=50 | ✅ n=824+1150 (completo) | ✅ n=400 |
| Qwen2-VL-2B | ✅ n=50 | ✅ n=50+50 | ✅ n=400 |
| InternVL2-1B | ✅ n=50* | ✅ n=50+50 | ✅ n=400 |
| InternVL2-2B | — (descartado) | — (descartado) | ✅ n=400 (ref.) |
| PaliGemma2-3B | ✅ n=50 | ✅ n=50+50 | ✅ n=400 |

*Resultado reconstruido desde outputs del notebook; el .txt original no fue descargado de Colab.

### Fases pendientes

**Escala de conteo (próximo):**  
Incrementar TallyQA de n=50 a n=300 para los 4 modelos activos. Solo requiere cambiar `SAMPLE_SIZE` y re-correr cada notebook. Estimado: 1 sesión de Colab por modelo.

**Explicabilidad / grounding (diseño en progreso):**  
La fase de explicabilidad tiene dos técnicas candidatas:

1. **Oclusión sistemática:** cubrir la imagen en grilla N×N, registrar la variación en la predicción por celda. Las celdas que más afectan la predicción son las más "relevantes" para el modelo. Comparar contra los bounding boxes de CAPTURe real para verificar si la atención coincide con los objetos.

2. **Visualización de atención cruzada:** PaliGemma2 y Qwen2-VL exponen mapas de atención del encoder visual. Se puede proyectar la atención asociada al token de respuesta sobre la imagen original.

CAPTURe real es el candidato natural para explicabilidad: tiene bounding boxes de ground truth, tiene los casos de mayor error (GT=170+, pred≈12), y Moondream2 ya tiene el dataset completo corrido.

**Sincronización con la propuesta escrita:**  
El documento `propuesta_memoria.docx` requiere actualización para reflejar los resultados actuales, la decisión de descarte de InternVL2-2B, y los hallazgos preliminares del eje espacial.

---

## Reproducibilidad

Todas las corridas usan `RANDOM_SEED = 42` y `revision="main"` al cargar modelos desde HuggingFace. Para reproducción exacta, fijar la revisión al commit hash correspondiente a la fecha de corrida (ver campo `FECHA` en cada archivo `.txt` de resultados).

Dependencias clave por modelo:

| Modelo | transformers | Notas |
|---|---|---|
| Moondream2 | ==4.57.6 | Fork propio; instalar desde `vikhyatk/moondream2` |
| InternVL2 | ==4.37.2 | Versión anterior requerida por `trust_remote_code` |
| Qwen2-VL | >=4.46.2 | Requiere `qwen_vl_utils` adicional |
| PaliGemma2 | >=4.46.2 | Token `<image>` debe incluirse explícitamente en el prompt |

Cada notebook incluye en su celda 1 la instalación exacta de dependencias. No existe una versión única de `transformers` compatible con los cuatro modelos; cada modelo se ejecuta en sesión de Colab independiente.
