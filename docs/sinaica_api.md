# Documentación de la API SINAICA/INECC (descubierta por ingeniería inversa del frontend)

Fuente: <https://sinaica.inecc.gob.mx> — portal oficial del Sistema Nacional de Información de Calidad del Aire.
Todos los endpoints aceptan `POST` con `application/x-www-form-urlencoded` y responden JSON.

## 1. Metadatos de estaciones: `infoEstacion`

```
POST /lib/libd/cnxn.php
metodo=infoEstacion&estacionId=<id>&json=true
```

Devuelve metadatos completos: `lat`, `long`, `elevacion`, `munc`, `edo`, dirección,
`fechaIniDatos` (inicio de serie), `fechaUltValidacion`.

## 2. Datos horarios: `getDatos`

```
POST /lib/libd/cnxn.php
metodo=getDatos
estacionesId=<id estación>
fechaInit=<YYYY-MM-DD>&fechaFin=<YYYY-MM-DD>
paramId=<O3|PM2.5|PM10|NO2|SO2|CO>
campos=2
limit=1
inc=1
soloVal=1
soloValidados=1
```

Respuesta (array):

```json
[{"id":"148O315010409","fecha":"2015-01-04","hora":9,"valor":0.02,"bandO":null,"val":1}]
```

- `valor`: O3/NO2/SO2/CO en **ppm**; PM10 y PM2.5 en **µg/m³**
- `val=1` → dato validado oficialmente por INECC
- Dias con `<24` filas = horas sin medición (huecos reales de la red)
- Limitado a **1000 filas** por respuesta → hacen falta bloques por mes (≈744 filas/mes máx.)

## Estaciones de la red Monterrey (redId=72)

Ver `docs/stations.csv` (generado con `infoEstacion`). 15 estaciones activas;
Pesquería (2020) y Misión San Juan (2022) empezaron tarde; Cadereyta/UANL/ITESM desde 2017.

## Notas de uso

- Uso responsable: 1 hilo, *delay* entre peticiones, cachear el resultado.
- El portal fuente es público y de acceso gratuito; los datos validados son oficiales.
- Alternativa: dataset público `bigquery-public-data.openaq` (solo datos crudos, serie incompleta para Monterrey).
