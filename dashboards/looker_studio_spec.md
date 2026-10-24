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
1. **Conectar:** Looker Studio → BigQuery dataset `sima` (proyecto `aire-mty`).
2. **Campos calculados:** % cambio vs 2015 = media anual / media 2015 − 1.
3. **Controles:** desplegable de año, desplegable de estación, rango de fechas.
4. **Filtrado por hora válida:** usar filtros / SQL: mantener solo `validado = 1`:
   hacerlo preferible en una vista BQ (`CREATE VIEW ... WHERE validado = 1`)
   para no repetir condición en cada gráfica del dashboard.
5. **Compartir:** enlace público de lectura (pub.aaas) — el LINK del dashboard
   se agrega aquí cuando esté publicado.

## Capturas (pendiente)
- [ ] captura página 1 (resumen)
- [ ] captura ranking de estaciones
- [ ] captura heatmap hora×mes
