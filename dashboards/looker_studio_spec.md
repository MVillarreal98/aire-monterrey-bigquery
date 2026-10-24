# Spec · Dashboard Looker Studio "Calidad del Aire AMM 2015-2024"

Origen al dashboard: tabla particionada `sima_horarios` en BigQuery
(Looker Studio se conecta nativamente a BQ y ejecuta SQL en el warehouse —
el modelo ELT completo queda reproducible: API → parquet → BigQuery → dashboard).

## Páginas del dashboard

### 1. Resumen ejecutivo (scorecards)
- Scorecards grandes: **media anual PM2.5** y **media anual O3**, con selector de año
  (default 2024) y % de cambio vs 2015 a lado.
- Sparkline 2015-2024 de cada uno (media de red).
- Card "días sobre norma" (PM2.5 > 41 µg/m³ 24h · O3 > 0.090 ppm 1h).

### 2. Tendencias y estacionalidad
- Serie temporal mensual PM2.5 y O3 (promedio entre estaciones midieron ese día).
- Heatmap hora×mes (pattern horario del sql/05): evidencia la
  *inversión térmica* PM2.5 madrugada/invierno vs *pico vespertino* O3.

### 3. Ranking de estaciones
- Barras horizontales: media PM2.5 por estación (barras coloreadas de rojo a verde por media).
- Barras O3. Tooltip con días sobre norma.
- Filtro de municipio (San Pedro vs Apodaca vs Centro…).

### 4. Días de contingencia (storytelling)
- Tabla de los 30 peores días (sql/04 4B) con la peor estación marcada.
- Segmento de serie anual de contingencias probables.

## Cómo montar el proyecto (tareas)

> **ESTADO: publicado ✅ (24-oct-2026)**
> https://datastudio.google.com/reporting/fe47cccc-d1c9-4392-97d0-605069f4096c
> Montado con conexión directa a la tabla `sima_horarios` (las filas ya vienen
> validadas del downloader); campo calculado por parámetro (`CASE WHEN param`),
> dimensión temporal en granularidad "Año y mes", métricas con agregación Media
> y cálculo acumulativo Ninguna, O3 en eje derecho, scorecards con rango fijo
> 2015/2024.

1. **Conectar:** Looker Studio → BigQuery dataset `sima` (proyecto `aire-monterrey-bq`).

## Pasos para publicar el dashboard (4 pasos, ~10 min)

1. Conecta los datos: en [lookerstudio.google.com](https://lookerstudio.google.com) →
   **Blank report → Add data → BigQuery** → selecciona proyecto `aire-monterrey-bq` →
   dataset `sima` → tabla `sima_horarios`. Conexión "Custom query" (
   pega `SELECT * FROM \`aire-monterrey-bq.sima.sima_horarios\` WHERE validado = 1`).
   ⚠️ Conexión con acceso "owner credentials" (así nadie necesita tu permiso de BQ).
2. Monta las 4 páginas según la spec arriba (scorecards → tendencias → ranking → contingencias).
3. **Revisa la cuota:** el conector corre queries con el billing del proyecto;
   el sandbox gratuito de BQ incluye 1 TB/mes de consulta — holgado para este dataset.
4. Publica: botón **Share → Invite with link** (opción "View"), cambia "Restricted" a
   "Anyone with the link", copia URL y pégala en `README.md` reemplazando el placeholder
   "link pendiente". Conserva la data solo en modo lectura (no "Editor").

## Capturas (pendiente)
- [ ] captura página 1 (resumen)
- [ ] captura ranking de estaciones
- [ ] captura heatmap hora×mes
