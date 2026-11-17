"""Paso 2: consultas SQL, pruebas estadísticas y gráficas.

Entrada:  data/credit.db (creada por 01_calidad_y_limpieza.py), sql/consultas.sql
Salidas:  reports/resultados.md, figures/*.png
"""
from pathlib import Path
import re
import sqlite3

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parents[1]
DATA, SQL, REPORTS, FIGURES = (RAIZ / p for p in ("data", "sql", "reports", "figures"))
FIGURES.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

con = sqlite3.connect(DATA / "credit.db")
df = pd.read_sql_query("SELECT * FROM solicitudes", con)


# ---------- 1. Consultas SQL ----------
def cargar_consultas(ruta):
    texto = ruta.read_text(encoding="utf-8")
    bloques = re.split(r"^-- name: (\w+)\s*$", texto, flags=re.M)
    return {bloques[i]: bloques[i + 1].strip() for i in range(1, len(bloques), 2)}


consultas = cargar_consultas(SQL / "consultas.sql")
res = {nombre: pd.read_sql_query(q, con) for nombre, q in consultas.items()}

# ---------- 2. Estadística ----------
def cramers_v(tabla):
    chi2 = stats.chi2_contingency(tabla)[0]
    n = tabla.to_numpy().sum()
    r, k = tabla.shape
    return np.sqrt(chi2 / (n * (min(r, k) - 1)))


df["tramo_financiado"] = pd.cut(
    df["financiado_pct"], [-np.inf, 0.60, 0.80, 0.95, np.inf],
    labels=["<60%", "60-79%", "80-94%", "95%+"], right=False,
)
pruebas = []
for col, nombre in [
    ("grupo_antiguedad", "Antigüedad laboral"),
    ("Records", "Antecedentes"),
    ("Job", "Tipo de empleo"),
    ("tramo_financiado", "Parte del bien financiada"),
    ("Home", "Vivienda"),
]:
    tabla = pd.crosstab(df[col], df["malo"])
    chi2, p, gl, _ = stats.chi2_contingency(tabla)
    pruebas.append({"Variable": nombre, "Chi-cuadrado": round(chi2, 1), "gl": gl,
                    "p": f"{p:.1e}", "V de Cramér": round(cramers_v(tabla), 2)})
pruebas = pd.DataFrame(pruebas).sort_values("V de Cramér", ascending=False)

# Mann-Whitney: ingreso de créditos malos vs buenos (solo con ingreso)
con_ing = df.dropna(subset=["Income"])
mw = stats.mannwhitneyu(con_ing.loc[con_ing.malo == 1, "Income"], con_ing.loc[con_ing.malo == 0, "Income"])
med_malo = con_ing.loc[con_ing.malo == 1, "Income"].median()
med_bueno = con_ing.loc[con_ing.malo == 0, "Income"].median()


# Intervalos de confianza de Wilson (95%) para antecedentes
def wilson(k, n, z=1.96):
    p = k / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margen = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return centro - margen, centro + margen


ic = []
for seg, g in df.groupby("Records"):
    lo, hi = wilson(g.malo.sum(), len(g))
    ic.append({"Segmento": seg, "n": len(g), "Tasa malos": f"{g.malo.mean():.1%}", "IC 95%": f"{lo:.1%} – {hi:.1%}"})
ic = pd.DataFrame(ic)

# Outliers por IQR (se revisan, no se borran)
outliers = []
for col in ["Income", "Amount", "Price"]:
    s = df[col].dropna()
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    fuera = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
    outliers.append({"Columna": col, "Q1": q1, "Q3": q3, "Outliers": int(fuera), "%": f"{fuera / len(s):.1%}"})
outliers = pd.DataFrame(outliers)

# ---------- 3. Gráficas ----------
AZUL, ROJO, GRIS = "#2E5C8A", "#C0392B", "#9AA5B1"
tasa_general = df["malo"].mean() * 100


