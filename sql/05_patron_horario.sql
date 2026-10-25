-- ============================================================
-- 05 · Patrón horario y estacional de la contaminación
--  Media por contaminante, hora del día y mes (todas las estaciones)
-- ============================================================
-- Alimenta el heatmap hora × mes: ¿a qué hora y en qué meses se concentra
-- cada contaminante?

SELECT
  param,
  hora,                                                       -- 0-23 local Monterrey
  EXTRACT(MONTH FROM fecha)            AS mes,                -- 1-12
  ROUND(AVG(valor), 3)                 AS media_valor,
  COUNT(*)                             AS horas_validas
FROM `aire-monterrey-bq.sima.sima_horarios`
WHERE validado = 1
  AND param IN ('PM2.5', 'O3')
GROUP BY param, hora, mes
ORDER BY param, mes, hora;

-- Hipótesis a contrastar con el resultado (no verificadas en este repo):
--  · O3: pico entre 13 y 17 h, más alto en primavera, bajo de noche
--    (el ozono se forma con radiación solar).
--  · PM2.5: máximos nocturnos y de madrugada en invierno, consistentes
--    con inversión térmica.
