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
$env:Path += ";C:\Users\miket\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
```

## Costo

- **Sandbox gratuito**: 1 TB de consultas/mes + 10 GB de almacenamiento.
- El parquet (~10 años × 15 estaciones) cabrá con sobra; las queries del repo
  quedan en decenas de MB por partición escaneada — no hay costo HTTP.
