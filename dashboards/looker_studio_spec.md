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

## Capturas (pendiente)

- [ ] página 1 (resumen)
- [ ] página 3 (ranking de estaciones)
- [ ] página 4 (top 10 días)

Guardarlas en `docs/img/dashboard_*.png` y enlazarlas en el README, para que la evidencia
no dependa de que la tabla siga existiendo.
