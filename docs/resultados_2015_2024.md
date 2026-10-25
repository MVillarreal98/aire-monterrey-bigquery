# Resultados del análisis · PM2.5 y O3, AMM 2015-2024

Fuente: 1,516,017 mediciones horarias validadas (estación × contaminante × hora) de 15
estaciones, obtenidas con 3,360 peticiones al endpoint de SINAICA/INECC. Los CSV de esta
corrida están commiteados en `outputs/` y se regeneran con `src/analysis/run_queries.py`
(cada archivo `sql/0N_*.sql` con varias queries produce `0N_*a.csv`, `0N_*b.csv`, …).

Las atribuciones causales de este documento son hipótesis consistentes con los datos, no
resultados medidos.

---

## 1. ¿Mejoró Monterrey de 2015 a 2024?

**Depende del contaminante, y la respuesta depende también de qué estaciones se comparan.**

Media anual de la red completa (query **2C**, `outputs/02_tendencia_anualc.csv`; mismo
indicador que `02_tendencia_anuala.csv` — nivel diario = promedio de las estaciones que
midieron ese día, nivel anual = promedio de los días —, con el % calculado sin redondeo
intermedio y el O3 en ppb):

| Contaminante | 2015 | 2024 | Cambio | Lectura |
|---|---|---|---|---|
| **PM2.5** (µg/m³) | 26.1 | 20.8 | **−20.0 %** | Bajó, pero sigue en 2× la norma anual (10 µg/m³) |
| **O3** (ppb, media) | 21.6 | 27.9 | **+29.2 %** | Subió |

Dos advertencias que cambian la lectura:

- **Composición de la red (PM2.5).** En 2015 midieron PM2.5 7 estaciones (CE, NE, NE2, NO, SE,
  SO, SO2) y en 2024 fueron 14 (`outputs/02_tendencia_anualb.csv`). Varias de las nuevas
  tienen medias bajas, y la caída grande ocurre en 2017 (de 24.97 a 20.26 µg/m³), el año en que
  entran Cadereyta (SE3), UANL (N2) e ITESM Sur (SUR), con medias decenales de 18.7, 21.4 y
  15.7. Desde 2017 la media de red queda en una meseta de 19.8 a 21.6 µg/m³ (mejor año: 2023,
  19.8).

  Con panel fijo (query **2D** de `sql/02_tendencia_anual.sql`): estaciones con 183 días o
  más medidos en ambos años —con un umbral de 75 % (274 días) solo quedarían 2—, media anual
  por estación sobre medias diarias y promedio simple de esas medias (cada estación pesa
  igual):

  | Panel | 2015 | 2024 | Cambio |
  |---|---|---|---|
  | Red completa (2C) | 26.1 | 20.8 | **−20.0 %** |
  | Panel fijo: 6 estaciones (CE, NE, NE2, SE, SO, SO2) | 25.7 | 22.1 | **−14.1 %** |

  El −20 % de la red completa arrastra el efecto de la composición; el −14.1 % del panel
  fijo es la cifra comparable. Resultados en `outputs/02_tendencia_anualc.csv` y
  `outputs/02_tendencia_anuald.csv`.

- **Precisión del O3.** El +27.3 % citado antes salía de medias ya redondeadas a 3 decimales
  (0.028 / 0.022 − 1). La query **2C** recalculó el cambio sin redondeo intermedio:
  **21.6 → 27.9 ppb, +29.2 %** con la red completa. Con el panel fijo de 8 estaciones que
  midieron O3 en ambos años (CE, N, NE, NO, NO2, SE, SE2, SO2), el alza es mayor:
  **21.8 → 29.8 ppb, +36.8 %** (`outputs/02_tendencia_anuald.csv`).

Serie del O3 (media de red, ppm): 0.022 (2015), 0.024, 0.026, 0.021 (2018), 0.028, 0.028,
0.026, 0.026, 0.027, 0.028 (2024). Es más alta en 2019-2024 que en 2015-2016, con 2018 como
excepción. No es un alza sostenida año con año.

