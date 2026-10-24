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

    ax1.set_title("Calidad del aire AMM · media anual de red, 2015-2024\nPM2.5 −20% (aún 2× norma) · O3 +27%", fontsize=11)
    ax1.set_xticks(list(pm["anio"]))
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(IMG / "fig_tendencia_anual.png", dpi=130)
    plt.close(fig)


def fig_ranking() -> None:
    df = pd.read_csv(OUT / "03_ranking_estacionesa.csv").sort_values("media_pm25_decenio")
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    barras = ax.barh(df["estacion"], df["media_pm25_decenio"], color=ROJO, alpha=0.8)
    for b, pct in zip(barras, df["pct_dias_sobre_norma"]):
        ax.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2, f"{pct:.1f}% días>norma",
                va="center", fontsize=8, color=GRIS)
    ax.axvline(10, color="k", ls="--", lw=1)
    ax.text(10.2, -0.6, "norma anual 10", fontsize=8, color="k")
    ax.set_xlabel("PM2.5 media 2015-2024 (µg/m³)")
    ax.set_title("¿Qué estación respira peor? · PM2.5 por estación, 2015-2024", fontsize=11)
    fig.tight_layout()
    fig.savefig(IMG / "fig_ranking_pm25.png", dpi=130)
    plt.close(fig)


def fig_contingencias() -> None:
    df = pd.read_csv(OUT / "04_contingenciasa.csv").sort_values("anio")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    w = 0.38
    ax.bar(df["anio"] - w / 2, df["pm_dias_norma"], width=w, color=ROJO, alpha=0.85, label="PM2.5 · días sobre norma (>41 µg/m³ 24h)")
    ax.bar(df["anio"] + w / 2, df["o3_dias_norma"], width=w, color=AZUL, alpha=0.85, label="O3 · días sobre norma (>0.090 ppm 1h)")
    ax.bar(df["anio"] + w / 2, df["o3_dias_contingencia"], width=w, color="navy", alpha=0.95, label="O3 · nivel contingencia probable (>0.130)")
    ax.set_ylabel("días")
    ax.set_title("Contingencias ambientales (días técnicos por norma) · 2015-2024\n2024: récord de 20 días con levels de contingencia O3", fontsize=11)
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
    ax.set_title("Top 10 días más contaminados del decenio (PM2.5)\n#1: 1-ene-2019, pirotecnia + inversión térmica", fontsize=11)
    for i, (lbl, row) in enumerate(zip(top["fecha"].dt.strftime("%Y-%m-%d"), top.itertuples())):
        ax.text(row.media_24h_ciudad + 1, i, f"peor est: {row.media_24h_peor_est:.0f}", va="center", fontsize=8, color=GRIS)
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
