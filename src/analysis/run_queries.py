"""
Runner de queries: ejecuta el SQL del repo contra la fila pequeña de BigQuery
y guarda los resultados como CSV en outputs/.

Uso:
    .venv/Scripts/python src/analysis/run_queries.py [archivos...]

Sin argumentos corre los cuatro del negocio (02-05).
Requiere: gcloud auth application-default login (ver docs/gcp_setup.md).
"""

from __future__ import annotations

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

PROJECT = "aire-monterrey-bq"
TABLE_RE = re.compile(r"aire-mty\.sima\.sima_horarios")


def strip_comments(sql: str) -> str:
    # quita líneas de comentario '--'; los SQL del repo no usan '--' dentro de strings
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
