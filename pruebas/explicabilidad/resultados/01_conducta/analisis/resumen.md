# Resultados de conducta (oclusión + grounding), moondream2

120 preguntas, 480 consultas. IC 95 % de Wilson entre corchetes.
Determinismo: 10/10 respuestas idénticas al repetir (verificado en Colab; info_corrida.json registra 0 por un error de la celda de verificación, ya corregido).


## Respuesta en la imagen original (c0)

- Acierto exacto: 12.5 % [7.7–19.6] (n=120)
- Error medio (predicción − correcta): -2.32; mediana -2
- Cuenta de menos: 85.8 % [78.5–91.0] (n=120); cuenta de más: 1.7 % [0.5–5.9] (n=120)
- Grupos: cercano 57, lejano 48, acierto 15
- Número favorito (10 o 100, fijado en DISENO.md): 0
- Repertorio de respuestas en c0: 1×2, 2×37, 3×33, 4×20, 6×28
- Respuesta máxima en c0: 6 (GT máxima 10)
- Pendiente de la respuesta contra la respuesta correcta: 0.45 (1 = escala correcta)

Respuesta en c0 (columnas) según respuesta correcta (filas):

|   gt |   1 |   2 |   3 |   4 |   6 |
|-----:|----:|----:|----:|----:|----:|
|    2 |   0 |   8 |   1 |   0 |   0 |
|    3 |   2 |  10 |   4 |   0 |   0 |
|    4 |   0 |  12 |   7 |   0 |   0 |
|    5 |   0 |   3 |   7 |   4 |   1 |
|    6 |   0 |   2 |   7 |   6 |   3 |
|    7 |   0 |   1 |   2 |   2 |   3 |
|    8 |   0 |   0 |   1 |   3 |   4 |
|    9 |   0 |   0 |   2 |   3 |   9 |
|   10 |   0 |   1 |   2 |   2 |   8 |

## Oclusión

- Δ1 = −1 (borrar 1 objetivo baja 1): 30.8 % [23.3–39.6] (n=120)
- Δ2 = −2 (borrar 2 objetivos baja 2): 22.5 % [15.9–30.8] (n=120)
- Control estable (borrar 1 no objetivo no cambia): 89.2 % [82.3–93.6] (n=120)
- La respuesta cambia al borrar 1 objetivo: 42.5 % [34.0–51.4] (n=120); al borrar 1 no objetivo: 10.8 % [6.4–17.7] (n=120)
- Pendiente media: -0.43 (ideal −1; 0 = no reacciona)
- Categorías: direccion_correcta 63, no_reacciona 42, cuenta 11, otra 4

Por nivel:

|   num_shapes |   n |   cuenta |   no_reacciona |   pendiente |   control_estable |   acierto_c0 |
|-------------:|----:|---------:|---------------:|------------:|------------------:|-------------:|
|           15 |  24 |     20.8 |           33.3 |        -0.4 |              95.8 |         25   |
|           25 |  24 |      8.3 |           29.2 |        -0.4 |              83.3 |         12.5 |
|           35 |  24 |     12.5 |           29.2 |        -0.4 |              83.3 |         12.5 |
|           45 |  24 |      0   |           50   |        -0.4 |              95.8 |          8.3 |
|           55 |  24 |      4.2 |           33.3 |        -0.5 |              87.5 |          4.2 |

Por tipo:

| tipo         |   n |   cuenta |   no_reacciona |   pendiente |   control_estable |   acierto_c0 |
|:-------------|----:|---------:|---------------:|------------:|------------------:|-------------:|
| conteo_color |  60 |      8.3 |           26.7 |        -0.5 |              86.7 |         23.3 |
| conteo_forma |  60 |     10   |           43.3 |        -0.4 |              91.7 |          1.7 |

Por grupo:

| grupo   |   n |   cuenta |   no_reacciona |   pendiente |   control_estable |   acierto_c0 |
|:--------|----:|---------:|---------------:|------------:|------------------:|-------------:|
| acierto |  15 |     20   |           13.3 |        -0.7 |              80   |          100 |
| cercano |  57 |      7   |           36.8 |        -0.4 |              93   |            0 |
| lejano  |  48 |      8.3 |           39.6 |        -0.4 |              87.5 |            0 |

## Grounding (point en c0)

