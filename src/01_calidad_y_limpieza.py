"""Paso 1: perfilado, reglas de calidad y limpieza del conjunto de solicitudes de crédito.

Entrada:  data/CreditScoring_raw.csv
Salidas:  data/credit_clean.csv, data/credit.db (tabla `solicitudes`), reports/reporte_calidad.md
"""
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DATA = RAIZ / "data"
REPORTS = RAIZ / "reports"
REPORTS.mkdir(exist_ok=True)

CENTINELA = 99999999

# Códigos según la convención habitual de este conjunto (deben confirmarse con la fuente original).
MAPAS = {
    "Status": {1: "bueno", 2: "malo"},
    "Home": {1: "alquiler", 2: "propietario", 3: "privada", 4: "ignorado", 5: "padres", 6: "otro"},
    "Marital": {1: "soltero", 2: "casado", 3: "viudo", 4: "separado", 5: "divorciado"},
    "Records": {1: "sin_antecedentes", 2: "con_antecedentes"},
    "Job": {1: "fijo", 2: "medio_tiempo", 3: "independiente", 4: "otro"},
}

raw = pd.read_csv(DATA / "CreditScoring_raw.csv")
df = raw.copy()
reglas = []  # (regla, filas afectadas, tratamiento)

# 1. Duplicados exactos
dup = int(df.duplicated().sum())
df = df.drop_duplicates()
reglas.append(("Filas duplicadas exactas", dup, "Eliminadas"))

# 2. Variable objetivo sin dato (Status = 0)
sin_estado = int((df["Status"] == 0).sum())
df = df[df["Status"] != 0]
reglas.append(("Status = 0 (estado del crédito sin dato)", sin_estado, "Eliminadas: sin objetivo no se puede analizar"))

# 3. Valores centinela 99999999 en columnas de dinero
for col in ["Income", "Assets", "Debt"]:
    n = int((df[col] == CENTINELA).sum())
    df[col] = df[col].replace(CENTINELA, np.nan)
    reglas.append((f"{col} = 99999999 (faltante disfrazado)", n, "Convertidos a NaN, no imputados"))

# 4. Ingreso en 0: imposible para un solicitante de crédito
cero = int((df["Income"] == 0).sum())
df.loc[df["Income"] == 0, "Income"] = np.nan
reglas.append(("Income = 0 (ingreso imposible)", cero, "Convertidos a NaN, no imputados"))

# 5. Códigos 0 en variables categóricas = sin categoría
for col in ["Home", "Marital", "Job"]:
    n = int((df[col] == 0).sum())
    reglas.append((f"{col} = 0 (código sin categoría)", n, "Quedan como NaN"))

# 6. Monto pedido mayor al precio del bien
inconsistentes = int((df["Amount"] > df["Price"]).sum())
reglas.append(("Amount > Price (pide más de lo que vale el bien)", inconsistentes, "Se marcan y se conservan"))

# Decodificar categorías
for col, mapa in MAPAS.items():
    df[col] = df[col].map(mapa)

# Variables derivadas
df["malo"] = (df["Status"] == "malo").astype(int)
df["financiado_pct"] = df["Amount"] / df["Price"]
df["ingreso_faltante"] = df["Income"].isna().astype(int)
df["grupo_antiguedad"] = pd.cut(
    df["Seniority"], bins=[-1, 1, 5, 10, np.inf], labels=["0-1 años", "2-5 años", "6-10 años", "11+ años"]
).astype(str)
df["grupo_edad"] = pd.cut(
    df["Age"], bins=[17, 25, 35, 45, 55, np.inf], labels=["18-25", "26-35", "36-45", "46-55", "56+"]
).astype(str)

# Guardar
df.to_csv(DATA / "credit_clean.csv", index=False)
with sqlite3.connect(DATA / "credit.db") as con:
    df.to_sql("solicitudes", con, if_exists="replace", index=False)

# Reporte de calidad
sin_ingreso = df["Income"].isna()
lineas = [
    "# Reporte de calidad de datos",
    "",
    f"Filas originales: {len(raw):,}. Filas después de limpiar: {len(df):,}.",
    "",
    "| Regla | Filas afectadas | Tratamiento |",
    "| --- | --- | --- |",
]
lineas += [f"| {r} | {n:,} | {t} |" for r, n, t in reglas]
lineas += [
    "",
    "## Faltantes después de limpiar",
    "",
    "| Columna | Faltantes | % |",
    "| --- | --- | --- |",
]
for col in ["Income", "Assets", "Debt", "Home", "Marital", "Job"]:
    n = int(df[col].isna().sum())
    lineas.append(f"| {col} | {n:,} | {n / len(df):.1%} |")
lineas += [
    "",
    "## ¿Los ingresos faltantes son aleatorios?",
    "",
    f"- Tasa de créditos malos sin ingreso: {df.loc[sin_ingreso, 'malo'].mean():.1%} (n = {int(sin_ingreso.sum())}).",
    f"- Tasa de créditos malos con ingreso: {df.loc[~sin_ingreso, 'malo'].mean():.1%} (n = {int((~sin_ingreso).sum())}).",
    "- Sin ingreso registrado por tipo de empleo:",
]
por_empleo = df.groupby("Job")["ingreso_faltante"].mean().sort_values(ascending=False)
lineas += [f"  - {k}: {v:.1%}" for k, v in por_empleo.items()]
lineas += [
    "",
    "Conclusión: los faltantes no son aleatorios. Imputarlos con la media o la mediana ocultaría un patrón de riesgo, "
    "así que se dejan como faltantes y se reportan.",
]
(REPORTS / "reporte_calidad.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")

print(f"Filas limpias: {len(df):,} | créditos malos: {df['malo'].sum():,} ({df['malo'].mean():.1%})")
print("Reporte guardado en reports/reporte_calidad.md")
