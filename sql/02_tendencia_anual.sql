-- ============================================================
-- 02 · Pregunta de negocio 1
--  ¿Mejoró la calidad del aire de Monterrey de 2015 a 2024?
--  PM2.5 (µg/m³) y Ozono O3 (ppm): serie anual + % de cambio vs 2015
-- ============================================================
-- Normas de referencia, aplicadas como umbral constante a 2015-2024:
--   PM2.5 anual = 10 µg/m³ (NOM-025-SSA1-2021) · O3 horario = 0.090 ppm (NOM-020-SSA1-2021)
--
-- Diseño del indicador de red (2A):
--   1) Nivel DIARIO = promedio de las horas válidas de todas las estaciones
--      que midieron ese día (una estación con más horas pesa más).
--   2) Nivel ANUAL = promedio de los días.
--   Esto evita que un día con más horas pese más, pero NO corrige el cambio
--   de composición de la red: si entran estaciones con niveles bajos, la
--   media baja aunque el aire no cambie. Para eso está el panel fijo (2D).
--   2A redondea media_anual a 3 decimales ANTES de calcular pct_vs_2015,
--   lo que en O3 (0.022 → 0.028) deja el % con un margen de ±5 puntos.
--   2C repite el cálculo 2015 vs 2024 sin redondeo intermedio.

-- ------------------------------------------------------------
-- 2A · Serie anual de la ciudad + cambio acumulado respecto a 2015
-- ------------------------------------------------------------
WITH dias AS (
  SELECT
    fecha,
    param,
    AVG(valor) AS prom_dia          -- "red de Monterrey" ese día
  FROM `aire-monterrey-bq.sima.sima_horarios`
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
FROM `aire-monterrey-bq.sima.sima_horarios`
WHERE param IN ('PM2.5', 'O3')
GROUP BY anio, estacion, param
ORDER BY param, anio, horas_validas DESC;

-- ------------------------------------------------------------
-- 2C · 2015 vs 2024 con la red completa, sin redondeo intermedio
--      (mismo indicador que 2A, O3 reportado en ppb con 1 decimal)
--      Ejecutada (2026-10-25): resultados en outputs/02_tendencia_anualc.csv.
-- ------------------------------------------------------------
WITH dias AS (
  SELECT
    fecha,
    param,
    AVG(valor) AS prom_dia
  FROM `aire-monterrey-bq.sima.sima_horarios`
  WHERE validado = 1
    AND param IN ('PM2.5', 'O3')
    AND EXTRACT(YEAR FROM fecha) IN (2015, 2024)
  GROUP BY fecha, param
),

anios AS (
  SELECT
    EXTRACT(YEAR FROM fecha) AS anio,
    param,
    AVG(prom_dia) AS media
  FROM dias
  GROUP BY anio, param
)

SELECT
  param,
  IF(param = 'O3', 'ppb', 'ug/m3')                                   AS unidad,
  ROUND(MAX(IF(anio = 2015, media, NULL)) * IF(param = 'O3', 1000, 1), 1) AS media_2015,
  ROUND(MAX(IF(anio = 2024, media, NULL)) * IF(param = 'O3', 1000, 1), 1) AS media_2024,
  ROUND(
    100.0 * (MAX(IF(anio = 2024, media, NULL)) - MAX(IF(anio = 2015, media, NULL)))
    / MAX(IF(anio = 2015, media, NULL)),
    1
  ) AS pct_cambio
FROM anios
GROUP BY param
ORDER BY param;

-- ------------------------------------------------------------
-- 2D · Panel fijo: solo estaciones que midieron el contaminante en 2015
--      Y en 2024 con al menos min_dias días. Media anual = promedio de
--      las medias anuales por estación (cada estación pesa igual).
--      min_dias = 183 (la mitad del año): con 274 días (75 %) solo
--      quedarían 2 estaciones de PM2.5 (outputs/02_tendencia_anualb.csv).
--      Ejecutada (2026-10-25): resultados en outputs/02_tendencia_anuald.csv.
-- ------------------------------------------------------------
WITH config AS (
  SELECT 183 AS min_dias
),

diaria_est AS (
  SELECT
    estacion,
    param,
    fecha,
    AVG(valor) AS media_dia
  FROM `aire-monterrey-bq.sima.sima_horarios`
  WHERE validado = 1
    AND param IN ('PM2.5', 'O3')
    AND EXTRACT(YEAR FROM fecha) IN (2015, 2024)
  GROUP BY estacion, param, fecha
),

anual_est AS (
  SELECT
    estacion,
    param,
    EXTRACT(YEAR FROM fecha) AS anio,
    COUNT(*)                 AS dias_con_datos,
    AVG(media_dia)           AS media_anual_est
  FROM diaria_est
  GROUP BY estacion, param, anio
),

panel AS (
  SELECT a.estacion, a.param
  FROM anual_est a
  CROSS JOIN config c
  WHERE a.dias_con_datos >= c.min_dias
  GROUP BY a.estacion, a.param
  HAVING COUNT(DISTINCT a.anio) = 2
),

anual_panel AS (
  SELECT
    a.param,
    a.anio,
    COUNT(*)                                   AS estaciones,
    STRING_AGG(a.estacion, ',' ORDER BY a.estacion) AS lista_estaciones,
    AVG(a.media_anual_est)                     AS media_panel
  FROM anual_est a
  JOIN panel p
    ON a.estacion = p.estacion
   AND a.param = p.param
  GROUP BY a.param, a.anio
)

SELECT
  param,
  IF(param = 'O3', 'ppb', 'ug/m3')                                         AS unidad,
  MAX(estaciones)                                                          AS estaciones_panel,
  MAX(lista_estaciones)                                                    AS lista_estaciones,
  ROUND(MAX(IF(anio = 2015, media_panel, NULL)) * IF(param = 'O3', 1000, 1), 1) AS media_2015,
  ROUND(MAX(IF(anio = 2024, media_panel, NULL)) * IF(param = 'O3', 1000, 1), 1) AS media_2024,
  ROUND(
    100.0 * (MAX(IF(anio = 2024, media_panel, NULL)) - MAX(IF(anio = 2015, media_panel, NULL)))
    / MAX(IF(anio = 2015, media_panel, NULL)),
    1
  ) AS pct_cambio
FROM anual_panel
GROUP BY param
ORDER BY param;