## 2. ¿Qué estación respira peor?

**PM2.5: media 2015-2024 y % de días sobre la norma diaria de 41 µg/m³**
(`outputs/03_ranking_estacionesa.csv`):

| # | Estación | Media (µg/m³) | % días sobre norma | Días medidos |
|---|---|---|---|---|
| 1 | Juárez (SE2) | 26.0 | 14.3 | 2,118 |
| 2 | Santa Catarina (SO) | 25.5 | 10.6 | 3,163 |
| 3 | Apodaca (NE2) | 24.5 | 6.9 | 3,212 |
| 4 | Obispado, Centro (CE) | 23.4 | 7.1 | 2,879 |
| 10 | San Pedro (SO2) | 18.6 | 1.5 | 2,795 |

Respuesta a la pregunta 2 del README: entre San Pedro, Apodaca y Centro, Apodaca es la más alta
(3.ª de 14), Centro va muy cerca (4.ª) y San Pedro está entre las más bajas (10.ª). Las
estaciones no tienen el mismo número de días medidos, así que las medias decenales mezclan
periodos distintos. Misión San Juan (NO3) solo tiene 132 días.

**O3: media horaria y horas sobre la norma de 0.090 ppm** (`outputs/03_ranking_estacionesb.csv`):

| # | Estación | Media (ppm) | Horas sobre norma |
|---|---|---|---|
| 1 | San Bernabé (NO) | 0.028 | 531 |
| 2 | ITESM Sur (SUR) | 0.028 | 341 |
| 3-8 | García (NO2), Misión San Juan (NO3), Pesquería (NE3), Juárez (SE2), Obispado (CE), ITNL (SE) | 0.027 | 64 a 715 |

Las medias de O3 de todas las estaciones caen entre 0.022 y 0.028 ppm, y con 3 decimales hay
seis estaciones empatadas en 0.027. El orden dentro de ese empate no significa nada. Por
horas sobre norma, la más alta es Santa Catarina (SO), con 961.

**Cambio por estación, PM2.5, 2015-2019 vs 2020-2024** (`outputs/03_ranking_estacionesc.csv`):

| Estación | Días 2015-2019 | Media 2015-2019 | Días 2020-2024 | Media 2020-2024 | Cambio |
|---|---|---|---|---|---|
| Juárez (SE2) | 429 | 20.1 | 1,689 | 27.5 | +36.8 % |
| ITESM Sur (SUR) | 445 | 13.8 | 1,492 | 16.2 | +17.3 % |
| Obispado (CE) | 1,170 | 22.2 | 1,709 | 24.3 | +9.2 % |
| Santa Catarina (SO) | 1,394 | 25.4 | 1,769 | 25.5 | +0.5 % |
| Apodaca (NE2) | 1,534 | 27.0 | 1,678 | 22.1 | −18.1 % |
| San Bernabé (NO) | 932 | 25.1 | 1,319 | 20.7 | −17.6 % |
| UANL (N2) | 749 | 24.3 | 1,727 | 20.1 | −17.3 % |
| García (NO2) | 493 | 23.8 | 1,541 | 17.3 | −27.2 % |

- De las 13 estaciones con datos de PM2.5 en ambos periodos, 9 bajaron y 4 subieron. Las bajas
  de ITNL (SE, −1.5 %) y San Pedro (SO2, −3.6 %) son pequeñas.
- El +36.8 % de Juárez compara 429 días contra 1,689: Juárez no tiene PM2.5 en 2015 y su primer
  periodo es corto. Es la señal más fuerte del análisis, pero hace falta revisar su cobertura
  por año antes de darla por buena.