- Puntos por pregunta: media 6.58; GT media 5.84; predicción c0 media 3.52
- n.º de puntos = GT: 25.0 % [18.1–33.4] (n=120)
- n.º de puntos = respuesta de query: 13.3 % [8.4–20.6] (n=120)
- Precisión (puntos sobre una figura objetivo): 77.0 % de 790 puntos
- Puntos sobre figura no objetivo: 108; sobre fondo: 74
- Cobertura (figuras objetivo encontradas): 68.6 % de 701
- Preguntas sin ningún punto: 2; con 100 puntos (salida degenerada, tope de max_objects): 2
- Figuras objetivo encontradas = GT: 27.5 % [20.3–36.1] (n=120) (query acierta 12.5 % [7.7–19.6] (n=120))
- Error medio: figuras objetivo encontradas − GT = -1.83; query − GT = -2.32

| tipo         |   gt |   n_puntos |   c0 |   precision_point |   cobertura_point |
|:-------------|-----:|-----------:|-----:|------------------:|------------------:|
| conteo_color | 4.72 |       4.4  | 3.18 |              0.89 |              0.82 |
| conteo_forma | 6.97 |       8.77 | 3.87 |              0.85 |              0.63 |

## Muestra para los mapas (rollout y Grad-CAM)

| qid   | grupo   |   orden_en_grupo |   num_shapes | tipo         | objetivo   |   gt |   c0 | pregunta                                           | imagen_v2            |
|:------|:--------|-----------------:|-------------:|:-------------|:-----------|-----:|-----:|:---------------------------------------------------|:---------------------|
| q002  | acierto |                1 |           15 | conteo_forma | rombo      |    2 |    2 | How many diamonds are there in the image?          | escena_0036_n015.png |
| q065  | acierto |                2 |           35 | conteo_color | rojo       |    3 |    3 | How many red shapes are there in the image?        | escena_0111_n035.png |
| q016  | acierto |                3 |           15 | conteo_color | rojo       |    2 |    2 | How many red shapes are there in the image?        | escena_0045_n015.png |
| q071  | acierto |                4 |           35 | conteo_color | rojo       |    2 |    2 | How many red shapes are there in the image?        | escena_0096_n035.png |
| q091  | acierto |                5 |           45 | conteo_color | rosado     |    6 |    6 | How many pink shapes are there in the image?       | escena_0123_n045.png |
| q019  | acierto |                6 |           15 | conteo_color | amarillo   |    2 |    2 | How many yellow shapes are there in the image?     | escena_0043_n015.png |
| q039  | acierto |                7 |           25 | conteo_color | rosado     |    6 |    6 | How many pink shapes are there in the image?       | escena_0085_n025.png |
| q031  | cercano |                1 |           25 | conteo_forma | triangulo  |    3 |    2 | How many triangles are there in the image?         | escena_0062_n025.png |
| q038  | cercano |                2 |           25 | conteo_color | celeste    |    4 |    2 | How many light blue shapes are there in the image? | escena_0075_n025.png |
| q029  | cercano |                3 |           25 | conteo_forma | cuadrado   |    2 |    3 | How many squares are there in the image?           | escena_0069_n025.png |
| q062  | cercano |                4 |           35 | conteo_color | rosado     |    5 |    4 | How many pink shapes are there in the image?       | escena_0108_n035.png |
| q015  | cercano |                5 |           15 | conteo_color | rosado     |    4 |    3 | How many pink shapes are there in the image?       | escena_0044_n015.png |
| q005  | cercano |                6 |           15 | conteo_forma | triangulo  |    3 |    2 | How many triangles are there in the image?         | escena_0035_n015.png |
| q092  | cercano |                7 |           45 | conteo_color | azul       |    5 |    4 | How many blue shapes are there in the image?       | escena_0135_n045.png |
| q099  | lejano  |                1 |           55 | conteo_forma | triangulo  |    9 |    4 | How many triangles are there in the image?         | escena_0152_n055.png |
| q058  | lejano  |                2 |           35 | conteo_forma | rombo      |    8 |    4 | How many diamonds are there in the image?          | escena_0100_n035.png |
| q048  | lejano  |                3 |           35 | conteo_forma | triangulo  |   10 |    6 | How many triangles are there in the image?         | escena_0103_n035.png |
| q024  | lejano  |                4 |           25 | conteo_forma | triangulo  |    9 |    6 | How many triangles are there in the image?         | escena_0063_n025.png |
| q110  | lejano  |                5 |           55 | conteo_color | rojo       |    9 |    6 | How many red shapes are there in the image?        | escena_0165_n055.png |
| q068  | lejano  |                6 |           35 | conteo_color | verde      |    5 |    2 | How many green shapes are there in the image?      | escena_0107_n035.png |