# Resultados del análisis · PM2.5 y O3, AMM 2015-2024

Fuente: 1,516,017 horas validadas (3,360 descargas de la API SINAICA/INECC · 15 estaciones).
CSV crudos en `outputs/` (regenerables con `src/analysis/run_queries.py`).

---

## 1. ¿Mejoró Monterrey de 2015 a 2024?

**Depende del contaminante — y las respuestas son contrapuestas:**

| Contaminante | 2015 | 2024 | Cambio | ¿Mejoró? |
|---|---|---|---|---|
| **PM2.5** (µg/m³) | 26.1 | 20.8 | **−20.0 %** | ✅ Sí — pero sigue **2× la norma anual** (10 µg/m³) |
| **O3** (ppm media) | 0.022 | 0.028 | **+27.3 %** | ❌ No — empeoró |

- PM2.5: mejora sostenida desde 2017 con meseta ~20-21 µg/m³. Mejor año: 2023 (19.8).
- O3: alza sostenida 2017-2024, y los días con niveles "contingencia probable" crecen:
  **4 (2015) → 20 (2024)**; días sobre norma 73 → 121 al año.
- ⚠️ *Cuidado de lectura:* la media anual depende de la composición de la red — entre 2015
  y 2024 cambiaron las estaciones disponibles (Cadereyta/UANL/ITESM 2017, Pesquería 2020,
  Misión San Juan 2022). La cobertura por estación-año está en `outputs/02b.csv` para auditar
  cuánto del indicador cambia por composición y cuánto por aire real.

## 2. ¿Qué estación respira peor?

**PM2.5 (media 2015-2024, µg/m³ · % días sobre norma 41):**

| # | Estación | Media | % días sobre norma |
|---|---|---|---|
| 1 | **Juárez (SE2)** | 26.0 | 14.3 |
| 2 | Santa Catarina (SO) | 25.5 | 10.6 |
| 3 | Apodaca (NE2) | 24.5 | 6.9 |

**O3 (media ppm · horas sobre norma 0.090):**

| # | Estación | Media | Horas sobre norma |
|---|---|---|---|
| 1 | San Bernabé (NO) | 0.028 | 531 |
| 2 | ITESM SUR | 0.028 | 341 |
| 3 | García (NO2) | 0.027 | 715 |

- En PM2.5 domina el suroriente (Juárez/Cadereyta) — industria, tráfico pesado y
  contribución regional; en O3 dominan las estaciones del norte y del poniente alto.
- **El cambio por décadas (outputs/03c.csv) es más interesante:** Juárez
  **empeoró +36.8 %** en PM2.5 entre 2015-2019 y 2020-2024 (y la ITESM
  Eugenio Garza +17.3 %, Obispado +9.2 %; Santa Catarina plana +0.5 %).
  Las otras **9 de 13 estaciones con datos completos mejoraron**, y los ya
  contaminados bajaron más: Apodaca (NE2) −18.1 %, San Bernabé (NO) −17.6 %,
  UANL (N2) −17.3 %, García (NO2) −27.2 %. La historia es de convergencia
  con una excepción: el sureste (Juárez) se despega y aún sube.

## 3. Contingencias y el peor día del decenio

- **1 de enero de 2019**: promedio red de **128.8 µg/m³** y peor estación con
  **313.6 µg/m³** — episodios de pirotecnia/fuegos de fin de año con inversión térmica
  nocturna; el evento más severo del decenio por márgenes muy superiores a los demás
  días del calendario (ver `outputs/04b.csv`).
- 2024 cerró con **20 días** con niveles O3 de contingencia probable (récord del período)
  y **13 días** de PM2.5 sobre norma.

## Heatmaps

- `outputs/heatmap_pm25_{2015,2024,decenio}.html` — la mancha térmica sobre el mapa real:
  en 2015 solo 7 estaciones con datos de PM2.5 reportando; en 2024, la red completa.
- `outputs/heatmap_o3_{2015,2024,decenio}.html` — 15 estaciones para O3 en el decenio.

## Limitaciones declaradas

1. **Outliers:** PM2.5 con máximos de 991 µg/m³ y mínimos de −1 en varios años — son
   episodios/glitches instrumentales; el análisis diario (media 24h) los absorbe parcial-
   mente. Criterio EPA de enmascaramiento por evento, pendiente para la v2.
2. **Composición de red cambiante** entre años (ver sección 1).
3. O3 estacional: los picos se concentran en primavera; el patrón horario del `sql/05`
   se espera en el dashboard con ese anualización.
