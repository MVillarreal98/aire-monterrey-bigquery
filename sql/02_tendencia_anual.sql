-- ============================================================
-- 02 · Pregunta de negocio 1
--  ¿Mejoró la calidad del aire de Monterrey de 2015 a 2024?
--  PM2.5 (µg/m³) y Ozono O3 (ppm): serie anual + % de cambio vs 2015
-- ============================================================
-- Normas mexicanas de referencia (NOM-025): PM2.5 anual = 10 µg/m³ · O3 horario = 0.090 ppm
--
-- Diseño del indicador (clave para comparar años con distinta cobertura de red):
--   1) Nivel DIARIO = promedio entre las estaciones que efectivamente midieron ese día.
--      → si el analizador de una estación se cayó un mes, no distorsiona el promedio.
--   2) Nivel ANUAL = promedio de los días reunidos.
--   → así cada año integra el mismo material aunque midan distinto número de horas.

-- ------------------------------------------------------------
-- 2A · Serie anual de la ciudad + cambio acumulado respecto a 2015
-- ------------------------------------------------------------
WITH dias AS (
  SELECT
    fecha,
    param,
    AVG(valor) AS prom_dia          -- "red de Monterrey" ese día
  FROM `aire-mty.sima.sima_horarios`
  WHERE validado = 1
    AND param IN ('PM2.5', 'O3')
  GROUP BY fecha, param
),

anios AS (
  SELECT
    EXTRACT(YEAR FROM fecha) AS anio,
    param,
    COUNT(*)                       AS dias_reportados,
    ROUND(AVG(prom_dia), 3)        AS media_anual
  FROM dias
  GROUP BY anio, param
),

base_2015 AS (
  SELECT param, media_anual AS media_2015
  FROM anios
  WHERE anio = 2015
)

SELECT
  a.anio,
  a.param,
  a.dias_reportados,
  a.media_anual,
  b.media_2015,
  ROUND(100.0 * (a.media_anual - b.media_2015) / b.media_2015, 1) AS pct_vs_2015
FROM anios a
JOIN base_2015 b USING (param)
ORDER BY a.param, a.anio;

-- ------------------------------------------------------------
-- 2B · Honestidad de los datos: horas válidas por estación y año
--      (decide si un "cambio" real es el medidor o la red que mide más)
-- ------------------------------------------------------------
SELECT
  EXTRACT(YEAR FROM fecha) AS anio,
  estacion,
  param,
  COUNT(*) AS horas_validas,
  COUNT(DISTINCT fecha) AS dias_con_datos
FROM `aire-mty.sima.sima_horarios`
WHERE param IN ('PM2.5', 'O3')
GROUP BY anio, estacion, param
ORDER BY param, anio, horas_validas DESC;
