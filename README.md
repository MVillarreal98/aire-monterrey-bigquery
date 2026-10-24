# aire-monterrey-bigquery 🌫️🔥

**¿Respiró mejor Monterrey en 2024 que en 2015?** Análisis de calidad del aire del Área
Metropolitana de Monterrey (AMM) sobre **~10 años de datos horarios** de ~15 estaciones
(SIMA — Sistema Integral de Monitoreo Atmosférico), procesados con **Google BigQuery**.

## Preguntas de negocio

1. **PM2.5 y Ozono:** ¿mejoró la calidad del aire de Monterrey entre 2015 y 2024?
2. **¿Qué estación respira peor?** Comparativa San Pedro vs Apodaca vs Centro (y todo el ranking de estaciones).
3. **Contingencias ambientales:** serie histórica de episodios y **mapa de calor** (folium) de la contaminación sobre la geografía real de Monterrey.

## Stack

| Capa | Tecnología |
|---|---|
| Ingesta | Python + requests → SIMA (aire.nl.gob.mx) / SINAICA-INECC |
| Almacén | BigQuery — tabla **particionada por fecha**, clúster por estación |
| Transformación | SQL sobre millones de filas (GROUP BY, ventanas, particiones) |
| Visualización | Folium (heatmap geográfico), Matplotlib, **Looker Studio** (dashboard publicado) |

## Estructura

```
aire-monterrey-bigquery/
├── sql/                 # SQL de BigQuery (incremental y numerado, como en producción)
├── src/
│   ├── download/        # scrapers/downloader de SIMA
│   ├── analysis/        # notebooks/scripts de análisis (pandas)
│   └── viz/             # folium heatmaps y gráficos
├── data/
│   ├── raw/             # archivos originales de SIMA (gitignored)
│   └── processed/       # parquet limpio listo para BigQuery (gitignored)
├── dashboards/          # instrucciones y spec del dashboard en Looker Studio
└── docs/                # decisiones (ADRs), diccionario de datos, metadatos de estaciones
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

BigQuery: autenticar con `gcloud auth application-default login`
(sandbox de GCP permite consultar gratis; los datasets públicos cuentan aparte del cupo).

## Evidencias

**Tendencia del decenio** — PM2.5 mejoró −20 % (aún 2× la norma anual), O3 empeoró +27 %:

![Tendencia anual 2015-2024](docs/img/fig_tendencia_anual.png)

**Heatmap PM2.5 sobre mapa real**: 2015 (7 estaciones) vs 2024 (red completa).
En 2015 el hotspot estaba en el suroeste (Santa Catarina, 34.8 µg/m³); en 2024
el máx es San Bernabé 30.1 y Juárez 29.2, que sube al trono del decenio
(+36.8 % entre décadas, `docs/resultados_2015_2024.md`):

| 2015 | 2024 |
|---|---|
| ![PM2.5 2015](docs/img/heatmap_pm25_2015.png) | ![PM2.5 2024](docs/img/heatmap_pm25_2024.png) |

**El resto de la evidencia** en [`docs/resultados_2015_2024.md`](docs/resultados_2015_2024.md)
y `docs/img/` (O3 2024, media decenal, ranking por estación, contingencias, peores días).

**Dashboard:** 📊 [**Ver el dashboard interactivo en Looker Studio**](https://datastudio.google.com/reporting/fe47cccc-d1c9-4392-97d0-605069f4096c) —
4 páginas: Resumen (2015 vs 2024 con flechas) · Tendencias mensuales con eje dual ·
Ranking por estación · Top 10 días de contingencia.

## Estado

- [x] Estructura del repo
- [x] Descarga de datos SIMA 2015–2024 (3,360 peticiones → 1.5 M filas validadas)
- [x] Tabla particionada en BigQuery (`aire-monterrey-bq:sima`, 1,516,017 rows)
- [x] Análisis PM2.5/O3 2015 vs 2024 (`docs/resultados_2015_2024.md`)
- [x] Ranking de estaciones (Juárez SE2, la peor en PM2.5; +36.8% entre décadas)
- [x] Contingencias + heatmap folium (`outputs/*.html`)
- [ ] Dashboard Looker Studio publicado — **✅ listo:** https://datastudio.google.com/reporting/fe47cccc-d1c9-4392-97d0-605069f4096c
