"""
Heatmap de calidad del aire sobre el mapa real de Monterrey (folium).

Lee el parquet procesado + docs/stations.csv y genera:
  outputs/heatmap_pm25_<año|decenio>.html → media horaria de PM2.5 por estación
  outputs/heatmap_o3_<año|decenio>.html   → media horaria de O3 por estación

--year (p. ej. 2015) usa un solo año; sin --year usa 2015-2024 completo.

Limitaciones de lectura:
  · La intensidad se normaliza contra el máximo de CADA mapa, así que los
    colores de dos mapas (p. ej. 2015 y 2024) no son comparables: compara los
    números de las etiquetas.
  · La capa HeatMap suma la intensidad de estaciones cercanas y no interpola
    entre estaciones: los puntos son estaciones.
  · La media es de todas las horas del periodo; el ranking de sql/03 usa
    medias diarias, así que las cifras pueden diferir un poco.

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
        titulo = f"{param} · media decenal 2015-2024"

    medias = subset.groupby("estacion_id")["valor"].mean().rename("media")
    est = stations.join(medias, on="id")
    est = est.dropna(subset=["media", "lat", "lon"])

    # Peso del heatmap: media / norma (PM2.5: 41 µg/m³ de 24 h; O3: 0.090 ppm),
    # reescalado contra el máximo del mapa, de modo que la estación más alta
    # siempre vale 1.0. Por eso los colores no se comparan entre mapas.
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
        # O3 en ppm necesita 3 decimales en el tooltip (con 2 todas las estaciones salían 0.02/0.03)
        media_txt = f"{row['media']:.3f} ppm" if param == "O3" else f"{row['media']:.2f} µg/m³"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            tooltip=folium.Tooltip(
                f"{row['nombre']} ({row['codigo']}) · {row['municipio']}\n"
                f"media {param} = {media_txt}",
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

    # Título flotante sobre el mapa: si va como bloque encima, el mapa (100 % de alto)
    # se desborda y la atribución de OpenStreetMap queda fuera de la ventana y de la captura.
    titulo_html = (
        "<h4 style='position:fixed;top:8px;left:50%;transform:translateX(-50%);z-index:1000;"
        "margin:0;padding:4px 10px;background:rgba(255,255,255,0.9);border-radius:4px;"
        f"font-family:sans-serif'>{titulo}</h4>"
    )
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
