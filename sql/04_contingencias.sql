-- ============================================================
-- 04 · Pregunta de negocio 3
--  Serie histórica de días técnicos de contingencia ambiental, 2015-2024
-- ============================================================
-- IMPORTANTE: esto NO reemplaza las declaraciones oficiales del
-- Programa de Contingencias de SIMA (fases por ICA). Aquí contamos
-- DÍAS TÉCNICOS por umbrales de norma, serie comparable año a año.
--
-- Umbrales de referencia (NOM/protocolos SIMA):
--   PM2.5 media 24h:
--     > 41 µg/m³  → día "mal tiempo" (norma diaria excedida)
--     > 97 µg/m³  → nivel de contingencia probable (ICA ~ 200)
--   O3 máximo 1h:
--     > 0.090 ppm → norma horaria excedida
--     > 0.130 ppm → nivel de contingencia probable (IMECA ~ 200)

WITH pm25_diaria AS (
  -- promedio 24h por estación y día
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-mty.sima.sima_horarios`
  WHERE param = 'PM2.5'
    AND validado = 1
  GROUP BY estacion, fecha
),

o3_por_dia AS (
  -- máximo horario del día por estación
  SELECT
    estacion,
    fecha,
    MAX(valor) AS max_1h
  FROM `aire-mty.sima.sima_horarios`
  WHERE param = 'O3'
    AND validado = 1
  GROUP BY estacion, fecha
),

pm25_red AS (
  -- "red de la ciudad": media del día entre estaciones que midieron
  SELECT
    fecha,
    AVG(media_24h)              AS media_24h_red,
    MAX(media_24h)              AS media_24h_peor_estacion,
    COUNT(*)                    AS estaciones_midieron
  FROM pm25_diaria
  GROUP BY fecha
),

o3_red AS (
  SELECT
    fecha,
    AVG(max_1h)                 AS max_1h_red_prom,
    MAX(max_1h)                 AS max_1h_red,      -- la peor estación ese día
    COUNT(*)                    AS estaciones_midieron
  FROM o3_por_dia
  GROUP BY fecha
),

dias_pm25 AS (
  SELECT
    EXTRACT(YEAR FROM fecha)          AS anio,
    COUNT(*)                                              AS dias_pm25_mididos,
    COUNTIF(media_24h_red > 41)                           AS dias_norma_excedida,
    COUNTIF(media_24h_peor_estacion > 97)                 AS dias_contingencia_probable
  FROM pm25_red
  GROUP BY anio
),

dias_o3 AS (
  SELECT
    EXTRACT(YEAR FROM fecha)          AS anio,
    COUNT(*)                                              AS dias_o3_mididos,
    COUNTIF(max_1h_red > 0.090)                           AS dias_norma_excedida,
    COUNTIF(max_1h_red > 0.130)                           AS dias_contingencia_probable
  FROM o3_red
  GROUP BY anio
)

-- Serie anual lado a lado
SELECT
  p.anio,
  p.dias_pm25_mididos,
  p.dias_norma_excedida                   AS pm_dias_norma,
  p.dias_contingencia_probable            AS pm_dias_contingencia,
  o.dias_o3_mididos,
  o.dias_norma_excedida                   AS o3_dias_norma,
  o.dias_contingencia_probable            AS o3_dias_contingencia
FROM dias_pm25 p
JOIN dias_o3 o USING (anio)
ORDER BY p.anio;

-- ------------------------------------------------------------
-- 4B · Calendario de los peores 30 días del decenio (PM2.5)
--      alimenta anotaciones del mapa folium / dashboard
--      (independiente: trae sus propios CTEs, ejecutable por sí solo)
-- ------------------------------------------------------------
WITH pm25_diaria AS (
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-mty.sima.sima_horarios`
  WHERE param = 'PM2.5'
    AND validado = 1
  GROUP BY estacion, fecha
),

pm25_red AS (
  SELECT
    fecha,
    AVG(media_24h) AS media_24h_red,
    MAX(media_24h) AS media_24h_peor_estacion,
    COUNT(*)       AS estaciones_midieron
  FROM pm25_diaria
  GROUP BY fecha
)

SELECT
  fecha,
  ROUND(media_24h_red, 1)           AS media_24h_ciudad,
  ROUND(media_24h_peor_estacion, 1) AS media_24h_peor_est,
  estaciones_midieron
FROM pm25_red
WHERE media_24h_red > 41
ORDER BY media_24h_red DESC
LIMIT 30;