- Varias de las estaciones con media alta en 2015-2019 bajaron (Apodaca, San Bernabé, UANL,
  García), pero Santa Catarina, la segunda más alta, quedó plana. Comparar periodos de 5 años no
  es lo mismo que comparar 2015 contra 2024: San Bernabé baja entre periodos, pero su media de
  2024 (30.1, con 86 días) es mayor que la de 2015 (25.8).

## 3. Días sobre norma y peores días

Serie anual (`outputs/04_contingenciasa.csv`):

- **O3:** días en que la peor estación supera 0.090 ppm en una hora: 73 (2015) → 121 (2024).
  Días sobre 0.130 ppm: 4 → 20; los 20 de 2024 son el máximo del periodo. Los dos conteos usan el
  máximo entre estaciones, que sube solo con añadir estaciones: el salto de 2017 (95 días)
  coincide con la entrada de tres estaciones. La query **4C** lo normaliza por estación-día
  y ya se ejecutó (`outputs/04_contingenciasc.csv`): 5.2 % de los estación-días sobre norma
  en 2015 frente a 9.9 % en 2024 (máximo del periodo; los demás años van de 3.0 % a 8.9 %).
- **PM2.5:** días en que la media de la red supera 41 µg/m³: 15 (2015) y 13 (2024). Este criterio
  usa la media de la red, no la peor estación, así que no es comparable con el de O3.

Peores días de PM2.5 (`outputs/04_contingenciasb.csv`, media de red de 24 h):

- **1 de enero de 2019:** media de red de **128.8 µg/m³** con 13 estaciones; la peor estación
  marcó **313.6 µg/m³**. El segundo peor día (1-ene-2022) tiene 63.4.
- De los 10 peores días, 5 son 1 de enero y los 10 caen en diciembre o enero. Eso es consistente
  con la pirotecnia de Año Nuevo y con las inversiones térmicas de invierno; no se midió ninguna
  de las dos.
- Algunos días del top 10 tienen pocas estaciones midiendo: 1-ene-2017 con 1 y 17 y 19-dic-2017
  con 5. Su "media de red" es en realidad la media de esas pocas estaciones.

## Mapas

- `outputs/heatmap_pm25_{2015,2024,decenio}.html`: media horaria de PM2.5 por estación (7
  estaciones en 2015, 14 en 2024).
- `outputs/heatmap_o3_{2015,2024,decenio}.html`: lo mismo para O3 (10 estaciones en 2015, 15 en
  2024).
- Cada mapa se normaliza contra su propio máximo, así que los colores no se pueden comparar
  entre mapas. Compara los números de cada estación. La capa HeatMap además suma la intensidad
  de estaciones cercanas; los puntos son estaciones y el color no interpola entre ellas.
- Las capturas PNG están en `docs/img/`.

## Limitaciones declaradas

1. **Outliers:** PM2.5 tiene máximos de 991 µg/m³ y mínimos de −1 en varios años, por episodios
   o fallas del instrumento. La media diaria los diluye solo en parte. No se aplicó un criterio
   de enmascaramiento por evento.
2. **Composición de red cambiante** entre años (ver la sección 1).
3. **Sin criterio de suficiencia diaria:** un día con una sola hora válida cuenta como media
   diaria. La práctica normativa pide al menos 75 % de las horas (18 de 24).
4. **Normas:** se usan como umbral constante los valores de la NOM-025-SSA1-2021 (PM2.5: 41
   µg/m³ en 24 h —el de "año 1" de la norma gradual, en 2024-2025 rige el de año 3: 33— y
   10 µg/m³ anual) y de la NOM-020-SSA1-2021 (O3: 0.090 ppm en 1 h) para todo 2015-2024.
   Enlaces al DOF en la sección "Fuente de datos y atribución" del README. Los umbrales de
   97 µg/m³ y 0.130 ppm ("contingencia probable") los definió el autor como referencia; no
   corresponden a las declaraciones oficiales.
5. **O3 estacional:** los picos se concentran en primavera. `sql/05` calcula el patrón por hora
   y mes (`outputs/05_patron_horario.csv`).
