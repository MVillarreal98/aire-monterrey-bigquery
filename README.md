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

## Estado

- [x] Estructura del repo
- [x] Descarga de datos SIMA 2015–2024 (3,360 peticiones → 1.5 M filas validadas)
- [x] Tabla particionada en BigQuery (`aire-monterrey-bq:sima`, 1,516,017 rows)
- [x] Análisis PM2.5/O3 2015 vs 2024 (`docs/resultados_2015_2024.md`)
- [x] Ranking de estaciones (Juárez SE2, la peor en PM2.5; +36.8% entre décadas)
- [x] Contingencias + heatmap folium (`outputs/*.html`)
- [ ] Dashboard Looker Studio publicado (spec lista en `dashboards/`)
