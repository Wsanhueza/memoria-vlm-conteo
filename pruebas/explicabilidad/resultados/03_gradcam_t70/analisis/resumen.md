# Grad-CAM de moondream2: resultados y cruce con la oclusión

20 preguntas de la muestra + 2 controles. Verificación: la pasada con gradientes elige el mismo número que query() (5/5).
Enriquecimiento: fracción del mapa sobre la región / fracción del área que ocupa (1 = sin preferencia).

## gradcam_llm

- Figuras objetivo: 0.35 (mediana 0.06)
- Otras figuras: 0.28 (mediana 0.17)
- Fondo: 1.09 (mediana 1.09)
- Objetivo > otras figuras en 8/20 imágenes
- Percentil del token de la figura borrada en c1: 14.24 (mediana 0.00); de la borrada en control: 18.37 (mediana 0.00)

## gradcam_enc

- Figuras objetivo: 0.69 (mediana 0.23)
- Otras figuras: 0.78 (mediana 0.66)
- Fondo: 1.04 (mediana 1.05)
- Objetivo > otras figuras en 7/20 imágenes
- Percentil del token de la figura borrada en c1: 24.23 (mediana 0.00); de la borrada en control: 37.12 (mediana 12.30)

## Grad × entrada (con signo): contribución media por token

- Objetivo 0.05 (mediana 0.02); otras figuras -0.00 (mediana -0.00); fondo -0.00 (mediana -0.00)
- Objetivo > fondo en 18/20; otras > fondo en 12/20

## Cruce con la oclusión (¿la respuesta cambió al borrar 1 objetivo?)

| cambio   |   ('gradcam_llm_pct_borrada_c1', 'mean') |   ('gradcam_llm_pct_borrada_c1', 'count') |   ('gradcam_llm_enriq_objetivo', 'mean') |   ('gradcam_llm_enriq_objetivo', 'count') |   ('gxi_objetivo', 'mean') |   ('gxi_objetivo', 'count') |
|:---------|-----------------------------------------:|------------------------------------------:|-----------------------------------------:|------------------------------------------:|---------------------------:|----------------------------:|
| False    |                                     4.58 |                                        10 |                                     0.08 |                                        10 |                       0.03 |                          10 |
| True     |                                    23.9  |                                        10 |                                     0.63 |                                        10 |                       0.07 |                          10 |

## Por grupo

| grupo   |   gradcam_llm_enriq_objetivo |   gradcam_llm_enriq_otras |   gradcam_llm_enriq_fondo |
|:--------|-----------------------------:|--------------------------:|--------------------------:|
| acierto |                         0.88 |                      0.5  |                      1.06 |
| cercano |                         0.07 |                      0.17 |                      1.1  |
| lejano  |                         0.06 |                      0.14 |                      1.12 |

## Por imagen

