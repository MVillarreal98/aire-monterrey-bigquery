# Dashboard Looker Studio "Calidad del Aire AMM 2015-2024"

## Estado

Publicado el 24-oct-2026 con acceso de solo lectura para cualquiera con el enlace:
<https://datastudio.google.com/reporting/fe47cccc-d1c9-4392-97d0-605069f4096c>

Lo que se construyó, según el autor (el contenido se renderiza con JavaScript y no se
puede verificar desde este repo):

- **Conexión:** directa a la tabla `aire-monterrey-bq.sima.sima_horarios`, sin consulta
  personalizada. Las filas ya vienen validadas del downloader. Acceso con "owner
  credentials", así que quien lo abre no necesita permisos de BigQuery.
- **Campos:** campo calculado por contaminante (`CASE WHEN param …`), dimensión temporal
  con granularidad "Año y mes", métricas con agregación Media.
- **4 páginas:**
  1. Resumen: scorecards de 2015 vs 2024 (rango fijo) con flechas de cambio.
  2. Tendencias mensuales de PM2.5 y O3, con el O3 en el eje derecho.
  3. Ranking por estación.
  4. Top 10 días más contaminados (PM2.5).

Riesgo: el dashboard lee la tabla en vivo. Si la tabla expira (sandbox de BigQuery), se
queda sin datos. Ver la sección "Pendiente" de [`docs/gcp_setup.md`](../docs/gcp_setup.md).

## Diseño original (no todo se implementó)

Se conserva como referencia. Diferencias con lo publicado:

- La spec pedía la tabla de los 30 peores días de `sql/04` (4B); se publicó un top 10.
- Un filtro por municipio necesitaría combinar la tabla con `docs/stations.csv`, porque
  `sima_horarios` no tiene columna de municipio. No consta que se haya implementado.
- El heatmap hora × mes de `sql/05` y la serie anual de días de contingencia no constan en
  las 4 páginas publicadas.
- Las cifras del dashboard usan la media de las mediciones horarias. Pueden no coincidir
  con las del README, que usan medias diarias (`sql/02` y `sql/03`), y no corrigen el cambio
  de composición de la red.

## Pasos para reproducirlo

1. En [lookerstudio.google.com](https://lookerstudio.google.com): **Blank report → Add
   data → BigQuery** → proyecto → dataset `sima` → tabla `sima_horarios`, con acceso
   "owner credentials".
2. Montar las páginas descritas arriba.
3. **Share → Invite with link**, opción "View", y cambiar "Restricted" a "Anyone with the
   link".

## Capturas (tomadas el 2026-10-24)

- [x] página 1 (resumen) — `docs/img/dashboard_resumen.png`
- [x] página 2 (tendencias mensuales) — `docs/img/dashboard_tendencias.png`
- [x] página 3 (ranking de estaciones) — `docs/img/dashboard_ranking.png`
- [x] página 4 (top 10 días) — `docs/img/dashboard_contingencias.png`

Enlazadas en el README, para que la evidencia no dependa de que la tabla siga existiendo.

## Pendientes del reporte (requieren editarlo en Looker Studio, como dueño)

Defectos que las capturas del 2026-10-24 dejaron a la vista:

1. **Scorecards del resumen:** promedian por fila horaria (26.79 → 20.58 µg/m³, −23 %),
   mientras el repo usa media diaria → anual (−20 %, query 2C) y panel fijo (−14.1 %,
   query 2D). Un lector que compare los tres números ve una contradicción. Corregir
   cambiando la métrica del scorecard o etiquetándola como "media por medición".
2. **Scorecards de O3 con 2 decimales** (0.02 → 0.03): sin precisión útil. Cambiar el
   formato a 3 decimales, o a ppb con 1 decimal como la query 2C.
3. **Tabla del top 10:** 28-ene-2023 (61.52) aparece arriba de 17-ene-2019 (62.41), y
   30-abr-2019 (47.16) arriba de 28-abr-2021 (50.05): el orden no corresponde a la columna
   PM2.5 que se muestra. Revisar el sort del componente.
4. **Cuadros de texto que afirman causas** ("pirotecnia + inversión térmica nocturna",
   "récord de días en contingencia", "O3 +36 %"): en el repo esas afirmaciones ya se
   marcan como hipótesis o se corrigieron (query 2C: +29.2 %). Reescribirlos o quitarlos.
