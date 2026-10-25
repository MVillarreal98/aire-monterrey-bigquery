"""
Runner de queries: ejecuta los SQL de sql/ contra la tabla de BigQuery
y guarda cada resultado como CSV en outputs/.

Uso:
    .venv/Scripts/python src/analysis/run_queries.py [archivos...]

Sin argumentos corre los cuatro archivos de negocio (02-05). Un archivo con
varias queries produce un CSV por query con sufijo a, b, c...
(p. ej. 02_tendencia_anuala.csv).
Proyecto de GCP: variable de entorno AIRE_GCP_PROJECT (por defecto
aire-monterrey-bq). Los SQL nombran la tabla como
`aire-monterrey-bq.sima.sima_horarios` y aquí se sustituye el proyecto.
Requiere: gcloud auth application-default login (ver docs/gcp_setup.md).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from google.cloud import bigquery

REPO = Path(__file__).resolve().parents[2]
SQL_DIR = REPO / "sql"
OUT_DIR = REPO / "outputs"

DEFAULT_FILES = [
    "02_tendencia_anual.sql",
    "03_ranking_estaciones.sql",
    "04_contingencias.sql",
    "05_patron_horario.sql",
]

PROJECT = os.environ.get("AIRE_GCP_PROJECT", "aire-monterrey-bq")
# acepta también 'aire-mty', el nombre que usaban versiones anteriores de los SQL
TABLE_RE = re.compile(r"(?:aire-monterrey-bq|aire-mty)\.sima\.sima_horarios")


def strip_comments(sql: str) -> str:
    # quita las líneas que empiezan con '--' en la columna 0. Los comentarios al
    # final de una línea se quedan (BigQuery los acepta), así que no deben
    # contener ';', porque split_statements corta por ';'.
    return re.sub(r"(?m)^--.*\n?", "", sql)


def split_statements(sql: str) -> list[str]:
    parts = [p.strip() for p in sql.split(";") if p.strip()]
    return parts


def run() -> None:
    files = sys.argv[1:] or DEFAULT_FILES
    client = bigquery.Client(project=PROJECT)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for name in files:
        sql = (SQL_DIR / name).read_text(encoding="utf-8")
        sql = TABLE_RE.sub(f"{PROJECT}.sima.sima_horarios", sql)
        sql = strip_comments(sql)
        statements = split_statements(sql)
        tag = name.replace(".sql", "")
        for i, stmt in enumerate(statements):
            suffix = "" if len(statements) == 1 else chr(ord("A") + i)
            dest = OUT_DIR / f"{tag}{suffix.lower()}.csv"
            df = client.query(stmt).result().to_dataframe()
            df.to_csv(dest, index=False)
            print(f"[OK] {dest.name}: {len(df)} filas")
            print(df.head(3).to_string(index=False))


if __name__ == "__main__":
    run()
