# Grad-CAM de moondream2: resultados y cruce con la oclusión

20 preguntas de la muestra + 2 controles. Verificación: la pasada con gradientes elige el mismo número que query() (5/5).
Enriquecimiento: fracción del mapa sobre la región / fracción del área que ocupa (1 = sin preferencia).

## gradcam_llm

- Figuras objetivo: 1.98 (mediana 0.08)
- Otras figuras: 2.07 (mediana 0.23)
- Fondo: 0.99 (mediana 1.02)
- Objetivo > otras figuras en 8/20 imágenes
- Percentil del token de la figura borrada en c1: 17.36 (mediana 0.00); de la borrada en control: 24.80 (mediana 4.05)

## gradcam_enc

- Figuras objetivo: 1.36 (mediana 0.76)
- Otras figuras: 1.13 (mediana 0.86)
- Fondo: 1.00 (mediana 1.00)
- Objetivo > otras figuras en 7/20 imágenes
- Percentil del token de la figura borrada en c1: 33.47 (mediana 8.80); de la borrada en control: 45.87 (mediana 57.60)

## Grad × entrada (con signo): contribución media por token

- Objetivo 0.01 (mediana 0.03); otras figuras -0.01 (mediana -0.01); fondo -0.00 (mediana -0.00)
- Objetivo > fondo en 14/20; otras > fondo en 5/20

## Cruce con la oclusión (¿la respuesta cambió al borrar 1 objetivo?)

| cambio   |   ('gradcam_llm_pct_borrada_c1', 'mean') |   ('gradcam_llm_pct_borrada_c1', 'count') |   ('gradcam_llm_enriq_objetivo', 'mean') |   ('gradcam_llm_enriq_objetivo', 'count') |   ('gxi_objetivo', 'mean') |   ('gxi_objetivo', 'count') |
|:---------|-----------------------------------------:|------------------------------------------:|-----------------------------------------:|------------------------------------------:|---------------------------:|----------------------------:|
| False    |                                     4.75 |                                         8 |                                     0.19 |                                         8 |                      -0.05 |                           8 |
| True     |                                    25.76 |                                        12 |                                     3.18 |                                        12 |                       0.05 |                          12 |

## Por grupo

| grupo   |   gradcam_llm_enriq_objetivo |   gradcam_llm_enriq_otras |   gradcam_llm_enriq_fondo |
|:--------|-----------------------------:|--------------------------:|--------------------------:|
| acierto |                         4.4  |                      1.75 |                      0.99 |
| cercano |                         1.22 |                      4.01 |                      0.95 |
| lejano  |                         0.05 |                      0.18 |                      1.03 |

## Por imagen

