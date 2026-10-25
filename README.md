# aire-monterrey-bigquery

**¿Respiró mejor Monterrey en 2024 que en 2015?** Análisis de calidad del aire del Área
Metropolitana de Monterrey (AMM) con ~1.5 M mediciones horarias validadas de O3 y PM2.5
(15 estaciones de la red SIMA, 2015-2024), descargadas de SINAICA/INECC y cargadas en
**Google BigQuery**.

Proyecto personal de análisis (octubre de 2026), desarrollado con asistencia de
herramientas de IA (ver [Cómo se construyó](#cómo-se-construyó)).

## Preguntas de negocio

1. **PM2.5 y ozono:** ¿mejoró la calidad del aire de Monterrey entre 2015 y 2024?
2. **¿Qué estación respira peor?** San Pedro vs Apodaca vs Centro, y el ranking completo.
3. **Días de contingencia:** serie anual de días sobre norma y mapa de las estaciones.

## Respuestas cortas (con sus límites)

1. **PM2.5 bajó y el ozono subió, pero la red cambió entre los dos años.** Con la red
   completa, la media anual de PM2.5 pasa de 26.1 a 20.8 µg/m³ (−20 %). En 2015 solo 7
   estaciones midieron PM2.5 y en 2024 fueron 14, varias con medias bajas, así que parte de
   ese −20 % se debe a la composición de la red. Con las mismas 7 estaciones el cambio
   estimado es de ≈ −11 % (≈ −16 % sin San Bernabé, que en 2024 solo midió 86 días); el
   método está en [`docs/resultados_2015_2024.md`](docs/resultados_2015_2024.md). El O3 pasa
   de 0.022 a 0.028 ppm (+27 %). Ese porcentaje se calculó sobre medias redondeadas a 3
   decimales: con esa precisión, el cambio real está entre ≈ +22 % y ≈ +33 %.
2. **Apodaca (NE2) 24.5 µg/m³, 3.ª de 14; Centro/Obispado (CE) 23.4, 4.ª; San Pedro (SO2) 18.6,
   10.ª** (media de PM2.5 en 2015-2024). La más alta es Juárez (SE2) con 26.0, pero tiene
   solo 429 días medidos en 2015-2019, contra 1,689 en 2020-2024.
3. **Días de O3 sobre norma: 73 (2015) → 121 (2024).** El conteo usa la peor estación de la
   red cada día, así que sube solo con añadir estaciones. La query 4C lo normaliza por
   estación-día.

Las queries 2C (sin redondeo intermedio), 2D (panel fijo de estaciones) y 4C (O3
normalizado) están en `sql/`, pero **todavía no se han ejecutado**. Cuando se ejecuten, sus
cifras reemplazarán a las estimaciones de arriba.

## Stack

| Capa | Tecnología |
|---|---|
| Ingesta | Python + requests → endpoint público de SINAICA/INECC (datos de la red SIMA) |
| Almacén | BigQuery: tabla particionada por fecha y clusterizada por estación y contaminante |
| Transformación | SQL de BigQuery con CTEs, agregación diaria → anual, `COUNTIF` y `APPROX_QUANTILES` sobre 1.5 M mediciones horarias |
| Visualización | Matplotlib, Folium (mapa de estaciones) y un dashboard de **Looker Studio** |

## Estructura

```
aire-monterrey-bigquery/
├── sql/                 # DDL de la tabla (01) y 4 archivos de SQL analítico (02-05)
├── src/
│   ├── download/        # descarga de SINAICA (sinaica_download.py) y parquet (build_parquet.py)
│   ├── analysis/        # run_queries.py: ejecuta sql/02-05 y guarda CSV en outputs/
│   └── viz/             # figuras matplotlib (charts.py) y mapas folium (heatmap_folium.py)
├── outputs/             # resultados commiteados: CSV de las queries y mapas HTML
├── data/
│   ├── raw/             # JSONL descargados (no se versionan)
│   └── processed/       # parquet listo para BigQuery (no se versiona)
├── dashboards/          # spec del dashboard de Looker Studio
├── docs/                # API de SINAICA, setup de GCP, estaciones, resultados y figuras PNG
└── tests/               # 5 tests unitarios de la ingesta (sin BigQuery)
```

## Reproducir

Probado en Windows 10 con Python 3.12; las versiones están fijadas en `requirements.txt`.
Los pasos 3 y 4 necesitan un proyecto de GCP propio (ver [`docs/gcp_setup.md`](docs/gcp_setup.md)).

```powershell
# 0. Entorno
python -m venv .venv
.venv\Scripts\Activate.ps1          # bash: source .venv/Scripts/activate (Windows) o .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests -v           # 5 tests de ingesta; no usan la red ni BigQuery

# 1. Descarga (3,360 peticiones a 1.1 s o más cada una: una hora o más)
python src/download/sinaica_download.py

# 2. Parquet tipado y deduplicado
python src/download/build_parquet.py

# 3. Carga a BigQuery y, justo después, el ALTER TABLE que quita la expiración de
#    particiones (comando completo y motivo en sql/01 y docs/gcp_setup.md)
bq load --source_format=PARQUET --time_partitioning_field=fecha --clustering_fields=estacion,param --replace aire-monterrey-bq:sima.sima_horarios data/processed/sima_horarios.parquet

# 4. Queries de negocio → outputs/*.csv
python src/analysis/run_queries.py

# 5. Figuras (solo leen outputs/*.csv) y mapas (leen el parquet local)
python src/viz/charts.py
python src/viz/heatmap_folium.py --year 2015
python src/viz/heatmap_folium.py --year 2024
python src/viz/heatmap_folium.py
```

`run_queries.py` usa el proyecto `aire-monterrey-bq`; para usar otro, define la variable de
entorno `AIRE_GCP_PROJECT`. Los CSV y los mapas HTML de la última corrida están commiteados
en `outputs/`, así que las cifras se pueden revisar y las figuras regenerar sin acceso a
BigQuery. Los PNG de los mapas (`docs/img/heatmap_*.png`) son capturas a 1280×860 de esos
HTML en un navegador sin interfaz (por ejemplo, `msedge --headless=new --screenshot`).

## Evidencias

**Tendencia anual de la red completa** (sin corregir el cambio de composición de la red):

![Tendencia anual 2015-2024](docs/img/fig_tendencia_anual.png)

**PM2.5 por estación, 2015 (7 estaciones) vs 2024 (14 estaciones).** Cada mapa se normaliza
contra su propio máximo, así que los colores **no** se pueden comparar entre los dos mapas:
compara los números de cada estación. Los puntos son estaciones y el color no interpola
entre ellas. San Bernabé (NO, 30.1 en 2024) solo tiene 86 días medidos ese año.

| 2015 | 2024 |
|---|---|
| ![PM2.5 2015](docs/img/heatmap_pm25_2015.png) | ![PM2.5 2024](docs/img/heatmap_pm25_2024.png) |

El resto de la evidencia (O3 2024, media decenal, ranking, días sobre norma y peores días)
está en [`docs/resultados_2015_2024.md`](docs/resultados_2015_2024.md) y en `docs/img/`.

**Dashboard:** [Looker Studio](https://datastudio.google.com/reporting/fe47cccc-d1c9-4392-97d0-605069f4096c),
con 4 páginas: resumen 2015 vs 2024, tendencias mensuales, ranking por estación y top 10 días
de PM2.5. Se conecta en vivo a la tabla de BigQuery: si la tabla expira o se borra, el
dashboard se queda sin datos (ver [`docs/gcp_setup.md`](docs/gcp_setup.md)).

## Fuente de datos y atribución

- **Datos:** Sistema Nacional de Información de la Calidad del Aire (SINAICA), del
  INECC/SEMARNAT, con las mediciones de la red SIMA del Gobierno de Nuevo León. Se
  descargaron en octubre de 2026 con el filtro de datos validados, desde el endpoint que usa
  el portal público <https://sinaica.inecc.gob.mx>, a una petición cada 1.1 s. No es una API
  oficial documentada (ver [`docs/sinaica_api.md`](docs/sinaica_api.md)).
- **Qué se publica:** solo agregados derivados (`outputs/*.csv`, figuras y mapas). Los datos
  crudos y el parquet no se redistribuyen.
- **Mapas base:** © OpenStreetMap contributors (ODbL).
- **Licencia:** el código de este repositorio es MIT ([`LICENSE`](LICENSE)). Los datos y sus
  derivados conservan los términos de su fuente (SINAICA/INECC); la licencia MIT no se
  extiende a ellos.

## Limitaciones

- **Composición de la red:** se suman estaciones en 2017 (Cadereyta, UANL, ITESM Sur), 2020
  (Pesquería) y 2022 (Misión San Juan), y la cobertura por estación y año varía mucho
  (`outputs/02_tendencia_anualb.csv`). Las medias de red y los conteos que usan la peor
  estación del día dependen de qué estaciones midieron.
- **Sin criterio de suficiencia diaria:** un día con pocas horas válidas cuenta como media
  diaria completa, cuando la práctica normativa pide al menos 75 % de las horas. El top 10 de
  días incluye el 1-ene-2017, con una sola estación midiendo.
- **Normas:** se aplican los valores de la NOM-025-SSA1-2021 (PM2.5) y la NOM-020-SSA1-2021
  (O3) como umbral constante a todo 2015-2024, aunque antes de 2021 regían otros valores. Los
  umbrales de "contingencia probable" (97 µg/m³ y 0.130 ppm) los fijó el autor como
  referencia; no son las declaraciones oficiales del programa de contingencias.
- **Outliers:** hay lecturas de 991 µg/m³ y de −1, y no se aplicó enmascaramiento por evento.
- **Diseño de la tabla:** con unas 415 filas por día, la partición diaria no ahorra costo con
  este volumen, y las queries de `sql/02-05` no filtran por fecha. Se dejó para practicar el
  patrón.
- **Atribuciones causales** (pirotecnia, industria, inversión térmica): son hipótesis
  consistentes con los datos, no resultados medidos.

## Cómo se construyó

Desarrollado con asistencia de herramientas de IA. Los commits `fix: review …` del historial
corresponden a rondas de revisión del código y de las afirmaciones de los documentos,
también asistidas por IA. Los 5 tests de `tests/test_pipeline.py` cubren solo los helpers de
ingesta (codificación del nombre de archivo, meses y deduplicación). El workflow
`.github/workflows/tests.yml` puede ejecutarlos en GitHub Actions en cada push
a `main` y en cada pull request. El SQL y las figuras no tienen tests automatizados.
