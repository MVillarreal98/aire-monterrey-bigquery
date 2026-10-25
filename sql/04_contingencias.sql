-- ============================================================
-- 04 · Pregunta de negocio 3
--  Serie histórica de días técnicos de contingencia ambiental, 2015-2024
-- ============================================================
-- IMPORTANTE: esto NO reemplaza las declaraciones oficiales del
-- Programa de Contingencias de SIMA (fases por ICA). Aquí contamos
-- DÍAS TÉCNICOS por umbrales de norma, serie comparable año a año.
--
-- Umbrales:
--   PM2.5 media del día calendario:
--     > 41 µg/m³  → norma de 24 h excedida (NOM-025-SSA1-2021)
--     > 97 µg/m³  → "contingencia probable": umbral alto definido por el autor
--   O3 máximo de 1 h:
--     > 0.090 ppm → norma horaria excedida (NOM-020-SSA1-2021)
--     > 0.130 ppm → "contingencia probable": umbral alto definido por el autor
--   Las NOM se aplican como umbral constante a todo 2015-2024. Los umbrales
--   altos son referencias del autor, no los del programa oficial.
--
-- Criterios distintos por contaminante (no comparables entre sí):
--   · PM2.5 "días sobre norma" usa la MEDIA de la red ese día.
--   · O3 usa el MÁXIMO entre estaciones (la peor estación del día). Ese
--     conteo sube solo con añadir estaciones. 4C lo normaliza por
--     estación-día.

WITH pm25_diaria AS (
  -- promedio 24h por estación y día
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-monterrey-bq.sima.sima_horarios`
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
  FROM `aire-monterrey-bq.sima.sima_horarios`
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
    COUNT(*)                                              AS dias_pm25_medidos,
    COUNTIF(media_24h_red > 41)                           AS dias_norma_excedida,
    COUNTIF(media_24h_peor_estacion > 97)                 AS dias_contingencia_probable
  FROM pm25_red
  GROUP BY anio
),

dias_o3 AS (
  SELECT
    EXTRACT(YEAR FROM fecha)          AS anio,
    COUNT(*)                                              AS dias_o3_medidos,
    COUNTIF(max_1h_red > 0.090)                           AS dias_norma_excedida,
    COUNTIF(max_1h_red > 0.130)                           AS dias_contingencia_probable
  FROM o3_red
  GROUP BY anio
)

-- Serie anual lado a lado
SELECT
  p.anio,
  p.dias_pm25_medidos,
  p.dias_norma_excedida                   AS pm_dias_norma,
  p.dias_contingencia_probable            AS pm_dias_contingencia,
  o.dias_o3_medidos,
  o.dias_norma_excedida                   AS o3_dias_norma,
  o.dias_contingencia_probable            AS o3_dias_contingencia
FROM dias_pm25 p
JOIN dias_o3 o USING (anio)
ORDER BY p.anio;

-- ------------------------------------------------------------
-- 4B · Calendario de los peores 30 días del decenio (PM2.5)
--      (independiente: trae sus propios CTEs, ejecutable por sí solo)
--      Ojo: algunos días tienen pocas estaciones midiendo (columna
--      estaciones_midieron). El 1-ene-2017 entra al top con 1 sola.
-- ------------------------------------------------------------
WITH pm25_diaria AS (
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-monterrey-bq.sima.sima_horarios`
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

-- ------------------------------------------------------------
-- 4C · O3 normalizado por tamaño de red: % de estación-días cuyo
--      máximo horario supera 0.090 ppm. No depende de cuántas
--      estaciones midieron, a diferencia de o3_dias_norma de 4A.
--      Pendiente de ejecutar: sus cifras no están en docs/ todavía.
-- ------------------------------------------------------------
WITH o3_por_dia AS (
  SELECT
    estacion,
    fecha,
    MAX(valor) AS max_1h
  FROM `aire-monterrey-bq.sima.sima_horarios`
  WHERE param = 'O3'
    AND validado = 1
  GROUP BY estacion, fecha
)

SELECT
  EXTRACT(YEAR FROM fecha)                                  AS anio,
  COUNT(DISTINCT estacion)                                  AS estaciones,
  COUNT(*)                                                  AS estacion_dias,
  COUNTIF(max_1h > 0.090)                                   AS estacion_dias_sobre_norma,
  ROUND(100.0 * COUNTIF(max_1h > 0.090) / COUNT(*), 2)      AS pct_estacion_dias_sobre_norma
FROM o3_por_dia
GROUP BY anio
ORDER BY anio;
