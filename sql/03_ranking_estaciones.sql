-- ============================================================
-- 03 · Pregunta de negocio 2
--  ¿Qué estación de la red respira peor?
--  Ranking de estaciones, con metodología + comparativa de décadas
-- ============================================================
-- Metodología:
--   · PM2.5 se evalúa contra la NORMA DIARIA (promedio móvil 24h = 41 µg/m³, NOM-025):
--     primero promediamos cada día, luego contamos días que exceden — no las horas.
--   · O3 se evalúa en horas (norma 1h = 0.090 ppm) porque así está definida la norma.
--   · Cobertura: si una estación midió pocos años (Pesquería desde 2020), la media
--     de 10 años no es comparable → la query reporta los años con datos reales.

-- ------------------------------------------------------------
-- 3A · Ranking 2015-2024 por PM2.5: media, p95 y días sobre norma
-- ------------------------------------------------------------
WITH diaria_pm25 AS (
  -- promedio móvil de 24h como la norma: media del día calendario por estación
  SELECT
    estacion,
    fecha,
    AVG(valor) AS media_24h
  FROM `aire-mty.sima.sima_horarios`
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
FROM `aire-mty.sima.sima_horarios`
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
  FROM `aire-mty.sima.sima_horarios`
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
