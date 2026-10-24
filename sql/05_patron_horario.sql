-- ============================================================
-- 05 · Patrón horario y estacional de la contaminación
--  (la "radiografía" que saca a Monterrey de la simple pantalla)
-- ============================================================
-- Útil para el dashboard: respuesta a "¿cuándo respira la ciudad, por hora
-- y por mes?" — transportes, temperatura, inversión térmica invernal.

SELECT
  param,
  hora,                                                       -- 0-23 local Monterrey
  EXTRACT(MONTH FROM fecha)            AS mes,                -- 1-12
  ROUND(AVG(valor), 3)                 AS media_valor,
  COUNT(*)                             AS horas_validas
FROM `aire-mty.sima.sima_horarios`
WHERE validado = 1
  AND param IN ('PM2.5', 'O3')
GROUP BY param, hora, mes
ORDER BY param, mes, hora;

-- Lectura esperada:
--  · O3: pico vespertino (13-17 h) todo el año, más severo mar-jul; NO2 noct...
--    O3 sube con sol y tráficos — el patrón debe dormir por la noche.
--  · PM2.5: máximos por la MADRUGADA (00-07) y primavera/invierno —
--    inversión térmica nocturna + fugas sinterizas + polvo de rancho.
