-- Consultas del proyecto de riesgo de crédito (SQLite, tabla `solicitudes`).
-- malo = 1 cuando el crédito terminó en estado "malo" (incumplimiento).
-- Cada consulta empieza con "-- name:" para que src/02_analisis.py la pueda ejecutar.

-- name: q1_tasa_general
SELECT COUNT(*)                     AS solicitudes,
       SUM(malo)                    AS malos,
       ROUND(100.0 * AVG(malo), 1)  AS pct_malos
FROM solicitudes;

-- name: q2_ranking_segmentos
-- Tasa de créditos malos por segmento, con ranking de riesgo (CTE + UNION ALL + RANK).
WITH segmentos AS (
    SELECT 'Antecedentes' AS dimension, Records AS segmento, malo FROM solicitudes
    UNION ALL
    SELECT 'Vivienda', Home, malo FROM solicitudes WHERE Home IS NOT NULL
    UNION ALL
    SELECT 'Empleo', Job, malo FROM solicitudes WHERE Job IS NOT NULL
    UNION ALL
    SELECT 'Antigüedad laboral', grupo_antiguedad, malo FROM solicitudes
),
resumen AS (
    SELECT dimension,
           segmento,
           COUNT(*)                    AS n,
           SUM(malo)                   AS malos,
           ROUND(100.0 * AVG(malo), 1) AS pct_malos
    FROM segmentos
    GROUP BY dimension, segmento
    HAVING COUNT(*) >= 50
)
SELECT dimension, segmento, n, malos, pct_malos,
       RANK() OVER (ORDER BY pct_malos DESC) AS ranking_riesgo
FROM resumen
ORDER BY ranking_riesgo;

-- name: q3_cuartil_ingreso
-- Riesgo por cuartil de ingreso, solo filas con ingreso válido (NTILE).
WITH con_ingreso AS (
    SELECT *, NTILE(4) OVER (ORDER BY Income) AS cuartil_ingreso
    FROM solicitudes
    WHERE Income IS NOT NULL
)
SELECT cuartil_ingreso,
       MIN(Income)                 AS ingreso_min,
       MAX(Income)                 AS ingreso_max,
       COUNT(*)                    AS n,
       ROUND(100.0 * AVG(malo), 1) AS pct_malos
FROM con_ingreso
GROUP BY cuartil_ingreso
ORDER BY cuartil_ingreso;

-- name: q4_tramo_financiado
-- Riesgo según qué parte del bien se financia (monto / precio).
SELECT CASE
         WHEN financiado_pct < 0.60 THEN '1. Menos de 60%'
         WHEN financiado_pct < 0.80 THEN '2. 60% a 79%'
         WHEN financiado_pct < 0.95 THEN '3. 80% a 94%'
         ELSE '4. 95% o más'
       END                         AS tramo_financiado,
       COUNT(*)                    AS n,
       ROUND(100.0 * AVG(malo), 1) AS pct_malos
FROM solicitudes
GROUP BY tramo_financiado
ORDER BY tramo_financiado;

-- name: q5_antecedentes_x_antiguedad
-- ¿Se acumulan los factores de riesgo?
SELECT Records                     AS antecedentes,
       grupo_antiguedad,
       COUNT(*)                    AS n,
       ROUND(100.0 * AVG(malo), 1) AS pct_malos
FROM solicitudes
GROUP BY Records, grupo_antiguedad
HAVING COUNT(*) >= 30
ORDER BY pct_malos DESC;

-- name: q6_financiado_x_antiguedad
SELECT CASE
         WHEN financiado_pct < 0.60 THEN '1. Menos de 60%'
         WHEN financiado_pct < 0.95 THEN '2. 60% a 94%'
         ELSE '3. 95% o más'
       END                         AS tramo_financiado,
       grupo_antiguedad,
       COUNT(*)                    AS n,
       ROUND(100.0 * AVG(malo), 1) AS pct_malos
FROM solicitudes
GROUP BY tramo_financiado, grupo_antiguedad
HAVING COUNT(*) >= 30
ORDER BY pct_malos DESC;

-- name: q7_faltantes
-- Control de calidad: faltantes por columna.
SELECT SUM(Income IS NULL) AS sin_ingreso,
       SUM(Assets IS NULL) AS sin_activos,
       SUM(Debt IS NULL)   AS sin_deuda,
       SUM(Home IS NULL)   AS sin_vivienda,
       SUM(Job IS NULL)    AS sin_empleo
FROM solicitudes;
