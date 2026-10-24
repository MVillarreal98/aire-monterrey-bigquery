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
    # y remapeamos por el max del mapa: la estación más cargada siempre = 1.0
    # (sin esto O3 queda ~0.3 en todas y el gradiente no se distingue)
    if param == "PM2.5":
        peso = est["media"] / 41.0  # norma diaria
    else:
        peso = (est["media"] * 1000.0) / 90.0  # ppm → ppb relativo a norma horaria
    max_peso = peso.max()
    # sin esto O3 queda ~0.3 en todas y el gradiente no se distingue;
    # max_peso==0 (año sin datos del param) => heatmap vacío y silent NaN
    if max_peso > 0:
        est["peso"] = (peso / max_peso).clip(0.15, 1.0)
    else:
        est["peso"] = 0.5

    m = folium.Map(location=MTY_CENTER, zoom_start=10.5, tiles="OpenStreetMap")
    fmt = "{:.3f}" if param == "O3" else "{:.1f}"   # O3 en ppm necesita 3 decimales
    HeatMap(
        est[["lat", "lon", "peso"]].values.tolist(),
        radius=25,
        blur=18,
        min_opacity=0.2,
    ).add_to(m)

    for _, row in est.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            tooltip=folium.Tooltip(
                f"{row['nombre']} ({row['codigo']}) · {row['municipio']}\n"
                f"media {param} = {row['media']:.2f}{' ppm' if param == 'O3' else ' µg/m³'}",
                permanent=False,
            ),
            radius=5,
            color="black",
            fill=True,
            fill_opacity=0.8,
        ).add_to(m)
        # etiqueta permanente con el valor (sin ella, la captura PNG no muestra datos)
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.features.DivIcon(
                icon_size=(40, 16),
                icon_anchor=(20, 14),
                html=f"<div style='font-size:11px;font-weight:bold;color:#111;"
                f"text-shadow:1px 1px 2px white,-1px -1px 2px white'>{fmt.format(row['media'])}</div>",
            ),
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
