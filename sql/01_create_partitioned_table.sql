-- ============================================================
-- 01 · Creación de la tabla particionada de datos horarios
--  (estructura + comando de carga documentado)
-- ============================================================
-- La carga del parquet es CLI/consola, no SQL: el comando va documentado
-- al final como referencia reproducible.

-- Recrea la tabla de cero (idempotente):
-- DROP TABLE IF EXISTS `aire-mty.sima.sima_horarios`;

CREATE TABLE `aire-mty.sima.sima_horarios` (
  estacion_id INT64    NOT NULL,   -- id SINAICA de la estación
  estacion    STRING   NOT NULL,   -- código SIMA (CE, NE, SO, ...)
  param       STRING   NOT NULL,   -- O3 | PM2.5 | PM10 | NO2 | SO2 | CO
  fecha       DATE     NOT NULL,
  hora        INT64    NOT NULL,   -- 0-23, hora local de Monterrey
  valor       FLOAT64,             -- ppm (gases) o µg/m3 (partículas)
  validado    INT64    NOT NULL    -- 1 = dato validado oficialmente por INECC
)
PARTITION BY fecha
CLUSTER BY estacion, param
OPTIONS (
  partition_expiration_days = NULL,  -- histórico: retener todo
  description = 'Datos horarios validados SIMA Monterrey 2015-2024 (ingesta desde API SINAICA/INECC)'
);

-- ============================================================
--  CARGA DEL PARQUET (CLI):
--
--  bq load --source_format=PARQUET \
--      --time_partitioning_field=fecha \
--      --clustering_fields=estacion,param \
--      --replace \
--      aire-mty:sima.sima_horarios data/processed/sima_horarios.parquet
--
--  Ventajas del diseño particionado (se luce en el portafolio):
--   · PARTITION BY fecha    → cualquier query de un año escanea ~1/10 del dato
--   · CLUSTER BY estacion,param → comparativas por estación leen bloques afines
--   · millones de filas × 10 años → las queries del repo quedan en unidades de MB
-- ============================================================
