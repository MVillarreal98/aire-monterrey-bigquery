"""
Convierte los JSONL de data/raw/ a un solo parquet limpio en data/processed/
Esquema tipado listo para cargar a BigQuery.

Uso:
    python src/download/build_parquet.py
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW_DIR = REPO / "data" / "raw"
OUT = REPO / "data" / "processed" / "sima_horarios.parquet"
STATIONS_CSV = REPO / "docs" / "stations.csv"


def load_raw() -> pd.DataFrame:
    stations = pd.read_csv(STATIONS_CSV)
    id2code = dict(zip(stations["id"], stations["codigo"]))
    frames = []
    for f in sorted(RAW_DIR.glob("sinaica_*_*.jsonl.gz")):
        est_id, param = f.stem.replace("sinaica_", "").split("_", 1)
        est_id = int(est_id)
        param = param.replace("_", ".")
        rows = [json.loads(line) for line in gzip.open(f, "rt", encoding="utf-8")]
        if not rows:
            continue
        df = pd.DataFrame(rows)[["fecha", "hora", "valor", "val"]]
        df["estacion_id"] = est_id
        df["estacion"] = id2code.get(est_id)
        df["param"] = param
        frames.append(df)
        print(f"[OK] {f.name}: {len(df)} filas")
    if not frames:
        raise SystemExit("No hay archivos raw. Corre primero sinaica_download.py")
    big = pd.concat(frames, ignore_index=True)

    big["fecha"] = pd.to_datetime(big["fecha"]).dt.date   # DATE (no TIMESTAMP): será campo de partición en BQ
    big["hora"] = big["hora"].astype(int)
    big["valor"] = pd.to_numeric(big["valor"], errors="coerce")
    big["val"] = big["val"].astype(int)
    big = big.dropna(subset=["valor"])
    # idempotencia: una re-ejecución del downloader añade duplicados; no re-contar aquí
    big = big.drop_duplicates(subset=["estacion_id", "param", "fecha", "hora"])
    big = big.rename(columns={"val": "validado"})
    big["valor"] = big["valor"].astype(float)
    return big[["estacion_id", "estacion", "param", "fecha", "hora", "valor", "validado"]]


def main() -> None:
    df = load_raw()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    print(f"\nParquet: {OUT} — {len(df):,} filas")
    print(df.groupby("param")["valor"].describe())


if __name__ == "__main__":
    main()
