# Setup GCP/BigQuery (reproducible)

Proyecto: `aire-monterrey-bq` — dataset `sima`, location `US`.

## Pasos que se ejecutaron

```bash
# 1. Instalar SDK (Windows)
winget install --id Google.CloudSDK

# 2. Autenticar cuenta (abre navegador)
gcloud auth login

# 3. Crear proyecto + activar BigQuery API
gcloud projects create aire-monterrey-bq --name="Aire Monterrey"
gcloud services enable bigquery.googleapis.com --project aire-monterrey-bq
gcloud config set project aire-monterrey-bq

# 4. Credenciales para la librería de Python (ADC, abre navegador)
gcloud auth application-default login

# 5. Crear el dataset
bq mk --dataset --location=US aire-monterrey-bq:sima
```

## Nota Windows

Si `bq` falla con *"Error retrieving auth credentials"* es porque no encuentra
`gcloud.cmd` en el PATH. Solución rápida por sesión:

```powershell
$env:Path += ";$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
```

## Gotcha documentado (vector de pérdida de datos)

Un `bq load --time_partitioning_field=fecha --replace` puede **heredar una expiración
de partición de 60 días** aunque nadie la haya pedido: el job reporta SUCCESS y 1.5M
`outputRows`, pero las particiones 2015-2024 cuentan como ya vencidas (QUERY devuelve
0 filas) y el reaper físico puede borrarlas. Si la expiración se anula con
`ALTER TABLE ... SET OPTIONS (partition_expiration_days = NULL)` **antes** de que
el reaper actúe, los datos reviven. Después, no. Verificación:

```bash
bq show aire-monterrey-bq:sima.sima_horarios   # ¿expirationMs? ¿Total Rows?
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`aire-monterrey-bq.sima.sima_horarios\`"
```

Causa probable: un dataset en el **sandbox de BigQuery** (proyecto sin facturación)
aplica por defecto una expiración de 60 días a tablas y particiones, y `--replace`
recrea la tabla con esos valores por defecto.

### Pendiente: confirmar que el dashboard no se quede sin datos

El dashboard de Looker Studio lee esta tabla en vivo. Si el proyecto sigue en el
sandbox, la tabla o el dataset pueden expirar aunque las particiones ya no lo hagan.
Revisar:

```bash
bq show --format=prettyjson aire-monterrey-bq:sima                 # defaultTableExpirationMs, defaultPartitionExpirationMs
bq show --format=prettyjson aire-monterrey-bq:sima.sima_horarios   # expirationTime, timePartitioning.expirationMs
```

**Verificado el 25/10/2026 con esos comandos:** el dataset `sima` sigue con los
defaults del sandbox armados (`defaultTableExpirationMs` y `defaultPartitionExpirationMs`
= 5,184,000,000 ms = 60 días). La tabla `sima_horarios` NO tiene `expirationTime` ni
`timePartitioning.expirationMs` (el `ALTER TABLE` posterior a la carga anuló la
expiración heredada) y conserva las 1,516,017 filas; se consultaron particiones de
2015-01-01, 2019-06-15 y 2024-12-31 y las tres devolvieron filas. El dashboard tiene
datos hoy y sin fecha de expiración; el riesgo restante es que una recarga futura con
`bq load --replace` volvería a heredar los defaults de 60 días del dataset.

Opciones, a decidir:

1. Activar la facturación (con una alerta de presupuesto) y quitar las expiraciones:
   `bq update --default_table_expiration 0 --default_partition_expiration 0 aire-monterrey-bq:sima`
   y `bq update --expiration 0 aire-monterrey-bq:sima.sima_horarios`.
2. Seguir en el sandbox y conectar el dashboard a una fuente que no expire (por
   ejemplo, una hoja de Google Sheets con los CSV agregados de `outputs/`).

En cualquier caso, conviene guardar capturas del dashboard en `docs/img/` para que la
evidencia no dependa de la tabla.

## Costo

- **Sandbox gratuito**: 1 TB de consultas al mes y 10 GB de almacenamiento.
- Medido con `bq query --dry_run` (25/10/2026): la serie anual completa (2A) procesa
  44.6 MB; con filtro de un solo año, 6.3 MB. La tabla (1.5 M filas) cabe con holgura.
- Con "owner credentials", cada visita al dashboard ejecuta consultas a cargo del
  proyecto. Con este volumen el costo esperado es mínimo, pero conviene una alerta de
  presupuesto si se activa la facturación.
