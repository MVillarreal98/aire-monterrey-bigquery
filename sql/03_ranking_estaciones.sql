-- ============================================================
-- 03 · Pregunta de negocio 2
--  ¿Qué estación de la red respira peor?
--  Ranking de estaciones, con metodología + comparativa de décadas
-- ============================================================
-- Metodología:
--   · PM2.5 se evalúa contra la norma de 24 h (41 µg/m³ = año 1 de la
--     NOM-025-SSA1-2021, aplicada como umbral constante a 2015-2024; el valor
--     de año 3 es 33 µg/m³ — ver sql/02). Se usa la media del día
--     calendario por estación, no un promedio móvil de 24 h, y no se exige un
--     mínimo de horas por día (la Tabla 2 de la NOM-020 pide 18 de 24).
--     Se cuentan días que exceden, no horas.
--   · O3 se evalúa en horas (norma de 1 h = 0.090 ppm, NOM-020-SSA1-2021).
--   · Cobertura: las estaciones no midieron los mismos días (Misión San Juan
--     solo 2022-2024, Juárez sin PM2.5 en 2015). Las medias decenales mezclan
--     periodos distintos, por eso cada query reporta los días u horas medidos.
--   · O3 se redondea a 3 decimales: varias estaciones empatan y el orden
--     dentro del empate no significa nada.

-- ------------------------------------------------------------
-- 3A · Ranking 2015-2024 por PM2.5: media, p95 y días sobre norma
-- ------------------------------------------------------------
WITH diaria_pm25 AS (
  -- media del día calendario por estación (no es un promedio móvil de 24 h)
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-monterrey-bq.sima.sima_horarios`
  WHERE param = 'PM2.5'
    AND validado = 1
  GROUP BY estacion, fecha
)

SELECT
  estacion,
  COUNT(*)                                                          AS dias_medidos,
  ROUND(AVG(media_24h), 1)                                          AS media_pm25_decenio, -- µg/m³ (2015-2024)
  APPROX_QUANTILES(media_24h, 100)[OFFSET(95)]                      AS p95_dia,            -- µg/m³
  COUNTIF(media_24h > 41)                                           AS dias_sobre_norma,
  ROUND(100.0 * COUNTIF(media_24h > 41) / COUNT(*), 2)              AS pct_dias_sobre_norma
FROM diaria_pm25
GROUP BY estacion
ORDER BY media_pm25_decenio DESC;

-- ------------------------------------------------------------
-- 3B · Ranking 2015-2024 por O3: media y horas sobre norma 0.090 ppm
-- ------------------------------------------------------------
SELECT
  estacion,
  COUNT(*)                                                          AS horas_validas,
  ROUND(AVG(valor), 3)                                              AS media_o3,           -- ppm
  MAX(valor)                                                        AS max_1h,             -- ppm
  COUNTIF(valor > 0.090)                                            AS horas_sobre_norma,
  ROUND(100.0 * COUNTIF(valor > 0.090) / COUNT(*), 2)               AS pct_horas_sobre_norma
FROM `aire-monterrey-bq.sima.sima_horarios`
WHERE param = 'O3'
  AND validado = 1
GROUP BY estacion
ORDER BY media_o3 DESC;

-- ------------------------------------------------------------
-- 3C · ¿La estación que "respira peor" empeoró o mejoró?
--      PM2.5 por estación: 2015-2019 vs 2020-2024
-- ------------------------------------------------------------
WITH diaria_pm25 AS (
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-monterrey-bq.sima.sima_horarios`
  WHERE param = 'PM2.5'
    AND validado = 1
  GROUP BY estacion, fecha
)

SELECT
  estacion,
  COUNTIF(media_24h IS NOT NULL AND EXTRACT(YEAR FROM fecha) <= 2019) AS dias_2015_2019,
  ROUND(AVG(CASE WHEN EXTRACT(YEAR FROM fecha) <= 2019 THEN media_24h END), 1) AS media_2015_2019,
  COUNTIF(media_24h IS NOT NULL AND EXTRACT(YEAR FROM fecha) >= 2020) AS dias_2020_2024,
  ROUND(AVG(CASE WHEN EXTRACT(YEAR FROM fecha) >= 2020 THEN media_24h END), 1) AS media_2020_2024,
  ROUND(
    100.0 * (
      AVG(CASE WHEN EXTRACT(YEAR FROM fecha) >= 2020 THEN media_24h END)
    - AVG(CASE WHEN EXTRACT(YEAR FROM fecha) <= 2019 THEN media_24h END)
    ) / AVG(CASE WHEN EXTRACT(YEAR FROM fecha) <= 2019 THEN media_24h END),
    1
  ) AS pct_cambio
FROM diaria_pm25
GROUP BY estacion
ORDER BY pct_cambio DESC;
