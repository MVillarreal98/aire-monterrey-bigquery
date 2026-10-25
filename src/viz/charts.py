"""
Figuras del decenio (matplotlib) a partir de los CSV de outputs/.
Se guardan en docs/img/ — esas SÍ van al repo como evidencia estable
(los HTML de folium dependen de tiles externos, como evidencia van como PNG).

Uso:
    .venv/Scripts/python src/viz/charts.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "outputs"
IMG = REPO / "docs" / "img"

AZUL, ROJO, GRIS = "#2c7fb8", "#d95f0e", "0.45"


def fig_tendencia() -> None:
    df = pd.read_csv(OUT / "02_tendencia_anuala.csv")
    fig, ax1 = plt.subplots(figsize=(10, 4.8))

    o3 = df[df["param"] == "O3"].sort_values("anio")
    pm = df[df["param"] == "PM2.5"].sort_values("anio")

    ax1.bar(pm["anio"], pm["media_anual"], color=ROJO, alpha=0.75, label="PM2.5 (µg/m³, media)")
    ax1.axhline(10, color=ROJO, ls="--", lw=1, label="Norma anual NOM-025 (10 µg/m³)")
    ax1.set_ylabel("PM2.5 µg/m³", color=ROJO)
    ax1.set_ylim(0, 30)
    ax1.tick_params(axis="y", labelcolor=ROJO)

    ax2 = ax1.twinx()
    ax2.plot(o3["anio"], o3["media_anual"], color=AZUL, marker="o", lw=2, label="O3 (ppm, media)")
    ax2.set_ylabel("O3 ppm", color=AZUL)
    ax2.set_ylim(0.015, 0.035)
    ax2.tick_params(axis="y", labelcolor=AZUL)

    # El título no debe decir más que el README: el −20 % de PM2.5 es de la red completa
    # (7 estaciones en 2015, 14 en 2024) y el +27 % de O3 sale de medias redondeadas.
    ax1.set_title(
        "Calidad del aire AMM · media anual de la red completa, 2015-2024 (sin corregir cambio de red)\n"
        "PM2.5 −20 % red completa; ≈ −11 % mismas 7 estaciones (estimación) · "
        "O3 +27 % (+22 % a +33 % por redondeo)",
        fontsize=9.5,
    )
    ax1.set_xticks(list(pm["anio"]))
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="lower left", fontsize=8, framealpha=0.95)
    fig.tight_layout()
    fig.savefig(IMG / "fig_tendencia_anual.png", dpi=130)
    plt.close(fig)


def fig_ranking() -> None:
    df = pd.read_csv(OUT / "03_ranking_estacionesa.csv").sort_values("media_pm25_decenio")
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    barras = ax.barh(df["estacion"], df["media_pm25_decenio"], color=ROJO, alpha=0.8)
    # Días medidos en la etiqueta: la cobertura varía mucho por estación (SE2: 429 días en 2015-2019).
    for b, pct, dias in zip(barras, df["pct_dias_sobre_norma"], df["dias_medidos"]):
        ax.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2,
                f"{pct:.1f}% días>norma · {dias:,} días medidos",
                va="center", fontsize=8, color=GRIS)
    ax.axvline(10, color="k", ls="--", lw=1)
    ax.text(10.2, len(df) - 0.4, "norma anual 10", fontsize=8, color="k")
    ax.set_xlim(0, df["media_pm25_decenio"].max() * 1.55)
    ax.set_xlabel("PM2.5 media 2015-2024 (µg/m³)")
    ax.set_title("¿Qué estación respira peor? · PM2.5 por estación, 2015-2024", fontsize=11)
    fig.tight_layout()
    fig.savefig(IMG / "fig_ranking_pm25.png", dpi=130)
    plt.close(fig)


def fig_contingencias() -> None:
    df = pd.read_csv(OUT / "04_contingenciasa.csv").sort_values("anio")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    w = 0.38
    ax.bar(df["anio"] - w / 2, df["pm_dias_norma"], width=w, color=ROJO, alpha=0.85, label="PM2.5 · media de red > 41 µg/m³ (24 h)")
    ax.bar(df["anio"] + w / 2, df["o3_dias_norma"], width=w, color=AZUL, alpha=0.85, label="O3 · peor estación > 0.090 ppm (1 h)")
    ax.bar(df["anio"] + w / 2, df["o3_dias_contingencia"], width=w, color="navy", alpha=0.95, label="O3 · peor estación > 0.130 ppm (umbral del autor, no oficial)")
    ax.set_ylabel("días")
    ax.set_xticks(list(df["anio"]))
    # Los conteos de O3 usan la peor estación del día: suben al sumar estaciones (2017, 2020, 2022).
    ax.set_title("Días sobre norma por año · 2015-2024 (no son contingencias oficiales)\n"
                 "O3 cuenta la peor estación del día: sube al sumar estaciones (sin normalizar por red)", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(IMG / "fig_contingencias.png", dpi=130)
    plt.close(fig)


def fig_peores_dias() -> None:
    df = pd.read_csv(OUT / "04_contingenciasb.csv")
    df["fecha"] = pd.to_datetime(df["fecha"])
    top = df.sort_values("media_24h_ciudad").tail(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.6, 4.2))
    ax.barh(top["fecha"].dt.strftime("%Y-%m-%d"), top["media_24h_ciudad"], color=ROJO)
    ax.set_xlabel("PM2.5 media 24h de la red (µg/m³)")
    # Sin causas en el título: pirotecnia e inversión térmica son hipótesis (README, Limitaciones).
    ax.set_title("Top 10 días con mayor PM2.5 media de la red, 2015-2024\n"
                 "10 de 10 en dic-ene; 5 son 1-ene (algunos con pocas estaciones midiendo)", fontsize=10)
    for i, row in enumerate(top.itertuples()):
        ax.text(row.media_24h_ciudad + 1, i,
                f"peor est: {row.media_24h_peor_est:.0f} · {row.estaciones_midieron} est.",
                va="center", fontsize=8, color=GRIS)
    ax.set_xlim(0, top["media_24h_ciudad"].max() * 1.25)
    fig.tight_layout()
    fig.savefig(IMG / "fig_peores_dias.png", dpi=130)
    plt.close(fig)


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    fig_tendencia()
    fig_ranking()
    fig_contingencias()
    fig_peores_dias()
    for f in sorted(IMG.glob("*.png")):
        print(f"[OK] {f.name}")


if __name__ == "__main__":
    main()
