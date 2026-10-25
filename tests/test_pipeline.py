"""
Tests del pipeline de ingesta (sinaica_download → build_parquet).

El caso más frágil del repo: la codificación de nombre de archivo
('PM2.5' -> 'PM2_5' en disco, y su decodificación inversa). Un cambio
a medias en cualquiera de los dos lados rompe el parquet en silencio.

Uso: .venv/Scripts/python -m pytest tests -v
"""

from __future__ import annotations

import gzip
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src" / "download"))

from build_parquet import load_raw, parse_raw_filename  # noqa: E402
from sinaica_download import months_between, raw_path  # noqa: E402


def test_raw_path_codifica_punto_como_guion():
    p = raw_path(148, "PM2.5")
    assert p.name == "sinaica_148_PM2_5.jsonl.gz"


def test_ida_y_vuelta_parametro():
    # el bug real que ya ocurrió (stem de .jsonl.gz deja cola .jsonl):
    # 'sinaica_424_O3' debe decodificar a ('424', 'O3') — nunca 'O3.jsonl'
    est_id, param = parse_raw_filename(Path("sinaica_424_O3.jsonl.gz"))
    assert (est_id, param) == (424, "O3")

    est_id, param = parse_raw_filename(raw_path(148, "PM2.5"))
    assert (est_id, param) == (148, "PM2.5")


def test_months_between_frontera_de_anio():
    ms = list(months_between(date(2015, 11, 1), date(2016, 2, 1)))
    assert ms == [(2015, 11), (2015, 12), (2016, 1), (2016, 2)]


def test_decenio_completo_120_meses():
    assert len(list(months_between(date(2015, 1, 1), date(2024, 12, 1)))) == 120


def test_load_raw_dedup_idempotente(tmp_path):
    # el downloader hace append: al re-ejecutarse deja filas duplicadas y
    # load_raw debe colapsarlas por (estacion_id, param, fecha, hora)
    raw = tmp_path / "raw"
    raw.mkdir()
    fila = {"fecha": "2019-01-01", "hora": 1, "valor": 21.0, "val": 1}
    duplicate = {**fila, "valor": 99.0}   # misma clave, valor distinto
    with gzip.open(raw / "sinaica_148_O3.jsonl.gz", "wt", encoding="utf-8") as f:
        for r in (fila, duplicate):
            f.write(json.dumps(r) + "\n")

    stations = tmp_path / "stations.csv"
    stations.write_text("id,codigo\n148,SO2\n", encoding="utf-8")

    df = load_raw(raw_dir=raw, stations_csv=stations)
    assert len(df) == 1
    assert df.iloc[0]["valor"] == 21.0   # conserva la primera, no suma

