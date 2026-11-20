# Attention rollout del encoder visual de moondream2: resultados

20 imágenes de la muestra + 2 controles (gris, ruido). Verificación de la reimplementación: diferencia máxima 0, coseno mínimo 0,9999996.

## Tokens sumidero

- Top-5 del rollout en la imagen gris: 161 (fila 5, col 26); 135 (fila 5, col 0); 721 (fila 26, col 19); 188 (fila 6, col 26); 23 (fila 0, col 23)
- Top-4 de norma en la imagen gris: 513 (fila 19, col 0); 540 (fila 20, col 0); 23 (fila 0, col 23); 22 (fila 0, col 22)
- Masa del rollout en esos 8 tokens (1.1 % de los tokens): media 17.6 % en la muestra; 23.8 % en gris; 18.2 % en ruido
- Correlación de cada mapa con el de la imagen gris: media 0.996 (mín 0.991)
- La misma correlación quitando los sumideros: media 0.946 (mín 0.931)

## ¿El mapa distingue las figuras? (enriquecimiento; 1 = igual que el fondo)

- Todas las figuras: 1.25 (sin sumideros 1.46)
- Figuras objetivo: 1.42 (sin sumideros 1.57)
- Área media cubierta: figuras 10.4 %, objetivo 1.7 %

Por grupo:

| grupo   |   enriq_figuras |   enriq_objetivo |   enriq_figuras_sin_sinks |   enriq_objetivo_sin_sinks |   corr_con_gris |
|:--------|----------------:|-----------------:|--------------------------:|---------------------------:|----------------:|
| acierto |           1.308 |            1.208 |                     1.562 |                      1.463 |           0.996 |
| cercano |           1.27  |            1.7   |                     1.473 |                      1.747 |           0.995 |
| lejano  |           1.161 |            1.345 |                     1.335 |                      1.474 |           0.996 |

Por imagen:

| qid   | grupo   |   num_shapes | tipo         |   masa_en_sinks_pct |   corr_con_gris |   corr_con_gris_sin_sinks |   enriq_figuras |   enriq_objetivo |   enriq_figuras_sin_sinks |   enriq_objetivo_sin_sinks |   area_figuras_pct |   area_objetivo_pct |
|:------|:--------|-------------:|:-------------|--------------------:|----------------:|--------------------------:|----------------:|-----------------:|--------------------------:|---------------------------:|-------------------:|--------------------:|
| q040  | acierto |           25 | conteo_color |               17.76 |          0.9951 |                    0.9312 |           1.451 |            1.234 |                     1.634 |                      1.484 |               8.08 |                0.71 |
| q022  | acierto |           15 | conteo_color |               19.15 |          0.9965 |                    0.9467 |           1.339 |            1.173 |                     1.638 |                      1.435 |               5.01 |                1.1  |
| q018  | acierto |           15 | conteo_color |               19.32 |          0.9959 |                    0.9391 |           1.504 |            1.226 |                     1.815 |                      1.503 |               4.99 |                0.72 |
| q007  | acierto |           15 | conteo_forma |               18.88 |          0.9962 |                    0.9493 |           1.504 |            1.334 |                     1.817 |                      1.626 |               5.41 |                0.48 |
| q108  | acierto |           55 | conteo_color |               15.86 |          0.9962 |                    0.9456 |           0.996 |            1.015 |                     1.171 |                      1.193 |              18.22 |                2.44 |
| q016  | acierto |           15 | conteo_color |               19.39 |          0.9959 |                    0.9358 |           1.382 |            1.48  |                     1.699 |                      1.816 |               5.66 |                0.72 |
| q074  | acierto |           45 | conteo_forma |               16.69 |          0.997  |                    0.9577 |           0.979 |            0.997 |                     1.162 |                      1.183 |              15.97 |                0.72 |
| q054  | cercano |           35 | conteo_forma |               16.96 |          0.9962 |                    0.9465 |           1.227 |            2.155 |                     1.456 |                      2.567 |              11.82 |                1.2  |
| q010  | cercano |           15 | conteo_forma |               18.97 |          0.9961 |                    0.9391 |           1.386 |            1.491 |                     1.691 |                      1.82  |               5.13 |                0.72 |
| q085  | cercano |           45 | conteo_color |               15.94 |          0.9909 |                    0.9423 |           1.357 |            3.39  |                     1.275 |                      1.967 |              14.63 |                2.28 |
| q017  | cercano |           15 | conteo_color |               19.02 |          0.9957 |                    0.9347 |           1.488 |            1.742 |                     1.817 |                      2.127 |               5.14 |                0.86 |
| q011  | cercano |           15 | conteo_forma |               19    |          0.9963 |                    0.9427 |           1.346 |            1.299 |                     1.643 |                      1.587 |               5.26 |                0.96 |
| q093  | cercano |           45 | conteo_color |               16.64 |          0.9965 |                    0.9627 |           1.057 |            0.911 |                     1.206 |                      1.081 |              14.96 |                2.2  |
| q089  | cercano |           45 | conteo_color |               16.57 |          0.9967 |                    0.9535 |           1.032 |            0.914 |                     1.223 |                      1.083 |              15.49 |                2.21 |
| q113  | lejano  |           55 | conteo_color |               16.21 |          0.9963 |                    0.9452 |           0.989 |            1.212 |                     1.166 |                      1.43  |              16.96 |                2.82 |
| q078  | lejano  |           45 | conteo_forma |               16.43 |          0.9973 |                    0.9613 |           1.01  |            1.174 |                     1.193 |                      1.389 |              14.21 |                2.12 |
| q056  | lejano  |           35 | conteo_forma |               17.24 |          0.9962 |                    0.9423 |           1.096 |            1.35  |                     1.31  |                      1.613 |              11.32 |                2.53 |
| q029  | lejano  |           25 | conteo_forma |               18.07 |          0.9964 |                    0.9521 |           1.302 |            0.948 |                     1.517 |                      1.144 |               8.11 |                2.88 |
| q028  | lejano  |           25 | conteo_forma |               18.02 |          0.9954 |                    0.9435 |           1.52  |            2.359 |                     1.582 |                      2.053 |               8.47 |                2.62 |
| q079  | lejano  |           45 | conteo_forma |               16.59 |          0.9965 |                    0.9505 |           1.05  |            1.025 |                     1.244 |                      1.216 |              13.39 |                3.29 |