def barras(serie, titulo, archivo, xlabel):
    fig, ax = plt.subplots(figsize=(7, 4))
    colores = [ROJO if v == serie.max() else AZUL for v in serie.values]
    ax.bar(serie.index.astype(str), serie.values, color=colores)
    ax.axhline(tasa_general, color=GRIS, ls="--", lw=1, label=f"Promedio general: {tasa_general:.1f}%")
    ax.legend(frameon=False, loc="best", fontsize=9)
    for i, v in enumerate(serie.values):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_title(titulo, loc="left", fontsize=12)
    ax.set_ylabel("% de créditos malos")
    ax.set_xlabel(xlabel)
    ax.set_ylim(0, max(serie.max() * 1.2, tasa_general * 1.3))
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / archivo, dpi=150)
    plt.close(fig)


orden_ant = ["0-1 años", "2-5 años", "6-10 años", "11+ años"]
barras(df.groupby("grupo_antiguedad").malo.mean().reindex(orden_ant) * 100,
       "A menos antigüedad laboral, más créditos malos", "riesgo_antiguedad.png", "Antigüedad en el empleo actual")
barras(df.groupby("Job").malo.mean().sort_values(ascending=False) * 100,
       "Medio tiempo casi triplica el riesgo del empleo fijo", "riesgo_empleo.png", "Tipo de empleo")
barras(df.groupby("tramo_financiado", observed=True).malo.mean() * 100,
       "Financiar el 95% o más triplica el riesgo frente a menos del 60%", "riesgo_financiado.png", "Parte del bien financiada")

# Mapa de calor: antecedentes x antigüedad
piv = df.pivot_table(index="Records", columns="grupo_antiguedad", values="malo", aggfunc="mean")[orden_ant] * 100
fig, ax = plt.subplots(figsize=(7, 2.8))
im = ax.imshow(piv.values, cmap="Reds", vmin=0, vmax=100)
ax.set_xticks(range(len(orden_ant)), orden_ant)
ax.set_yticks(range(len(piv.index)), piv.index)
for i in range(piv.shape[0]):
    for j in range(piv.shape[1]):
        v = piv.values[i, j]
        ax.text(j, i, f"{v:.1f}%", ha="center", va="center", color="white" if v > 50 else "black", fontsize=10)
ax.set_title("Los factores se acumulan: % de créditos malos", loc="left", fontsize=12)
fig.tight_layout()
fig.savefig(FIGURES / "riesgo_combinado.png", dpi=150)
plt.close(fig)


# ---------- 4. Reporte ----------
def md(tabla):
    return tabla.to_markdown(index=False)


partes = ["# Resultados del análisis", ""]
titulos = {
    "q1_tasa_general": "Tasa general de créditos malos",
    "q2_ranking_segmentos": "Ranking de riesgo por segmento",
    "q3_cuartil_ingreso": "Riesgo por cuartil de ingreso",
    "q4_tramo_financiado": "Riesgo por parte del bien financiada",
    "q5_antecedentes_x_antiguedad": "Antecedentes x antigüedad laboral",
    "q6_financiado_x_antiguedad": "Parte financiada x antigüedad laboral",
    "q7_faltantes": "Faltantes por columna",
}
for nombre, tabla in res.items():
    partes += [f"## {titulos.get(nombre, nombre)} (`{nombre}`)", "", md(tabla), ""]
partes += ["## Pruebas chi-cuadrado y V de Cramér", "", md(pruebas), ""]
partes += ["## Intervalos de confianza de Wilson (95%)", "", md(ic), ""]
partes += [
    "## Ingreso: Mann-Whitney",
    "",
    f"Mediana de ingreso con crédito malo: {med_malo:.0f}; con crédito bueno: {med_bueno:.0f}. "
    f"U = {mw.statistic:,.0f}, p = {mw.pvalue:.1e}.",
    "",
    "## Outliers por IQR (revisados, no eliminados)",
    "",
    md(outliers),
    "",
]
(REPORTS / "resultados.md").write_text("\n".join(partes), encoding="utf-8")
print("Resultados en reports/resultados.md y gráficas en figures/")
