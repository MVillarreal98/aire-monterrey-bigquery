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

## Arreglos aplicados al reporte (2026-10-25, editado por el dueño)

Defectos que las capturas del 2026-10-24 dejaron a la vista, ya corregidos:

- [x] **Scorecards etiquetados** "Media por medición (µg/m³)" y "(ppm)": las métricas se
  renombraron en la fuente de datos (`CASE WHEN param = "PM2.5" / "O3" THEN valor END`;
  en la primera pasada el nombre quedó pegado dentro de la fórmula y la ordenación usaba
  SUM, que ordenaba por la suma horaria del día y no por la media mostrada).
- [x] **Scorecards de O3 con precisión útil:** 0.0219 → 0.0280 ppm (antes 0.02 → 0.03).
- [x] **Tabla del top 10 ordenada por la métrica mostrada** (ordenación en AVG,
  descendente). Con el orden correcto, los 10 días caen entre diciembre y enero y 4 son
  1 de enero — coherente con `outputs/04_contingenciasb.csv`.
- [x] **Cuadros de texto alineados con el repo:** respuesta directa en cada página
  ("¿Respiró mejor…? Sí y no"), causas marcadas como hipótesis y las cifras del repo
  (+29 % red completa, +37 % panel fijo; 5.2 % → 9.9 % de estación-días).

## Trade-offs que quedan

1. Los scorecards siguen promediando por fila horaria (−23 %): el repo reporta −20 %
   (media diaria → anual, query 2C) y −14.1 % (panel fijo, query 2D). La diferencia
   queda etiquetada en el propio reporte y en el README.
2. Al renombrar las métricas en la fuente, los títulos y leyendas de los gráficos de
   Tendencias y Ranking dicen "Media por medición (µg/m³)" en vez de "PM2.5 (µg/m³)".
   Las unidades desambiguan y los captions nombran los contaminantes.
