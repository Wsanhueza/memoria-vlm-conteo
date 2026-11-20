# Resultados de conducta (oclusión + grounding), moondream2

120 preguntas, 480 consultas. IC 95 % de Wilson entre corchetes.
Determinismo: 10/10 respuestas idénticas al repetir (verificado en Colab; info_corrida.json registra 0 por un error de la celda de verificación, ya corregido).


## Respuesta en la imagen original (c0)

- Acierto exacto: 25.0 % [18.1–33.4] (n=120)
- Error medio (predicción − correcta): -1.78; mediana -1
- Cuenta de menos: 69.2 % [60.4–76.7] (n=120); cuenta de más: 5.8 % [2.9–11.6] (n=120)
- Grupos: cercano 53, lejano 37, acierto 30
- Número favorito (10 o 100, fijado en DISENO.md): 0
- Repertorio de respuestas en c0: 2×30, 3×31, 4×30, 6×26, 8×3
- Respuesta máxima en c0: 8 (GT máxima 10)
- Pendiente de la respuesta contra la respuesta correcta: 0.40 (1 = escala correcta)

Respuesta en c0 (columnas) según respuesta correcta (filas):

|   gt |   2 |   3 |   4 |   6 |   8 |
|-----:|----:|----:|----:|----:|----:|
|    2 |  11 |   1 |   0 |   0 |   0 |
|    3 |  11 |  10 |   1 |   0 |   0 |
|    4 |   4 |   4 |   2 |   2 |   0 |
|    5 |   1 |   7 |   6 |   3 |   0 |
|    6 |   1 |   1 |   6 |   6 |   0 |
|    7 |   2 |   4 |   6 |   5 |   0 |
|    8 |   0 |   2 |   3 |   1 |   1 |
|    9 |   0 |   1 |   2 |   1 |   1 |
|   10 |   0 |   1 |   4 |   8 |   1 |

## Oclusión

- Δ1 = −1 (borrar 1 objetivo baja 1): 30.8 % [23.3–39.6] (n=120)
- Δ2 = −2 (borrar 2 objetivos baja 2): 27.5 % [20.3–36.1] (n=120)
- Control estable (borrar 1 no objetivo no cambia): 92.5 % [86.4–96.0] (n=120)
- La respuesta cambia al borrar 1 objetivo: 39.2 % [30.9–48.1] (n=120); al borrar 1 no objetivo: 7.5 % [4.0–13.6] (n=120)
- Pendiente media: -0.50 (ideal −1; 0 = no reacciona)
- Categorías: direccion_correcta 62, no_reacciona 39, cuenta 15, otra 4

Por nivel:

|   num_shapes |   n |   cuenta |   no_reacciona |   pendiente |   control_estable |   acierto_c0 |
|-------------:|----:|---------:|---------------:|------------:|------------------:|-------------:|
|           15 |  24 |     29.2 |           25   |        -0.6 |              91.7 |         41.7 |
|           25 |  24 |     12.5 |           25   |        -0.5 |              95.8 |         25   |
|           35 |  24 |      4.2 |           33.3 |        -0.5 |              95.8 |         20.8 |
|           45 |  24 |     12.5 |           20.8 |        -0.7 |              83.3 |         20.8 |
|           55 |  24 |      4.2 |           58.3 |        -0.3 |              95.8 |         16.7 |

Por tipo:

| tipo         |   n |   cuenta |   no_reacciona |   pendiente |   control_estable |   acierto_c0 |
|:-------------|----:|---------:|---------------:|------------:|------------------:|-------------:|
| conteo_color |  60 |       20 |             20 |        -0.7 |              93.3 |         43.3 |
| conteo_forma |  60 |        5 |             45 |        -0.3 |              91.7 |          6.7 |

Por grupo:

| grupo   |   n |   cuenta |   no_reacciona |   pendiente |   control_estable |   acierto_c0 |
|:--------|----:|---------:|---------------:|------------:|------------------:|-------------:|
| acierto |  30 |     26.7 |           10   |        -0.7 |              93.3 |          100 |
| cercano |  53 |     11.3 |           26.4 |        -0.5 |              96.2 |            0 |
| lejano  |  37 |      2.7 |           59.5 |        -0.2 |              86.5 |            0 |

## Grounding (point en c0)

