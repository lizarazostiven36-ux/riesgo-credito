# Resultados del análisis

## Tasa general de créditos malos (`q1_tasa_general`)

|   solicitudes |   malos |   pct_malos |
|--------------:|--------:|------------:|
|          4452 |    1253 |        28.1 |

## Ranking de riesgo por segmento (`q2_ranking_segmentos`)

| dimension          | segmento         |    n |   malos |   pct_malos |   ranking_riesgo |
|:-------------------|:-----------------|-----:|--------:|------------:|-----------------:|
| Empleo             | medio_tiempo     |  452 |     271 |        60   |                1 |
| Antecedentes       | con_antecedentes |  773 |     429 |        55.5 |                2 |
| Antigüedad laboral | 0-1 años         | 1045 |     512 |        49   |                3 |
| Vivienda           | otro             |  319 |     146 |        45.8 |                4 |
| Vivienda           | alquiler         |  973 |     388 |        39.9 |                5 |
| Empleo             | otro             |  171 |      68 |        39.8 |                6 |
| Vivienda           | privada          |  246 |      84 |        34.1 |                7 |
| Empleo             | independiente    | 1022 |     332 |        32.5 |                8 |
| Antigüedad laboral | 2-5 años         | 1287 |     407 |        31.6 |                9 |
| Vivienda           | padres           |  783 |     233 |        29.8 |               10 |
| Antecedentes       | sin_antecedentes | 3679 |     824 |        22.4 |               11 |
| Empleo             | fijo             | 2805 |     580 |        20.7 |               12 |
| Antigüedad laboral | 6-10 años        |  796 |     163 |        20.5 |               13 |
| Vivienda           | propietario      | 2105 |     389 |        18.5 |               14 |
| Antigüedad laboral | 11+ años         | 1324 |     171 |        12.9 |               15 |

## Riesgo por cuartil de ingreso (`q3_cuartil_ingreso`)

|   cuartil_ingreso |   ingreso_min |   ingreso_max |    n |   pct_malos |
|------------------:|--------------:|--------------:|-----:|------------:|
|                 1 |             6 |            90 | 1018 |        40.5 |
|                 2 |            90 |           125 | 1018 |        24.7 |
|                 3 |           125 |           170 | 1018 |        19.6 |
|                 4 |           170 |           959 | 1017 |        17   |

## Riesgo por parte del bien financiada (`q4_tramo_financiado`)

| tramo_financiado   |    n |   pct_malos |
|:-------------------|-----:|------------:|
| 1. Menos de 60%    | 1097 |        13.9 |
| 2. 60% a 79%       | 1366 |        25.5 |
| 3. 80% a 94%       | 1450 |        36   |
| 4. 95% o más       |  539 |        42.9 |

## Antecedentes x antigüedad laboral (`q5_antecedentes_x_antiguedad`)

| antecedentes     | grupo_antiguedad   |    n |   pct_malos |
|:-----------------|:-------------------|-----:|------------:|
| con_antecedentes | 0-1 años           |  183 |        80.3 |
| con_antecedentes | 2-5 años           |  236 |        60.6 |
| con_antecedentes | 6-10 años          |  128 |        49.2 |
| sin_antecedentes | 0-1 años           |  862 |        42.3 |
| con_antecedentes | 11+ años           |  226 |        33.6 |
| sin_antecedentes | 2-5 años           | 1051 |        25.1 |
| sin_antecedentes | 6-10 años          |  668 |        15   |
| sin_antecedentes | 11+ años           | 1098 |         8.7 |

## Parte financiada x antigüedad laboral (`q6_financiado_x_antiguedad`)

| tramo_financiado   | grupo_antiguedad   |   n |   pct_malos |
|:-------------------|:-------------------|----:|------------:|
| 3. 95% o más       | 0-1 años           | 144 |        64.6 |
| 3. 95% o más       | 2-5 años           | 150 |        50   |
| 2. 60% a 94%       | 0-1 años           | 706 |        49.9 |
| 3. 95% o más       | 6-10 años          |  94 |        37.2 |
| 1. Menos de 60%    | 0-1 años           | 195 |        34.4 |
| 2. 60% a 94%       | 2-5 años           | 822 |        34.2 |
| 2. 60% a 94%       | 6-10 años          | 491 |        22.8 |
| 3. 95% o más       | 11+ años           | 151 |        18.5 |
| 1. Menos de 60%    | 2-5 años           | 315 |        16.2 |
| 2. 60% a 94%       | 11+ años           | 797 |        15.7 |
| 1. Menos de 60%    | 6-10 años          | 211 |         7.6 |
| 1. Menos de 60%    | 11+ años           | 376 |         4.8 |

## Faltantes por columna (`q7_faltantes`)

|   sin_ingreso |   sin_activos |   sin_deuda |   sin_vivienda |   sin_empleo |
|--------------:|--------------:|------------:|---------------:|-------------:|
|           381 |            47 |          18 |              6 |            2 |

## Pruebas chi-cuadrado y V de Cramér

| Variable                  |   Chi-cuadrado |   gl |       p |   V de Cramér |
|:--------------------------|---------------:|-----:|--------:|--------------:|
| Antigüedad laboral        |          407.3 |    3 | 5.7e-88 |          0.3  |
| Antecedentes              |          344.4 |    1 | 6.9e-77 |          0.28 |
| Tipo de empleo            |          324.7 |    3 | 4.5e-70 |          0.27 |
| Parte del bien financiada |          217.5 |    3 | 7e-47   |          0.22 |
| Vivienda                  |          220.9 |    5 | 9.6e-46 |          0.22 |

## Intervalos de confianza de Wilson (95%)

| Segmento         |    n | Tasa malos   | IC 95%        |
|:-----------------|-----:|:-------------|:--------------|
| con_antecedentes |  773 | 55.5%        | 52.0% – 59.0% |
| sin_antecedentes | 3679 | 22.4%        | 21.1% – 23.8% |

## Ingreso: Mann-Whitney

Mediana de ingreso con crédito malo: 100; con crédito bueno: 130. U = 1,146,299, p = 7.5e-39.

## Outliers por IQR (revisados, no eliminados)

| Columna   |   Q1 |   Q3 |   Outliers | %    |
|:----------|-----:|-----:|-----------:|:-----|
| Income    |   90 |  170 |        207 | 5.1% |
| Amount    |  700 | 1300 |         72 | 1.6% |
| Price     | 1117 | 1692 |        173 | 3.9% |
