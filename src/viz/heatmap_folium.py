"""
Heatmap de calidad del aire sobre el mapa real de Monterrey (folium).

Lee el parquet procesado + docs/stations.csv y genera:
  outputs/heatmap_pm25.html  → promedio anual de PM2.5 por estación (radio ponderado)
  outputs/heatmap_o3.html    → promedio anual de O3 por estación

Parámetros ajustables: --year (p. ej. 2015) compara un año puntual; sin --year
usa el decenio completo 2015-2024.

Uso:
    python src/viz/heatmap_folium.py [--year 2018]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import folium
import pandas as pd
from folium.plugins import HeatMap

REPO = Path(__file__).resolve().parents[2]
PARQUET = REPO / "data" / "processed" / "sima_horarios.parquet"
STATIONS_CSV = REPO / "docs" / "stations.csv"
OUT = REPO / "outputs"

# Centro geográfico del Área Metropolitana de Monterrey
MTY_CENTER = [25.6866, -100.3161]


def build_map(data: pd.DataFrame, stations: pd.DataFrame, param: str, year: int | None, out_name: str) -> None:
    subset = data[data["param"] == param]
    if year is not None:
        subset = subset[subset["fecha"].dt.year == year]
        titulo = f"{param} · AMM · {year}"
    else:
        titulo = f"{param} · media decenial 2015-2024"

    medias = subset.groupby("estacion_id")["valor"].mean().rename("media")
    est = stations.join(medias, on="id")
    est = est.dropna(subset=["media", "lat", "lon"])

    # Escala del peso del heatmap: libertad relativa entre contaminantes
    # PM2.5 en µg/m3 (nominal 10); O3 en ppm (norma 0.090) → normalizamos por norma
    if param == "PM2.5":
        est["peso"] = est["media"] / 41.0  # norma diaria
    else:
        est["peso"] = (est["media"] * 1000.0) / 90.0  # ppm → ppb relativo a norma horaria

    m = folium.Map(location=MTY_CENTER, zoom_start=10.5, tiles="CartoDB positron")
    HeatMap(
        est[["lat", "lon", "peso"]].values.tolist(),
        radius=25,
        blur=18,
        min_opacity=0.2,
    ).add_to(m)

    for _, row in est.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            tooltip=(
                f"{row['nombre']} ({row['codigo']}) · {row['municipio']}\n"
                f"media {param} = {row['media']:.3f}"
            ),
            radius=5,
            color="black",
            fill=True,
            fill_opacity=0.8,
        ).add_to(m)

    titulo_html = f"<h4 style='text-align:center;margin:4px'>{titulo}</h4>"
    m.get_root().html.add_child(folium.Element(titulo_html))

    out_path = REPO / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)
    m.save(out_path)
    print(f"[OK] mapa en {out_path} con {len(est)} estaciones")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=None)
    args = parser.parse_args()

    data = pd.read_parquet(PARQUET)
    data["fecha"] = pd.to_datetime(data["fecha"])   # parquet guarda DATE; para filtrar año volvemos datetime
    stations = pd.read_csv(STATIONS_CSV)
    suffix = str(args.year) if args.year else "decenio"

    for param, fname in [("PM2.5", f"heatmap_pm25_{suffix}.html"),
                         ("O3",    f"heatmap_o3_{suffix}.html")]:
        build_map(data, stations, param, args.year, f"outputs/{fname}")


if __name__ == "__main__":
    main()