| qid   | grupo   |   num_shapes | tipo         |   prediccion |   gt |   delta_c1 |   delta_control |   gradcam_llm_enriq_objetivo |   gradcam_llm_enriq_otras |   gradcam_llm_enriq_fondo |   gradcam_llm_pct_borrada_c1 |   gradcam_llm_pct_borrada_control |   gradcam_enc_enriq_objetivo |   gradcam_enc_enriq_otras |   gradcam_enc_enriq_fondo |   gradcam_enc_pct_borrada_c1 |   gradcam_enc_pct_borrada_control |   gxi_objetivo |   gxi_otras |   gxi_fondo |
|:------|:--------|-------------:|:-------------|-------------:|-----:|-----------:|----------------:|-----------------------------:|--------------------------:|--------------------------:|-----------------------------:|----------------------------------:|-----------------------------:|--------------------------:|--------------------------:|-----------------------------:|----------------------------------:|---------------:|------------:|------------:|
| q040  | acierto |           25 | conteo_color |            2 |    2 |         -1 |               0 |                         0.54 |                      0.36 |                      1.06 |                         71.2 |                              29.6 |                         0.58 |                      0.56 |                      1.04 |                         73.9 |                               0   |           0.25 |        0    |          -0 |
| q022  | acierto |           15 | conteo_color |            3 |    3 |         -1 |               0 |                         2.56 |                      0.81 |                      0.99 |                         68.3 |                              84.8 |                         6.48 |                      5.42 |                      0.76 |                         85.3 |                              94.2 |           0.13 |       -0.01 |          -0 |
| q018  | acierto |           15 | conteo_color |            3 |    3 |         -1 |               0 |                         0    |                      0.2  |                      1.04 |                          0   |                              36.6 |                         0.03 |                      0.79 |                      1.02 |                          0   |                              92.5 |           0.06 |       -0.02 |          -0 |
| q007  | acierto |           15 | conteo_forma |            2 |    2 |         -1 |               0 |                         0.01 |                      0.35 |                      1.04 |                          0   |                              45.7 |                         0.04 |                      0.71 |                      1.02 |                          0   |                              81.9 |          -0.03 |       -0    |          -0 |
| q108  | acierto |           55 | conteo_color |            8 |    8 |          0 |               0 |                         0.14 |                      0.41 |                      1.14 |                          0   |                              44.9 |                         0.38 |                      1.19 |                      0.98 |                          0   |                              91.6 |           0.01 |        0    |          -0 |
| q016  | acierto |           15 | conteo_color |            2 |    2 |         -1 |               0 |                         2.94 |                      1.15 |                      0.98 |                         99.5 |                              44.3 |                         2.71 |                      0.81 |                      1    |                         99.6 |                              72.3 |           0.23 |        0    |           0 |
| q074  | acierto |           45 | conteo_forma |            3 |    3 |          0 |               0 |                         0    |                      0.21 |                      1.15 |                          0   |                               0   |                         0.27 |                      0.68 |                      1.06 |                          0   |                               0   |           0.02 |       -0    |          -0 |
| q054  | cercano |           35 | conteo_forma |            3 |    5 |          0 |               0 |                         0.05 |                      0.42 |                      1.08 |                          0   |                               0   |                         0.79 |                      1.18 |                      0.98 |                          0   |                              51.4 |           0.04 |       -0    |          -0 |
| q010  | cercano |           15 | conteo_forma |            2 |    3 |          0 |               0 |                         0    |                      0    |                      1.05 |                          0   |                               0   |                         0    |                      0.04 |                      1.05 |                          0   |                               0   |           0.11 |       -0    |          -0 |
| q085  | cercano |           45 | conteo_color |            6 |    7 |          0 |               0 |                         0.08 |                      0.14 |                      1.15 |                          0   |                               0   |                         0.1  |                      0.64 |                      1.08 |                          0   |                               0   |          -0.02 |        0    |          -0 |
| q017  | cercano |           15 | conteo_color |            2 |    3 |          0 |               0 |                         0.04 |                      0.09 |                      1.05 |                          0   |                               0   |                         0.08 |                      0    |                      1.05 |                          0   |                               0   |           0.09 |        0    |          -0 |
| q011  | cercano |           15 | conteo_forma |            3 |    4 |         -1 |               0 |                         0.12 |                      0.43 |                      1.03 |                          0   |                              81.5 |                         0.5  |                      0.68 |                      1.02 |                         52.7 |                              91.1 |           0.04 |       -0    |           0 |
| q093  | cercano |           45 | conteo_color |            6 |    7 |         -2 |               0 |                         0.02 |                      0.01 |                      1.17 |                          0   |                               0   |                         0.04 |                      0.04 |                      1.17 |                          0   |                               0   |           0.01 |       -0.01 |          -0 |
| q089  | cercano |           45 | conteo_color |            6 |    7 |          0 |               0 |                         0.22 |                      0.13 |                      1.16 |                         45.8 |                               0   |                         0.32 |                      0.18 |                      1.15 |                         82.9 |                               0   |           0.09 |       -0    |          -0 |
| q113  | lejano  |           55 | conteo_color |            6 |   10 |          0 |               0 |                         0.15 |                      0.53 |                      1.11 |                          0   |                               0   |                         0.35 |                      1.17 |                      0.99 |                          0   |                              49.5 |          -0    |        0    |          -0 |
| q078  | lejano  |           45 | conteo_forma |            4 |    9 |          1 |               1 |                         0.11 |                      0.08 |                      1.15 |                          0   |                               0   |                         0.01 |                      0.09 |                      1.15 |                          0   |                               0   |           0.02 |       -0    |          -0 |
| q056  | lejano  |           35 | conteo_forma |            3 |    7 |         -1 |               0 |                         0    |                      0.14 |                      1.11 |                          0   |                               0   |                         0.88 |                      1.05 |                      1    |                         90.3 |                              93.4 |           0.01 |       -0    |          -0 |
| q029  | lejano  |           25 | conteo_forma |            3 |    6 |          0 |               0 |                         0.01 |                      0.01 |                      1.09 |                          0   |                               0   |                         0.06 |                      0    |                      1.09 |                          0   |                               0   |           0    |       -0    |          -0 |
| q028  | lejano  |           25 | conteo_forma |            4 |    7 |          0 |               0 |                         0.06 |                      0.05 |                      1.09 |                          0   |                               0   |                         0.06 |                      0.36 |                      1.07 |                          0   |                              24.6 |           0    |        0    |          -0 |
| q079  | lejano  |           45 | conteo_forma |            6 |    9 |         -2 |              -1 |                         0    |                      0.01 |                      1.15 |                          0   |                               0   |                         0.19 |                      0.03 |                      1.14 |                          0   |                               0   |           0    |       -0    |          -0 |