| qid   | grupo   |   num_shapes | tipo         |   prediccion |   gt |   delta_c1 |   delta_control |   gradcam_llm_enriq_objetivo |   gradcam_llm_enriq_otras |   gradcam_llm_enriq_fondo |   gradcam_llm_pct_borrada_c1 |   gradcam_llm_pct_borrada_control |   gradcam_enc_enriq_objetivo |   gradcam_enc_enriq_otras |   gradcam_enc_enriq_fondo |   gradcam_enc_pct_borrada_c1 |   gradcam_enc_pct_borrada_control |   gxi_objetivo |   gxi_otras |   gxi_fondo |
|:------|:--------|-------------:|:-------------|-------------:|-----:|-----------:|----------------:|-----------------------------:|--------------------------:|--------------------------:|-----------------------------:|----------------------------------:|-----------------------------:|--------------------------:|--------------------------:|-----------------------------:|----------------------------------:|---------------:|------------:|------------:|
| q002  | acierto |           15 | conteo_forma |            2 |    2 |          0 |               0 |                         0    |                      0.19 |                      1.01 |                          0   |                              58   |                         0    |                      0.1  |                      1.01 |                          0   |                               0   |           0.17 |       -0.02 |          -0 |
| q065  | acierto |           35 | conteo_color |            3 |    3 |          0 |               0 |                         0.13 |                      0.52 |                      1.02 |                         38   |                              51.6 |                         0.73 |                      1.22 |                      1    |                         62.6 |                              86   |           0.03 |       -0.01 |           0 |
| q016  | acierto |           15 | conteo_color |            2 |    2 |         -1 |               0 |                         0.44 |                      0.28 |                      1.01 |                          0   |                               0   |                         2.19 |                      0.82 |                      1    |                         93.1 |                              68.2 |           0.26 |       -0.01 |          -0 |
| q071  | acierto |           35 | conteo_color |            2 |    2 |          0 |               0 |                         0.34 |                      0.05 |                      1.03 |                          0   |                               0   |                         1.11 |                      0.72 |                      1.01 |                          0   |                              83   |          -0.67 |        0    |          -0 |
| q091  | acierto |           45 | conteo_color |            6 |    6 |          0 |               0 |                         0.56 |                      0.36 |                      1.03 |                          0   |                              28.1 |                         2.03 |                      1.94 |                      0.96 |                         63.1 |                              87.9 |           0.1  |        0.01 |          -0 |
| q019  | acierto |           15 | conteo_color |            2 |    2 |         -1 |               0 |                        29.23 |                     10.81 |                      0.83 |                         98.5 |                               0   |                         5.76 |                      2.93 |                      0.97 |                         98.2 |                              55.4 |           0.2  |       -0.05 |          -0 |
| q039  | acierto |           25 | conteo_color |            6 |    6 |         -2 |              -1 |                         0.11 |                      0.07 |                      1.02 |                          0   |                               0   |                         0.23 |                      0.39 |                      1.02 |                         17.6 |                               0   |           0.03 |       -0.01 |          -0 |
| q031  | cercano |           25 | conteo_forma |            2 |    3 |         -1 |               0 |                         7.16 |                      3.31 |                      0.94 |                         98.1 |                              95.9 |                         8.02 |                      2.98 |                      0.94 |                         97.4 |                              89.7 |           0.12 |       -0.01 |           0 |
| q038  | cercano |           25 | conteo_color |            2 |    4 |         -1 |               0 |                         0    |                     23.47 |                      0.62 |                          0   |                              99.9 |                         1.71 |                      3.57 |                      0.95 |                          0   |                              96.6 |           0.02 |       -0.01 |          -0 |
| q029  | cercano |           25 | conteo_forma |            2 |    2 |         -1 |               0 |                         0    |                      0    |                      1.02 |                          0   |                               0   |                         0    |                      0.01 |                      1.02 |                          0   |                               0   |          -0.13 |       -0.01 |          -0 |
| q062  | cercano |           35 | conteo_color |            4 |    5 |          0 |               0 |                         0.48 |                      0.1  |                      1.03 |                          0   |                               0   |                         1.54 |                      0.9  |                      1    |                          0   |                              59.8 |           0.03 |       -0.01 |          -0 |
| q015  | cercano |           15 | conteo_color |            3 |    4 |         -1 |               0 |                         0.9  |                      0.77 |                      1    |                         81.9 |                              27.6 |                         1.12 |                      1.77 |                      0.99 |                         70.5 |                              73.9 |           0.06 |       -0.02 |          -0 |
| q005  | cercano |           15 | conteo_forma |            2 |    3 |          0 |               0 |                         0    |                      0.41 |                      1.01 |                          0   |                               8.1 |                         0.1  |                      0.65 |                      1.01 |                          0   |                               9.9 |          -0.04 |        0    |          -0 |
| q092  | cercano |           45 | conteo_color |            4 |    5 |          0 |              -1 |                         0    |                      0.02 |                      1.04 |                          0   |                               0   |                         0    |                      0.22 |                      1.03 |                          0   |                               0   |           0.02 |       -0    |          -0 |
| q099  | lejano  |           55 | conteo_forma |            4 |    9 |         -1 |               0 |                         0    |                      0.23 |                      1.04 |                          0   |                               0   |                         1.05 |                      0.94 |                      1    |                         66.5 |                              73.9 |           0.03 |       -0    |          -0 |
| q058  | lejano  |           35 | conteo_forma |            4 |    8 |         -1 |              -1 |                         0.04 |                      0.22 |                      1.03 |                          0   |                               0   |                         0.37 |                      1.21 |                      1    |                         76.8 |                               0   |          -0.01 |       -0.01 |          -0 |
| q048  | lejano  |           35 | conteo_forma |            6 |   10 |          0 |               0 |                         0    |                      0.15 |                      1.03 |                          0   |                               0   |                         0.05 |                      0.3  |                      1.02 |                          0   |                               0   |          -0.01 |        0    |          -0 |
| q024  | lejano  |           25 | conteo_forma |            6 |    9 |         -1 |               0 |                         0    |                      0.07 |                      1.02 |                          0   |                              23.5 |                         0.02 |                      0.56 |                      1.01 |                          0   |                              28.4 |          -0.04 |       -0    |          -0 |
| q110  | lejano  |           55 | conteo_color |            6 |    9 |         -3 |               0 |                         0.26 |                      0.34 |                      1.03 |                         30.6 |                              23.3 |                         0.36 |                      0.43 |                      1.03 |                         23.6 |                              18.7 |           0.06 |       -0.01 |          -0 |
| q068  | lejano  |           35 | conteo_color |            2 |    5 |          1 |               0 |                         0    |                      0.09 |                      1.03 |                          0   |                              80   |                         0.79 |                      1.01 |                      1    |                          0   |                              86   |           0.01 |       -0    |          -0 |