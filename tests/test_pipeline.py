"""
Tests del pipeline de ingesta (sinaica_download → build_parquet).

El caso más frágil del repo: la codificación de nombre de archivo
('PM2.5' -> 'PM2_5' en disco, y su decodificación inversa). Un cambio
a medias en cualquiera de los dos lados rompe el parquet en silencio.

Uso: .venv/Scripts/python -m pytest tests -v
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src" / "download"))

from build_parquet import parse_raw_filename  # noqa: E402
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
