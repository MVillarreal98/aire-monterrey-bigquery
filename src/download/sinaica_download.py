"""
Descarga de datos horarios VALIDADOS de la red Monterrey (SIMA/INECC) vía la API SINAICA.

API documentada en docs/sinaica_api.md.
Descarga por estación × contaminante × mes → data/raw/ (JSONL gz).
No es reanudable (el append acumula): si se re-ejecuta, build_parquet.py
elimina los duplicados con drop_duplicates (transformación idempotente).

Uso:
    python src/download/sinaica_download.py
    python src/download/sinaica_download.py --estados 148 --params O3 --year-start 2020
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

BASE = "https://sinaica.inecc.gob.mx/lib/libd/cnxn.php"
REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
STATIONS_CSV = REPO / "docs" / "stations.csv"

# Parámetros objetivo del proyecto (O3 en ppm, PM2.5 en µg/m3)
DEFAULT_PARAMS = ["O3", "PM2.5"]
YEAR_START, YEAR_END = 2015, 2024
SLEEP_SECONDS = 1.1  # respeto al servidor: 1 hilo, delay entre peticiones
MAX_RETRIES = 4


def post_form(session: requests.Session, fields: dict, timeout: int = 60) -> requests.Response:
    return session.post(BASE, data=fields, timeout=timeout)


def download_month(
    session: requests.Session, est_id: int, param: str, year: int, month: int
) -> list[dict] | None:
    """Descarga un mes de datos horarios validados. Reintenta ante fallos."""
    import calendar

    last_day = calendar.monthrange(year, month)[1]
    fields = {
        "metodo": "getDatos",
        "estacionesId": str(est_id),
        "fechaInit": f"{year}-{month:02d}-01",
        "fechaFin": f"{year}-{month:02d}-{last_day:02d}",
        "paramId": param,
        "campos": "2",
        "limit": "1",
        "inc": "1",
        "soloVal": "1",
        "soloValidados": "1",
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = post_form(session, fields)
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else []
        except (requests.RequestException, json.JSONDecodeError) as exc:
            wait = 2**attempt
            print(f"    [retry {attempt}/{MAX_RETRIES}] {exc} — espero {wait}s")
            time.sleep(wait)
    return None


def raw_path(est_id: int, param: str) -> Path:
    safe_param = param.replace(".", "_")
    return RAW_DIR / f"sinaica_{est_id}_{safe_param}.jsonl.gz"


def append_rows(path: Path, rows: list[dict]) -> None:
    with gzip.open(path, "at", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def months_between(start: date, end: date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Descarga datos horarios validados SINAICA Monterrey")
    parser.add_argument("--estados", type=int, nargs="*", default=None,
                        help="IDs de estación (p. ej. 148 146 141). Vacío = las 15 de docs/stations.csv")
    parser.add_argument("--params", nargs="*", default=DEFAULT_PARAMS)
    parser.add_argument("--year-start", type=int, default=YEAR_START)
    parser.add_argument("--year-end", type=int, default=YEAR_END)
    args = parser.parse_args()

    stations = pd.read_csv(STATIONS_CSV)
    est_ids = args.estados if args.estados else stations["id"].tolist()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = "aire-monterrey-bigquery script (proyecto de analisis; contacto: repo github)"

    total_requests = 0
    for est_id in est_ids:
        nombre = stations.set_index("id").loc[est_id, "nombre"] if est_id in stations["id"].values else "?"
        for param in args.params:
            target = raw_path(est_id, param)
            # iniciar en la fecha más tardía entre el proyecto y el arranque real de la serie
            start_from = max(date(args.year_start, 1, 1), date(yearStart_est(est_id), 1, 1))
            for y, m in months_between(start_from, date(args.year_end, 12, 1)):
                rows = download_month(session, est_id, param, y, m)
                total_requests += 1
                if rows is None:
                    print(f"  [FAILED] {est_id} {param} {y}-{m:02d}: fallo definitivo")
                    continue
                if rows:
                    append_rows(target, rows)
                print(f"  [OK] est {est_id} ({nombre}) {param} {y}-{m:02d}: {len(rows)} filas")
                time.sleep(SLEEP_SECONDS)

    print(f"\nTerminal: {total_requests} peticiones. Archivos en {RAW_DIR}")


def yearStart_est(est_id: int) -> int:
    """No pedir meses anteriores al inicio real de la serie (información de stations.csv)."""
    stations = pd.read_csv(STATIONS_CSV).set_index("id")
    if est_id in stations.index:
        ini = pd.to_datetime(stations.loc[est_id, "fecha_ini_datos"])
        return max(ini.year - 1, 1997)  # margen de un año para capturar arranque desalineado
    return 1997


if __name__ == "__main__":
    main()
