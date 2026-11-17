# Reporte de calidad de datos

Filas originales: 4,455. Filas después de limpiar: 4,452.

| Regla | Filas afectadas | Tratamiento |
| --- | --- | --- |
| Filas duplicadas exactas | 2 | Eliminadas |
| Status = 0 (estado del crédito sin dato) | 1 | Eliminadas: sin objetivo no se puede analizar |
| Income = 99999999 (faltante disfrazado) | 34 | Convertidos a NaN, no imputados |
| Assets = 99999999 (faltante disfrazado) | 47 | Convertidos a NaN, no imputados |
| Debt = 99999999 (faltante disfrazado) | 18 | Convertidos a NaN, no imputados |
| Income = 0 (ingreso imposible) | 347 | Convertidos a NaN, no imputados |
| Home = 0 (código sin categoría) | 6 | Quedan como NaN |
| Marital = 0 (código sin categoría) | 1 | Quedan como NaN |
| Job = 0 (código sin categoría) | 2 | Quedan como NaN |
| Amount > Price (pide más de lo que vale el bien) | 0 | Se marcan y se conservan |

## Faltantes después de limpiar

| Columna | Faltantes | % |
| --- | --- | --- |
| Income | 381 | 8.6% |
| Assets | 47 | 1.1% |
| Debt | 18 | 0.4% |
| Home | 6 | 0.1% |
| Marital | 1 | 0.0% |
| Job | 2 | 0.0% |

## ¿Los ingresos faltantes son aleatorios?

- Tasa de créditos malos sin ingreso: 57.0% (n = 381).
- Tasa de créditos malos con ingreso: 25.4% (n = 4071).
- Sin ingreso registrado por tipo de empleo:
  - independiente: 29.7%
  - otro: 12.9%
  - medio_tiempo: 4.0%
  - fijo: 1.2%

Conclusión: los faltantes no son aleatorios. Imputarlos con la media o la mediana ocultaría un patrón de riesgo, así que se dejan como faltantes y se reportan.
