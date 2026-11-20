# Verificación de las cifras estadísticas de la memoria

CAPTURe: corrida original · explicabilidad: resultados/*

Resumen: OK 200 · INFO 42 · REDONDEO 10 · IC-BOOT 5

## 2.6.2

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Ejemplo ec. (2.5): (61·23,8 + 39·100)/100 | 53.5 | 53.5 | OK |

## 2.7.1

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Wilson con k = 0, n = 25 | 0.0; 13.3 | 0.0; 13.3 | OK |
| Semiancho de Wald, n = 100, p = 0,27 (puntos) | 8.7 | 8.7 | OK |
| Semiancho de Wald, n = 100, p = 0,5 (puntos) | 9.8 | 9.8 | OK |

## 4.1

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| InternVL2-1B: respuestas válidas (real; sint.) | 100; 97 | 100; 97 | OK |
| moondream2: respuestas válidas (real; sint.) | 95; 61 | 95; 61 | OK |
| PaliGemma2-3B: respuestas válidas (real; sint.) | 61; 31 | 61; 31 | OK |
| Qwen2-VL-2B: respuestas válidas (real; sint.) | 100; 99 | 100; 99 | OK |
| PaliGemma2-3B: parse_fail de 200 (texto: 108, 54 %) | 108 | 108 | OK |
| Tabla 4 · InternVL2-1B · real · solo válidas · sMAPE | 65.0 | 65.0 | OK |
| Tabla 4 · InternVL2-1B · real · solo válidas · IC 95 % | 58.3; 71.3 | 58.3; 71.3 | OK |
| Tabla 4 · InternVL2-1B · real · inválidas = 100 % · sMAPE | 65.0 | 65.0 | OK |
| Tabla 4 · InternVL2-1B · real · inválidas = 100 % · IC 95 % | 58.4; 71.2 | 58.3; 71.3 | REDONDEO |
| Tabla 4 · InternVL2-1B · sintetico · solo válidas · sMAPE | 65.7 | 65.7 | OK |
| Tabla 4 · InternVL2-1B · sintetico · solo válidas · IC 95 % | 61.2; 70.1 | 61.2; 70.0 | REDONDEO |
| Tabla 4 · InternVL2-1B · sintetico · inválidas = 100 % · sMAPE | 66.8 | 66.8 | OK |
| Tabla 4 · InternVL2-1B · sintetico · inválidas = 100 % · IC 95 % | 62.3; 71.0 | 62.2; 71.1 | REDONDEO |
| Tabla 4 · moondream2 · real · solo válidas · sMAPE | 38.9 | 38.9 | OK |
| Tabla 4 · moondream2 · real · solo válidas · IC 95 % | 33.3; 44.8 | 33.1; 44.8 | IC-BOOT |
| Tabla 4 · moondream2 · real · inválidas = 100 % · sMAPE | 41.9 | 41.9 | OK |
| Tabla 4 · moondream2 · real · inválidas = 100 % · IC 95 % | 35.9; 47.9 | 35.7; 48.0 | IC-BOOT |
| Tabla 4 · moondream2 · sintetico · solo válidas · sMAPE | 23.8 | 23.8 | OK |
| Tabla 4 · moondream2 · sintetico · solo válidas · IC 95 % | 17.7; 30.4 | 17.6; 30.3 | REDONDEO |
| Tabla 4 · moondream2 · sintetico · inválidas = 100 % · sMAPE | 53.5 | 53.5 | OK |
| Tabla 4 · moondream2 · sintetico · inválidas = 100 % · IC 95 % | 45.3; 61.8 | 45.2; 61.7 | REDONDEO |
| Tabla 4 · PaliGemma2-3B · real · solo válidas · sMAPE | 43.6 | 43.6 | OK |
| Tabla 4 · PaliGemma2-3B · real · solo válidas · IC 95 % | 36.5; 50.9 | 36.4; 50.9 | REDONDEO |
| Tabla 4 · PaliGemma2-3B · real · inválidas = 100 % · sMAPE | 65.6 | 65.6 | OK |
| Tabla 4 · PaliGemma2-3B · real · inválidas = 100 % · IC 95 % | 58.5; 72.5 | 58.4; 72.3 | IC-BOOT |
| Tabla 4 · PaliGemma2-3B · sintetico · solo válidas · sMAPE | 46.1 | 46.1 | OK |
| Tabla 4 · PaliGemma2-3B · sintetico · solo válidas · IC 95 % | 35.6; 57.0 | 35.2; 56.3 | IC-BOOT |
| Tabla 4 · PaliGemma2-3B · sintetico · inválidas = 100 % · sMAPE | 83.3 | 83.3 | OK |
| Tabla 4 · PaliGemma2-3B · sintetico · inválidas = 100 % · IC 95 % | 77.3; 89.0 | 77.3; 89.1 | REDONDEO |
| Tabla 4 · Qwen2-VL-2B · real · solo válidas · sMAPE | 37.3 | 37.3 | OK |
| Tabla 4 · Qwen2-VL-2B · real · solo válidas · IC 95 % | 32.0; 42.8 | 32.1; 42.7 | REDONDEO |
| Tabla 4 · Qwen2-VL-2B · real · inválidas = 100 % · sMAPE | 37.3 | 37.3 | OK |
| Tabla 4 · Qwen2-VL-2B · real · inválidas = 100 % · IC 95 % | 32.0; 42.7 | 32.1; 42.7 | REDONDEO |
| Tabla 4 · Qwen2-VL-2B · sintetico · solo válidas · sMAPE | 49.0 | 49.0 | OK |
| Tabla 4 · Qwen2-VL-2B · sintetico · solo válidas · IC 95 % | 42.1; 55.8 | 42.2; 55.7 | REDONDEO |
| Tabla 4 · Qwen2-VL-2B · sintetico · inválidas = 100 % · sMAPE | 49.5 | 49.5 | OK |
| Tabla 4 · Qwen2-VL-2B · sintetico · inválidas = 100 % · IC 95 % | 42.6; 56.5 | 42.3; 56.3 | IC-BOOT |
| Tabla 4 · InternVL2-1B (parser estricto) · real · válidas | 65 | 65 | OK |
| Tabla 4 · InternVL2-1B (parser estricto) · real · solo válidas | 45.4; 38.8; 51.9 | 45.4; 38.8; 51.9 | OK |
| Tabla 4 · InternVL2-1B (parser estricto) · real · inválidas = 100 % | 64.5; 57.9; 71.0 | 64.5; 57.9; 71.0 | OK |
| Tabla 4 · InternVL2-1B (parser estricto) · sintetico · válidas | 27 | 27 | OK |
| Tabla 4 · InternVL2-1B (parser estricto) · sintetico · solo válidas | 25.9; 19.7; 33.1 | 25.9; 19.7; 33.1 | OK |
| Tabla 4 · InternVL2-1B (parser estricto) · sintetico · inválidas = 100 % | 80.0; 73.1; 86.6 | 80.0; 73.1; 86.6 | OK |
| Tabla 4 · moondream2 (parser estricto) · real · válidas | 91 | 91 | OK |
| Tabla 4 · moondream2 (parser estricto) · real · solo válidas | 37.1; 31.5; 42.9 | 37.1; 31.5; 42.9 | OK |
| Tabla 4 · moondream2 (parser estricto) · real · inválidas = 100 % | 42.8; 36.6; 49.2 | 42.8; 36.6; 49.2 | OK |
| Tabla 4 · moondream2 (parser estricto) · sintetico · válidas | 20 | 20 | OK |
| Tabla 4 · moondream2 (parser estricto) · sintetico · solo válidas | 7.9; 4.7; 11.2 | 7.9; 4.7; 11.2 | OK |
| Tabla 4 · moondream2 (parser estricto) · sintetico · inválidas = 100 % | 81.6; 74.3; 88.8 | 81.6; 74.3; 88.8 | OK |
| Tabla 4 · PaliGemma2-3B (parser estricto) · real · válidas | 61 | 61 | OK |
| Tabla 4 · PaliGemma2-3B (parser estricto) · real · solo válidas | 43.6; 36.3; 50.6 | 43.6; 36.3; 50.6 | OK |
| Tabla 4 · PaliGemma2-3B (parser estricto) · real · inválidas = 100 % | 65.6; 58.6; 72.4 | 65.6; 58.6; 72.4 | OK |
| Tabla 4 · PaliGemma2-3B (parser estricto) · sintetico · válidas | 6 | 6 | OK |
| Tabla 4 · PaliGemma2-3B (parser estricto) · sintetico · solo válidas | 12.6; 6.4; 17.8 | 12.6; 6.4; 17.8 | OK |
| Tabla 4 · PaliGemma2-3B (parser estricto) · sintetico · inválidas = 100 % | 94.8; 90.4; 98.4 | 94.8; 90.4; 98.4 | OK |
| Tabla 4 · Qwen2-VL-2B (parser estricto) · real · válidas | 91 | 91 | OK |
| Tabla 4 · Qwen2-VL-2B (parser estricto) · real · solo válidas | 31.6; 27.3; 36.1 | 31.6; 27.3; 36.1 | OK |
| Tabla 4 · Qwen2-VL-2B (parser estricto) · real · inválidas = 100 % | 37.8; 32.2; 43.4 | 37.8; 32.2; 43.4 | OK |
| Tabla 4 · Qwen2-VL-2B (parser estricto) · sintetico · válidas | 35 | 35 | OK |
| Tabla 4 · Qwen2-VL-2B (parser estricto) · sintetico · solo válidas | 15.7; 10.9; 21.3 | 15.7; 10.9; 21.3 | OK |
| Tabla 4 · Qwen2-VL-2B (parser estricto) · sintetico · inválidas = 100 % | 70.5; 62.5; 78.7 | 70.5; 62.5; 78.7 | OK |
| Constante · real · mediana de la muestra | 33 | 33 | OK |
| Tabla 4 · constante (33) · real · col. solo válidas | 37.0; 32.4; 41.5 | 37.0; 32.4; 41.5 | OK |
| Tabla 4 · constante (33) · real · col. inválidas = 100 % | 37.0; 32.6; 41.5 | 37.0; 32.6; 41.5 | OK |
| Constante · sintetico · mediana de la muestra | 10 | 10 | OK |
| Tabla 4 · constante (10) · sintetico · col. solo válidas | 13.7; 11.9; 15.4 | 13.7; 11.9; 15.4 | OK |
| Tabla 4 · constante (10) · sintetico · col. inválidas = 100 % | 13.7; 11.8; 15.4 | 13.7; 11.8; 15.4 | OK |
| InternVL2-1B: filas con predicción = 1 (de 200) | 104 | 104 | OK |
| InternVL2-1B: predicción = 1 (real; sint.) | 45; 59 | 45; 59 | OK |
| InternVL2-1B: de esas, con respuesta correcta = 1 | 0 | 0 | OK |
| Qwen2-VL-2B: filas con predicción = 1 (de 200) | 55 | 55 | OK |
| Qwen2-VL-2B: de esas, con respuesta correcta = 1 | 0 | 0 | OK |
| InternVL2-1B: aciertos por grupo, sobre todas (Chico; Mediano; Grande; Masivo) | — | 4/25; 0/27; 0/23; 0/25 | INFO |
| moondream2: aciertos por grupo, sobre todas (Chico; Mediano; Grande; Masivo) | — | 5/25; 0/27; 0/23; 0/25 | INFO |
| PaliGemma2-3B: aciertos por grupo, sobre todas (Chico; Mediano; Grande; Masivo) | — | 0/25; 0/27; 0/23; 0/25 | INFO |
| Qwen2-VL-2B: aciertos por grupo, sobre todas (Chico; Mediano; Grande; Masivo) | — | 3/25; 1/27; 0/23; 0/25 | INFO |
| moondream2: acierto en Chico (texto: 20 %, 5 de 25) | 20.0 | 20.0 | OK |
| moondream2: Wilson en Chico | 8.9; 39.1 | 8.9; 39.1 | OK |
| Límite superior de Wilson con 0 aciertos (n = 23; n = 25) | 14.3; 13.3 | 14.3; 13.3 | OK |

## 4.6.2

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Qwen2-VL-2B: predicción = 1 en el subset sintético | 49 | 49 | OK |
| InternVL2-1B: de las 104, cuántas comienzan una lista numerada | 87 | 87 | OK |
| InternVL2-1B · sintético · filas con razonamiento paso a paso (de 400) | 35 | 35 | OK |
| … de ellas en conteo_general | 30 | 30 | OK |
| … con predicción = 1 | 35 | 35 | OK |
| … sin 'there are N' recuperable | 23 | 23 | OK |
| … valores recuperados correctos | 0 | 0 | OK |
| … mínima respuesta correcta en conteo_general afectado (texto: ≥ 15) | 15 | 15 | OK |

## 3.2

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Rango de la respuesta correcta en CAPTURe real | 8; 501 | 8; 501 | OK |
| Valores distintos de la respuesta correcta | 59 | 59 | OK |
| Cuartiles q0,25; q0,50; q0,75 | 17.75; 33.00; 76.50 | 17.75; 33.00; 76.50 | OK |
| Tamaño de los grupos (Chico; Mediano; Grande; Masivo) | 25; 27; 23; 25 | 25; 27; 23; 25 | OK |

## 4.2

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Tabla 5 · InternVL2-1B · simple · n | 179 | 179 | OK |
| Tabla 5 · InternVL2-1B · simple · acierto [Wilson] | 78.8; 72.2; 84.1 | 78.8; 72.2; 84.1 | OK |
| Tabla 5 · InternVL2-1B · simple · RMSE | 0.81 | 0.81 | OK |
| Tabla 5 · InternVL2-1B · compleja · n | 121 | 121 | OK |
| Tabla 5 · InternVL2-1B · compleja · acierto [Wilson] | 63.6; 54.8; 71.7 | 63.6; 54.8; 71.7 | OK |
| Tabla 5 · InternVL2-1B · compleja · RMSE | 0.89 | 0.89 | OK |
| Tabla 5 · moondream2 · simple · n | 179 | 179 | OK |
| Tabla 5 · moondream2 · simple · acierto [Wilson] | 87.7; 82.1; 91.7 | 87.7; 82.1; 91.7 | OK |
| Tabla 5 · moondream2 · simple · RMSE | 0.59 | 0.59 | OK |
| Tabla 5 · moondream2 · compleja · n | 121 | 121 | OK |
| Tabla 5 · moondream2 · compleja · acierto [Wilson] | 74.4; 65.9; 81.3 | 74.4; 65.9; 81.3 | OK |
| Tabla 5 · moondream2 · compleja · RMSE | 0.76 | 0.76 | OK |
| Tabla 5 · PaliGemma2-3B · simple · n | 179 | 179 | OK |
| Tabla 5 · PaliGemma2-3B · simple · acierto [Wilson] | 75.4; 68.6; 81.1 | 75.4; 68.6; 81.1 | OK |
| Tabla 5 · PaliGemma2-3B · simple · RMSE | 1.02 | 1.02 | OK |
| Tabla 5 · PaliGemma2-3B · compleja · n | 121 | 121 | OK |
| Tabla 5 · PaliGemma2-3B · compleja · acierto [Wilson] | 60.3; 51.4; 68.6 | 60.3; 51.4; 68.6 | OK |
| Tabla 5 · PaliGemma2-3B · compleja · RMSE | 29.84 | 29.84 | OK |
| Tabla 5 · Qwen2-VL-2B · simple · n | 179 | 179 | OK |
| Tabla 5 · Qwen2-VL-2B · simple · acierto [Wilson] | 86.0; 80.2; 90.4 | 86.0; 80.2; 90.4 | OK |
| Tabla 5 · Qwen2-VL-2B · simple · RMSE | 0.57 | 0.57 | OK |
| Tabla 5 · Qwen2-VL-2B · compleja · n | 121 | 121 | OK |
| Tabla 5 · Qwen2-VL-2B · compleja · acierto [Wilson] | 74.4; 65.9; 81.3 | 74.4; 65.9; 81.3 | OK |
| Tabla 5 · Qwen2-VL-2B · compleja · RMSE | 0.77 | 0.77 | OK |
| McNemar moondream2 vs Qwen2-VL-2B · simples · (solo moondream2; solo Qwen) | 9; 6 | 9; 6 | OK |
| McNemar moondream2 vs Qwen2-VL-2B · simples · p | 0.61 | 0.61 | OK |
| McNemar moondream2 vs Qwen2-VL-2B · complejas · (solo moondream2; solo Qwen) | 10; 10 | 10; 10 | OK |
| McNemar moondream2 vs Qwen2-VL-2B · complejas · p | 1.00 | 1.00 | OK |
| PaliGemma2-3B · outlier: (respuesta correcta; respuesta) | 2; 330 | 2; 330 | OK |
| PaliGemma2-3B · compleja · MAE con y sin outlier | 3.31; 0.60 | 3.31; 0.60 | OK |
| PaliGemma2-3B · compleja · RMSE sin outlier | 1.17 | 1.17 | OK |
| Cota (2.10): 328/√121 | 29.8 | 29.8 | OK |
| Aporte del outlier al MAE: 328/121 | 2.71 | 2.71 | OK |
| n válidas en compleja (PaliGemma2-3B) | 121 | 121 | OK |
| InternVL2-1B: límites inferiores de Wilson (simple; compleja) vs RCN 71,8 y 56,2 | — | 72.2; 54.8 | INFO |
| moondream2: límites inferiores de Wilson (simple; compleja) vs RCN 71,8 y 56,2 | — | 82.1; 65.9 | INFO |
| PaliGemma2-3B: límites inferiores de Wilson (simple; compleja) vs RCN 71,8 y 56,2 | — | 68.6; 51.4 | INFO |
| Qwen2-VL-2B: límites inferiores de Wilson (simple; compleja) vs RCN 71,8 y 56,2 | — | 80.2; 65.9 | INFO |

## 4.3

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Las 4 corridas usan las mismas 400 preguntas (1 = sí) | 1 | 1 | OK |
| Tabla 6 · Geometric_Reasoning · clase mayoritaria (%) | 27 | 27 | OK |
| Tabla 6 · Geometric_Reasoning · acierto (InternVL; moondream; PaliGemma; Qwen) | 25; 29; 25; 35 | 25; 29; 25; 35 | OK |
| Geometric_Reasoning · InternVL2-1B: 25/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 17.5; 34.3; no supera | INFO |
| Geometric_Reasoning · moondream2: 29/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 21.0; 38.5; no supera | INFO |
| Geometric_Reasoning · PaliGemma2-3B: 25/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 17.5; 34.3; no supera | INFO |
| Geometric_Reasoning · Qwen2-VL-2B: 35/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 26.4; 44.7; no supera | INFO |
| Tabla 6 · Motion_Analysis · clase mayoritaria (%) | 31 | 31 | OK |
| Tabla 6 · Motion_Analysis · acierto (InternVL; moondream; PaliGemma; Qwen) | 30; 33; 45; 43 | 30; 33; 45; 43 | OK |
| Motion_Analysis · InternVL2-1B: 30/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 21.9; 39.6; no supera | INFO |
| Motion_Analysis · moondream2: 33/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 24.6; 42.7; no supera | INFO |
| Motion_Analysis · PaliGemma2-3B: 45/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 35.6; 54.8; SUPERA | INFO |
| Motion_Analysis · Qwen2-VL-2B: 43/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 33.7; 52.8; SUPERA | INFO |
| Tabla 6 · Egocentric · clase mayoritaria (%) | 36 | 36 | OK |
| Tabla 6 · Egocentric · acierto (InternVL; moondream; PaliGemma; Qwen) | 49; 60; 58; 59 | 49; 60; 58; 59 | OK |
| Egocentric · InternVL2-1B: 49/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 39.4; 58.7; SUPERA | INFO |
| Egocentric · moondream2: 60/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 50.2; 69.1; SUPERA | INFO |
| Egocentric · PaliGemma2-3B: 58/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 48.2; 67.2; SUPERA | INFO |
| Egocentric · Qwen2-VL-2B: 59/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 49.2; 68.1; SUPERA | INFO |
| Tabla 6 · Allocentric · clase mayoritaria (%) | 28 | 28 | OK |
| Tabla 6 · Allocentric · acierto (InternVL; moondream; PaliGemma; Qwen) | 37; 27; 41; 36 | 37; 27; 41; 36 | OK |
| Allocentric · InternVL2-1B: 37/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 28.2; 46.8; SUPERA | INFO |
| Allocentric · moondream2: 27/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 19.3; 36.4; no supera | INFO |
| Allocentric · PaliGemma2-3B: 41/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 31.9; 50.8; SUPERA | INFO |
| Allocentric · Qwen2-VL-2B: 36/100, Wilson y criterio 2.7.5 vs mayoritaria | — | 27.3; 45.8; no supera | INFO |
| Tabla 6 · acierto global (InternVL; moondream; PaliGemma; Qwen) | 35.2; 37.2; 42.2; 43.2 | 35.2; 37.2; 42.2; 43.2 | OK |
| Allocentric · PaliGemma2-3B [Wilson] | 41.0; 31.9; 50.8 | 41.0; 31.9; 50.8 | OK |
| Allocentric · moondream2 [Wilson] | 27.0; 19.3; 36.4 | 27.0; 19.3; 36.4 | OK |
| Motion_Analysis · PaliGemma2-3B [Wilson] | 45.0; 35.6; 54.8 | 45.0; 35.6; 54.8 | OK |
| Motion_Analysis · Qwen2-VL-2B [Wilson] | 43.0; 33.7; 52.8 | 43.0; 33.7; 52.8 | OK |
| Geometric_Reasoning · Qwen2-VL-2B [Wilson] | 35.0; 26.4; 44.7 | 35.0; 26.4; 44.7 | OK |
| Geometric · Qwen2-VL-2B · binomial unilateral exacta vs 27 % (p) | 0.048 | 0.048 | OK |
| Allocentric · InternVL2-1B [Wilson] (el texto dice que solo PaliGemma supera) | — | 37.0; 28.2; 46.8 | INFO |
| InternVL2-1B · parse_fail en Motion_Analysis (%) | 23 | 23 | OK |
| Cobertura de la muestra (%): 100/155; 100/346; 100/102; 100/376; 400/1533 | 65; 29; 98; 27; 26 | 65; 29; 98; 27; 26 | OK |

## 5.1

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| InternVL2-1B: % de respuestas 'A' por track (Geo; Mot; Ego; Allo) | — | 73; 68; 70; 60 | INFO |
| moondream2: % de respuestas 'A' por track (Geo; Mot; Ego; Allo) | — | 65; 16; 30; 27 | INFO |
| PaliGemma2-3B: % de respuestas 'A' por track (Geo; Mot; Ego; Allo) | — | 69; 25; 30; 22 | INFO |
| Qwen2-VL-2B: % de respuestas 'A' por track (Geo; Mot; Ego; Allo) | — | 30; 30; 35; 20 | INFO |

## 4.6.1

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| PaliGemma2-3B: responde 100 (n); GT media; GT = 100 | 31.00; 85.97; 5.00 | 31.00; 85.97; 5.00 | OK |
| PaliGemma2-3B: término sMAPE medio (respuestas = 100; resto) | 7.9; 22.5 | 7.9; 22.5 | OK |
| Qwen2-VL-2B: responde 100 (n); GT media; GT = 100 | 36.0; 81.4; 3.0 | 36.0; 81.4; 3.0 | OK |
| Qwen2-VL-2B: término sMAPE medio (respuestas = 100; resto) | 10.7; 6.4 | 10.7; 6.4 | OK |
| Ejemplo: 14/186 (%) | 7.5 | 7.5 | OK |
| conteo_general: rango de la respuesta correcta | 5; 100 | 5; 100 | OK |

## 4.4

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| InternVL2-1B: acierto % (general; forma; color; combinado) | — | 12; 7; 19; 1 | INFO |
| InternVL2-1B: sMAPE % (general; forma; color; combinado) | — | 47; 26; 27; 70 | INFO |
| moondream2: acierto % (general; forma; color; combinado) | — | 5; 11; 24; 15 | INFO |
| moondream2: sMAPE % (general; forma; color; combinado) | — | 45; 35; 23; 50 | INFO |
| PaliGemma2-3B: acierto % (general; forma; color; combinado) | — | 16; 10; 19; 34 | INFO |
| PaliGemma2-3B: sMAPE % (general; forma; color; combinado) | — | 18; 47; 45; 62 | INFO |
| Qwen2-VL-2B: acierto % (general; forma; color; combinado) | — | 21; 17; 28; 23 | INFO |
| Qwen2-VL-2B: sMAPE % (general; forma; color; combinado) | — | 8; 17; 14; 43 | INFO |
| InternVL2-1B: MAE total; sMAPE total; MAE con ≥ 80 figuras; sMAPE con ≥ 80 figuras | — | 12.7; 42.6; 23.8; 44.5 | INFO |
| moondream2: MAE total; sMAPE total; MAE con ≥ 80 figuras; sMAPE con ≥ 80 figuras | — | 12.3; 38.2; 22.9; 44.5 | INFO |
| PaliGemma2-3B: MAE total; sMAPE total; MAE con ≥ 80 figuras; sMAPE con ≥ 80 figuras | — | 7.3; 43.1; 8.9; 48.9 | INFO |
| Qwen2-VL-2B: MAE total; sMAPE total; MAE con ≥ 80 figuras; sMAPE con ≥ 80 figuras | — | 4.3; 20.3; 6.5; 20.2 | INFO |

## 4.5

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Tabla 7 · InternVL2-1B · VRAM pico, GB (mín; máx), 4 corridas | 1.8; 2.3 | 1.8; 2.3 | OK |
| Tabla 7 · InternVL2-1B · latencia CAPTURe (media; ± semiancho) | 3.15; 0.17 | 3.15; 0.17 | OK |
| Tabla 7 · InternVL2-1B · latencia TallyQA (media; ± semiancho) | 3.14; 0.09 | 3.14; 0.09 | OK |
| Tabla 7 · InternVL2-1B · latencia OmniSpatial (media; ± semiancho) | 0.71; 0.04 | 0.71; 0.04 | OK |
| Tabla 7 · InternVL2-1B · latencia sintético (media; ± semiancho) | 1.02; 0.05 | 1.02; 0.05 | OK |
| Tabla 7 · moondream2 · VRAM pico, GB (mín; máx), 4 corridas | 4.9; 5.2 | 4.9; 5.2 | OK |
| Tabla 7 · moondream2 · latencia CAPTURe (media; ± semiancho) | 3.38; 0.29 | 3.38; 0.29 | OK |
| Tabla 7 · moondream2 · latencia TallyQA (media; ± semiancho) | 2.08; 0.08 | 2.08; 0.08 | OK |
| Tabla 7 · moondream2 · latencia OmniSpatial (media; ± semiancho) | 4.94; 0.08 | 4.94; 0.08 | OK |
| Tabla 7 · moondream2 · latencia sintético (media; ± semiancho) | 5.02; 0.02 | 5.02; 0.02 | OK |
| Tabla 7 · PaliGemma2-3B · VRAM pico, GB (mín; máx), 4 corridas | 6.0; 6.0 | 6.0; 6.0 | OK |
| Tabla 7 · PaliGemma2-3B · latencia CAPTURe (media; ± semiancho) | 2.95; 0.06 | 2.95; 0.06 | OK |
| Tabla 7 · PaliGemma2-3B · latencia TallyQA (media; ± semiancho) | 2.72; 0.01 | 2.72; 0.01 | OK |
| Tabla 7 · PaliGemma2-3B · latencia OmniSpatial (media; ± semiancho) | 2.81; 0.01 | 2.81; 0.01 | OK |
| Tabla 7 · PaliGemma2-3B · latencia sintético (media; ± semiancho) | 2.90; 0.02 | 2.90; 0.02 | OK |
| Tabla 7 · Qwen2-VL-2B · VRAM pico, GB (mín; máx), 4 corridas | 4.7; 8.5 | 4.7; 8.5 | OK |
| Tabla 7 · Qwen2-VL-2B · latencia CAPTURe (media; ± semiancho) | 2.18; 0.09 | 2.18; 0.09 | OK |
| Tabla 7 · Qwen2-VL-2B · latencia TallyQA (media; ± semiancho) | 1.36; 0.07 | 1.36; 0.07 | OK |
| Tabla 7 · Qwen2-VL-2B · latencia OmniSpatial (media; ± semiancho) | 2.59; 0.04 | 2.59; 0.04 | OK |
| Tabla 7 · Qwen2-VL-2B · latencia sintético (media; ± semiancho) | 11.22; 0.02 | 11.22; 0.02 | OK |

## 2.6.5

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| InternVL2-1B · timeout en CAPTURe (texto: 0 %) | 0 | 0 | OK |
| InternVL2-1B · timeout en TallyQA (texto: 0 %) | 0 | 0 | OK |
| InternVL2-1B · timeout en OmniSpatial (texto: 0 %) | 0 | 0 | OK |
| InternVL2-1B · timeout en sintético (texto: 0 %) | 0 | 0 | OK |
| moondream2 · timeout en CAPTURe (texto: 0 %) | 0 | 0 | OK |
| moondream2 · timeout en TallyQA (texto: 0 %) | 0 | 0 | OK |
| moondream2 · timeout en OmniSpatial (texto: 0 %) | 0 | 0 | OK |
| moondream2 · timeout en sintético (texto: 0 %) | 0 | 0 | OK |
| PaliGemma2-3B · timeout en CAPTURe (texto: 0 %) | 0 | 0 | OK |
| PaliGemma2-3B · timeout en TallyQA (texto: 0 %) | 0 | 0 | OK |
| PaliGemma2-3B · timeout en OmniSpatial (texto: 0 %) | 0 | 0 | OK |
| PaliGemma2-3B · timeout en sintético (texto: 0 %) | 0 | 0 | OK |
| Qwen2-VL-2B · timeout en CAPTURe (texto: 0 %) | 0 | 0 | OK |
| Qwen2-VL-2B · timeout en TallyQA (texto: 0 %) | 0 | 0 | OK |
| Qwen2-VL-2B · timeout en OmniSpatial (texto: 0 %) | 0 | 0 | OK |
| Qwen2-VL-2B · timeout en sintético (texto: 0 %) | 0 | 0 | OK |

## 4.7.1

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Acierto en c0 [Wilson] (%) | 12.5; 7.7; 19.6 | 12.5; 7.7; 19.6 | OK |
| Cuenta de menos en c0 (%) | 85.8 | 85.8 | OK |
| Error medio en c0 | -2.3 | -2.3 | OK |
| Repertorio de respuestas en c0 | — | 1; 2; 3; 4; 6 | INFO |
| R² lineal y R² contra log(respuesta correcta) | 0.52; 0.50 | 0.52; 0.50 | OK |
| Ec. (3.7) coincide con la pendiente guardada (1 = sí) | 1 | 1 | OK |
| Cambia al borrar 1 objetivo [Wilson] (%) | 42.5; 34.0; 51.4 | 42.5; 34.0; 51.4 | OK |
| Cambia al borrar 1 no objetivo [Wilson] (%) | 10.8; 6.4; 17.7 | 10.8; 6.4; 17.7 | OK |
| McNemar c1 vs control (solo c1; solo control) | 43; 5 | 43; 5 | OK |
| McNemar c1 vs control · p (×10⁻⁸) | 1.4 | 1.4 | OK |
| Categorías: cuenta; dirección correcta; no reacciona; otra | 11; 63; 42; 4 | 11; 63; 42; 4 | OK |

## Tabla 8

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Pendiente β̂1 [IC t] | 0.445; 0.368; 0.523 | 0.445; 0.368; 0.523 | OK |
| Intercepto β̂0 [IC t] | 0.92; 0.43; 1.42 | 0.92; 0.43; 1.42 | OK |
| Pendiente media de la oclusión [IC t] | -0.433; -0.513; -0.354 | -0.433; -0.513; -0.354 | OK |

## 4.7.2

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Puntos totales; % sobre figura objetivo | 790.0; 77.0 | 790.0; 77.0 | OK |
| Figuras objetivo; % encontradas (cobertura) | 701.0; 68.6 | 701.0; 68.6 | OK |
| Conteo por puntos exacto vs respuesta escrita (%) | 27.5; 12.5 | 27.5; 12.5 | OK |
| McNemar puntos vs escrita (solo puntos; solo escrita) y p | 25.000; 7.000; 0.002 | 25.000; 7.000; 0.002 | OK |
| Sin llamadas degeneradas: preguntas; puntos; precisión %; cobertura % | 118.0; 590.0; 81.9; 69.1 | 118.0; 590.0; 81.9; 69.1 | OK |

## 4.7.3

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Masa del rollout en los 8 tokens fijos (%) y 8/729 (%) | 19.4; 1.1 | 19.4; 1.1 | OK |
| Correlación con la imagen gris (con; sin tokens fijos) | 0.997; 0.957 | 0.997; 0.957 | OK |
| Enriquecimiento de las figuras (con; sin tokens fijos) | 1.5; 1.8 | 1.5; 1.8 | OK |
| Imágenes con el mismo top-5 de rollout (de 22) | 22 | 22 | OK |

## 3.4

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Área media del fondo (%) y cota 1/fondo | 97.4; 1.0 | 97.4; 1.0 | OK |
| Área media de las figuras objetivo (%) | 0.38 | 0.38 | OK |

## 4.7.4

| Cifra | Memoria v5 | Calculado | Estado |
|---|---|---|---|
| Grad-CAM: enriquecimiento mediano (objetivo; otras; fondo) | 0.08; 0.23; 1.02 | 0.08; 0.23; 1.02 | OK |
| Grad × entrada: objetivo > otras (de 20) y prueba de signos p | 15.000; 0.041 | 15.000; 0.041 | OK |
| Wilcoxon pareado (p) | 0.070 | 0.070 | OK |
| Percentil de la figura borrada (cambió; no cambió): n y medias | 12; 8; 26; 5 | 12; 8; 26; 5 | OK |
| Medianas del percentil (cambió; no cambió) | 0; 0 | 0; 0 | OK |
| Mann-Whitney (p) | 0.29 | 0.29 | OK |
