-- ============================================================
-- 01 · Creación de la tabla particionada de datos horarios
--  (estructura + comando de carga documentado)
-- ============================================================
-- La carga del parquet es CLI/consola, no SQL: el comando va documentado
-- al final como referencia reproducible. La tabla publicada la creó ese
-- bq load con --replace, no este DDL; el DDL documenta el esquema buscado.

-- Recrea la tabla de cero:
-- DROP TABLE IF EXISTS `aire-monterrey-bq.sima.sima_horarios`

CREATE TABLE `aire-monterrey-bq.sima.sima_horarios` (
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
--  CARGA DEL PARQUET (CLI). Camino que se usó:
--
--  bq load --source_format=PARQUET \
--      --time_partitioning_field=fecha \
--      --clustering_fields=estacion,param \
--      --replace \
--      aire-monterrey-bq:sima.sima_horarios data/processed/sima_horarios.parquet
--
--  y justo después, en la consola de BigQuery:
--
--  ALTER TABLE `aire-monterrey-bq.sima.sima_horarios`
--    SET OPTIONS (partition_expiration_days = NULL)
--
--  --replace recrea la tabla con el esquema del parquet: ignora el DDL de
--  arriba (y sus OPTIONS) y hereda las expiraciones por defecto del
--  dataset. Sin el ALTER, las particiones 2015-2024 cuentan como vencidas
--  (incidente y verificación en docs/gcp_setup.md).
--
--  Alternativa sin probar: crear la tabla con el DDL y cargar con
--  --noreplace. Puede fallar porque el parquet declara columnas NULLABLE
--  y el DDL las declara NOT NULL.
--
--  Sobre el diseño:
--   · PARTITION BY fecha deja ~3,650 particiones de ~415 filas. Con este
--     volumen (1.5 M filas) no ahorra costo: Google recomienda particiones
--     más grandes (DATE_TRUNC(fecha, MONTH) o YEAR) o solo clustering.
--     Las queries de sql/02-05 no filtran por fecha, así que tampoco hay
--     poda de particiones. Se dejó así para practicar el patrón.
--   · CLUSTER BY estacion, param ordena los bloques para los filtros por
--     estación y contaminante que usan las queries.
--   · Los bytes procesados reales no se han medido (bq query --dry_run).
-- ============================================================