- Puntos por pregunta: media 4.91; GT media 5.56; predicción c0 media 3.77
- n.º de puntos = GT: 30.0 % [22.5–38.7] (n=120)
- n.º de puntos = respuesta de query: 18.3 % [12.4–26.2] (n=120)
- Precisión (puntos sobre una figura objetivo): 82.7 % de 589 puntos
- Puntos sobre figura no objetivo: 102; sobre fondo: 0
- Cobertura (figuras objetivo encontradas): 72.4 % de 667
- Preguntas sin ningún punto: 10; con 100 puntos (salida degenerada, tope de max_objects): 0
- Figuras objetivo encontradas = GT: 48.3 % [39.6–57.2] (n=120) (query acierta 25.0 % [18.1–33.4] (n=120))
- Error medio: figuras objetivo encontradas − GT = -1.53; query − GT = -1.78

| tipo         |   gt |   n_puntos |   c0 |   precision_point |   cobertura_point |
|:-------------|-----:|-----------:|-----:|------------------:|------------------:|
| conteo_color | 4.53 |       5    | 3.92 |              0.86 |              0.91 |
| conteo_forma | 6.58 |       4.82 | 3.63 |              0.9  |              0.66 |

## Muestra para los mapas (rollout y Grad-CAM)

| qid   | grupo   |   orden_en_grupo |   num_shapes | tipo         | objetivo   |   gt |   c0 | pregunta                                           | imagen_v2            |
|:------|:--------|-----------------:|-------------:|:-------------|:-----------|-----:|-----:|:---------------------------------------------------|:---------------------|
| q040  | acierto |                1 |           25 | conteo_color | naranjo    |    2 |    2 | How many orange shapes are there in the image?     | escena_0083_n025.png |
| q022  | acierto |                2 |           15 | conteo_color | rosado     |    3 |    3 | How many pink shapes are there in the image?       | escena_0049_n015.png |
| q018  | acierto |                3 |           15 | conteo_color | morado     |    3 |    3 | How many purple shapes are there in the image?     | escena_0048_n015.png |
| q007  | acierto |                4 |           15 | conteo_forma | triangulo  |    2 |    2 | How many triangles are there in the image?         | escena_0053_n015.png |
| q108  | acierto |                5 |           55 | conteo_color | azul       |    8 |    8 | How many blue shapes are there in the image?       | escena_0163_n055.png |
| q016  | acierto |                6 |           15 | conteo_color | rojo       |    2 |    2 | How many red shapes are there in the image?        | escena_0045_n015.png |
| q074  | acierto |                7 |           45 | conteo_forma | rombo      |    3 |    3 | How many diamonds are there in the image?          | escena_0137_n045.png |
| q054  | cercano |                1 |           35 | conteo_forma | triangulo  |    5 |    3 | How many triangles are there in the image?         | escena_0106_n035.png |
| q010  | cercano |                2 |           15 | conteo_forma | rombo      |    3 |    2 | How many diamonds are there in the image?          | escena_0041_n015.png |
| q085  | cercano |                3 |           45 | conteo_color | azul       |    7 |    6 | How many blue shapes are there in the image?       | escena_0122_n045.png |
| q017  | cercano |                4 |           15 | conteo_color | azul       |    3 |    2 | How many blue shapes are there in the image?       | escena_0055_n015.png |
| q011  | cercano |                5 |           15 | conteo_forma | triangulo  |    4 |    3 | How many triangles are there in the image?         | escena_0031_n015.png |
| q093  | cercano |                6 |           45 | conteo_color | rosado     |    7 |    6 | How many pink shapes are there in the image?       | escena_0140_n045.png |
| q089  | cercano |                7 |           45 | conteo_color | morado     |    7 |    6 | How many purple shapes are there in the image?     | escena_0143_n045.png |
| q113  | lejano  |                1 |           55 | conteo_color | celeste    |   10 |    6 | How many light blue shapes are there in the image? | escena_0175_n055.png |
| q078  | lejano  |                2 |           45 | conteo_forma | rombo      |    9 |    3 | How many diamonds are there in the image?          | escena_0131_n045.png |
| q056  | lejano  |                3 |           35 | conteo_forma | circulo    |    7 |    2 | How many circles are there in the image?           | escena_0118_n035.png |
| q029  | lejano  |                4 |           25 | conteo_forma | cuadrado   |    6 |    3 | How many squares are there in the image?           | escena_0081_n025.png |
| q028  | lejano  |                5 |           25 | conteo_forma | circulo    |    7 |    4 | How many circles are there in the image?           | escena_0077_n025.png |
| q079  | lejano  |                6 |           45 | conteo_forma | circulo    |    9 |    6 | How many circles are there in the image?           | escena_0133_n045.png |