````markdown
# Big Data Salmonicultura AWS

Proyecto académico de Big Data aplicado a datos productivos históricos de centros de cultivo salmonero.

El proyecto implementa un flujo cloud en AWS que integra procesamiento batch, almacenamiento en S3, transformación de datos, analítica predictiva, despliegue de modelo en SageMaker, simulación de datos operacionales, inferencia streaming y trazabilidad end-to-end.

La versión inicial del proyecto fue construida como una adaptación AWS de una evaluación originalmente orientada a Google Cloud Platform. Posteriormente, el proyecto fue extendido para incorporar ejecución en JupyterLab AWS, modelo online en SageMaker, simulador operacional y pipeline automatizado de demostración.

---

## Objetivo

El objetivo del proyecto es demostrar un flujo Big Data de extremo a extremo para salmonicultura, conectando datos históricos, procesamiento batch, modelo predictivo, inferencia operacional y visualización.

El flujo busca responder a una necesidad analítica del dominio: procesar información productiva semanal, calcular indicadores relevantes y estimar riesgo de bajo crecimiento en centros o unidades productivas.

El proyecto no se limita a notebooks aislados. También incorpora componentes ejecutables y trazables para demostrar el comportamiento del sistema en un ambiente cloud.

---

## Arquitectura general

El flujo general del proyecto es el siguiente:

```text
Dataset productivo histórico
        ↓
Amazon S3 - Zona RAW
        ↓
Athena / Glue Data Catalog - Tabla RAW
        ↓
JupyterLab AWS
        ↓
PySpark - Limpieza y transformación batch
        ↓
Amazon S3 - Zona processed en Parquet
        ↓
Athena / Glue Data Catalog - Capa analítica
        ↓
Dataset ML + entrenamiento del modelo
        ↓
Modelo joblib en S3
        ↓
Empaquetado para SageMaker
        ↓
Endpoint SageMaker temporal
        ↓
Simulador streaming
        ↓
Eventos + features + predicciones
        ↓
Resultados en S3
        ↓
Pipeline end-to-end con logs y resumen JSON
        ↓
Dashboard / visualización
```

---

## Componentes principales

| Componente | Herramienta / Servicio |
|---|---|
| Almacenamiento cloud | Amazon S3 |
| Zona RAW | Amazon S3 |
| Catálogo y consultas SQL | Athena + Glue Data Catalog |
| Procesamiento batch | PySpark |
| Ambiente de ejecución cloud | JupyterLab en AWS |
| Capa processed | Amazon S3 en formato Parquet |
| Analítica predictiva | Python + scikit-learn |
| Modelo serializado | joblib |
| Modelo online | AWS SageMaker |
| Inferencia operacional | SageMaker Runtime |
| Simulación streaming | Script Python |
| Trazabilidad | Pipeline modular + logs + JSON |
| Visualización inicial | Looker Studio |
| Visualización operacional | Grafana, en desarrollo |
| Control de versiones | Git + GitHub |

---

## Dashboard inicial

Dashboard KPI construido en Looker Studio:

[Ver Dashboard KPI](https://datastudio.google.com/s/s_DCOggeXLU)

Este dashboard corresponde a la primera etapa analítica del proyecto, basada en resultados batch y archivos preparados para visualización.

La etapa posterior incorpora una visualización operacional en Grafana usando resultados generados por el simulador streaming.

---

## Notebooks del proyecto

Los notebooks se encuentran en la carpeta `notebook/`.

| Notebook | Descripción |
|---|---|
| [`pipeline_batch_salmonicultura01.ipynb`](notebook/pipeline_batch_salmonicultura01.ipynb) | Definición del caso, ingesta del dataset en S3, validación de carga y creación de tabla RAW en Athena. |
| [`pipeline_batch_salmonicultura02.ipynb`](notebook/pipeline_batch_salmonicultura02.ipynb) | Transformación batch con PySpark, limpieza de datos, conversión de tipos, validaciones e indicadores productivos. |
| [`pipeline_batch_salmonicultura03.ipynb`](notebook/pipeline_batch_salmonicultura03.ipynb) | Creación de capa analítica, consultas KPI, preparación de datasets ML, entrenamiento del modelo y almacenamiento de predicciones. |

Los notebooks fueron ejecutados en JupyterLab dentro de AWS, validando acceso a S3, procesamiento batch y generación de artefactos del proyecto.

---

## Modelo predictivo

El proyecto utiliza un modelo de clasificación para estimar eventos asociados a bajo crecimiento productivo.

El modelo trabaja con features derivadas de los datos productivos, entre ellas:

```text
feed_per_open_biomass
feed_per_fish
temperature_avg
density_avg
mortality_rate
open_biomass
```

Artefactos principales del modelo:

```text
s3://bigdata-salmonicultura-fabian/models/low_growth_logistic_model.joblib
s3://bigdata-salmonicultura-fabian/models/low_growth_model_metrics.json
```

Métricas registradas del modelo:

```text
accuracy: 0.8520725407267041
precision: 0.8564256584662043
recall: 0.8436693255982596
f1_score: 0.8499996346978586
```

---

## SageMaker

El modelo entrenado se empaqueta como artefacto compatible con SageMaker:

```text
s3://bigdata-salmonicultura-fabian/sagemaker/model-artifacts/low_growth_model.tar.gz
```

La implementación considera scripts para:

```text
sagemaker/package_model.py
sagemaker/deploy_endpoint.py
sagemaker/test_endpoint.py
sagemaker/delete_endpoint.py
```

El endpoint se crea temporalmente para ejecutar inferencia online y luego se elimina para evitar costos innecesarios.

Ejemplo de respuesta validada del endpoint:

```json
{
  "predictions": [0],
  "probabilities": [0.01267890500889963]
}
```

---

## Simulador streaming

El proyecto incluye un simulador de eventos operacionales en:

```text
streaming/simulate_streaming_inference.py
```

El simulador genera eventos compatibles con el dominio productivo salmonero, calcula las features requeridas por el modelo y envía solicitudes de inferencia al endpoint SageMaker.

El simulador incorpora escenarios operacionales:

```text
normal
risk
```

Los resultados se guardan localmente y también pueden subirse a S3 en formato CSV y JSONL.

Ejemplo de ruta generada:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_YYYYMMDD_HHMMSS/inference_events.csv
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_YYYYMMDD_HHMMSS/inference_events.jsonl
```

También se incorporó subida incremental de resultados, útil para una demostración posterior con Grafana.

---

## Pipeline end-to-end

El proyecto incorpora un pipeline modular en la carpeta:

```text
pipeline/
```

Este pipeline coordina el flujo principal del proyecto y deja evidencia trazable de cada etapa.

Componentes del pipeline:

```text
pipeline/config.py
pipeline/command_runner.py
pipeline/aws_checks.py
pipeline/steps.py
pipeline/summary.py
pipeline/run_end_to_end_pipeline.py
```

El pipeline permite:

```text
validar identidad AWS
validar rutas base en S3
ejecutar opcionalmente notebooks batch
empaquetar el modelo para SageMaker
crear endpoint SageMaker temporal
probar inferencia online
ejecutar simulador streaming
subir resultados a S3
eliminar endpoint temporal
validar que no queden endpoints activos
generar pipeline.log
generar run_summary.json
subir evidencia a S3
```

Evidencias generadas por cada corrida:

```text
outputs/runs/run_YYYYMMDD_HHMMSS/pipeline.log
outputs/runs/run_YYYYMMDD_HHMMSS/run_summary.json
```

Evidencias subidas a S3:

```text
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_YYYYMMDD_HHMMSS/pipeline.log
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_YYYYMMDD_HHMMSS/run_summary.json
```

---

## Evidencia de ejecución validada

Se validó una ejecución end-to-end en AWS con subida incremental para demo Grafana.

Comando ejecutado:

```bash
python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 10 \
  --interval-seconds 1 \
  --streaming-upload-every 5
```

Resultado:

```text
Run pipeline: run_20260626_223955
Run streaming: run_20260626_224307
Eventos simulados: 10
Eventos con bajo crecimiento: 4
Probabilidad promedio bajo crecimiento: 0.3327
Escenarios: 6 normal, 4 risk
Endpoint temporal: low-growth-endpoint-1782513601
Estado final SageMaker: sin endpoints activos
```

Rutas generadas:

```text
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_20260626_223955/pipeline.log
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_20260626_223955/run_summary.json

s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_224307/inference_events.csv
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_224307/inference_events.jsonl
```

La validación final confirmó que no quedaron endpoints activos:

```json
{
  "Endpoints": []
}
```

---

````markdown
## Grafana

Se inició una feature para visualización operacional con Grafana.

La arquitectura objetivo para esta etapa es:

```text
S3 streaming results
        ↓
sync_streaming_to_sqlite.py
        ↓
SQLite generado en el ambiente AWS
        ↓
Grafana Docker
        ↓
Dashboard operacional
````

Componentes creados hasta el momento:

```text
grafana/
grafana_sync/
data/grafana/
```

El sincronizador:

```text
grafana_sync/sync_streaming_to_sqlite.py
```

permite descargar resultados streaming desde S3 y cargarlos en una base SQLite para ser consumida posteriormente por Grafana.

Prueba validada del sincronizador:

```text
Registros cargados: 10
Eventos con bajo crecimiento: 4
Probabilidad promedio bajo crecimiento: 0.3327
Eventos por escenario:
normal: 6
risk: 4
```

Estado actual:

```text
[~] Estructura base de Grafana creada.
[~] Sincronizador hacia SQLite validado.
[~] Contenedor Grafana probado localmente.
[ ] Dashboard final pendiente.
[ ] Ejecución y validación final en AWS pendiente.
[ ] Evidencia visual del dashboard pendiente.
```

Por lo tanto, Grafana se considera una etapa en progreso y no una funcionalidad final cerrada.

```
```

```

---

## Estructura del proyecto

```text
dashboard/
    Archivos CSV resumidos usados como fuente en Looker Studio.

data/
    Datos locales de apoyo.
    No representa la fuente cloud oficial del proyecto.

docs/
    Documentación técnica y evidencias del proyecto.

grafana/
    Configuración de Grafana, provisioning y dashboards.

grafana_sync/
    Script para sincronizar resultados streaming hacia SQLite.

models/
    Métricas o artefactos generados por la etapa predictiva.

notebook/
    Notebooks batch del proyecto.

outputs/
    Salidas locales generadas durante pruebas.
    No deben considerarse fuente oficial ni subirse completas al repositorio.

pipeline/
    Orquestador end-to-end trazable.

sagemaker/
    Scripts de empaquetado, despliegue, prueba y eliminación de endpoint SageMaker.

screenshots/
    Evidencias visuales del desarrollo, AWS y dashboard.

streaming/
    Simulador de eventos operacionales e inferencia contra SageMaker.
```

---

## Variables de entorno

El proyecto usa un archivo `.env` para credenciales temporales del laboratorio AWS y rutas principales.

Por seguridad, el archivo `.env` real no debe subirse al repositorio.

Se incluye un archivo de ejemplo:

```text
.env.example
```

Para ejecutar notebooks o scripts que requieran AWS, se debe crear un archivo `.env` propio basado en `.env.example` y completar las credenciales temporales del laboratorio AWS cuando corresponda.

En AWS JupyterLab, los permisos también pueden provenir del rol asociado a la instancia.

---

## Rutas S3 principales

```text
RAW:
s3://bigdata-salmonicultura-fabian/raw/productive_data/productive_data.csv

Processed:
s3://bigdata-salmonicultura-fabian/processed/productive_kpi/

Modelo:
s3://bigdata-salmonicultura-fabian/models/low_growth_logistic_model.joblib

Métricas:
s3://bigdata-salmonicultura-fabian/models/low_growth_model_metrics.json

Predicciones:
s3://bigdata-salmonicultura-fabian/exports/ml_predictions/ml_predictions_low_growth.csv

Artefacto SageMaker:
s3://bigdata-salmonicultura-fabian/sagemaker/model-artifacts/low_growth_model.tar.gz

Resultados streaming:
s3://bigdata-salmonicultura-fabian/streaming/inference_events/

Evidencias del pipeline:
s3://bigdata-salmonicultura-fabian/pipeline_runs/
```

---

## Limitaciones

El dataset utilizado corresponde a información productiva histórica semanal y no representa por sí solo un caso Big Data completo en volumen, velocidad y variedad.

El planteamiento original consideraba una arquitectura más cercana a alimentación automatizada, sensores y video submarino. En esta versión se trabajó con los datos disponibles, usando variables productivas históricas y `Feed Weight` como aproximación a información de alimentación.

La capa streaming corresponde a una simulación operacional. No recibe datos reales desde sensores o sistemas productivos en tiempo real, pero permite demostrar el flujo de inferencia online, generación de eventos, predicción y trazabilidad.

Grafana se encuentra incorporado como base técnica de visualización operacional, con sincronización hacia SQLite y datasource validado. El dashboard final aún debe ser versionado.

---

## Resultado

El proyecto permite demostrar un flujo cloud ampliado:

```text
S3 RAW
    ↓
Athena / Glue
    ↓
JupyterLab AWS
    ↓
PySpark batch
    ↓
S3 processed
    ↓
Modelo predictivo
    ↓
SageMaker endpoint
    ↓
Simulación streaming
    ↓
Predicciones
    ↓
S3 streaming results
    ↓
Pipeline trazable
    ↓
Visualización
```

Aunque se trata de una implementación académica y acotada, el trabajo valida una arquitectura extensible para incorporar mayor volumen de datos, sensores, eventos de alimentación, monitoreo operacional y modelos predictivos más robustos.

---

## Estado general

```text
[x] Procesamiento batch en AWS JupyterLab.
[x] Almacenamiento RAW y processed en S3.
[x] Capa analítica con Athena / Glue.
[x] Modelo predictivo entrenado y almacenado.
[x] Modelo empaquetado para SageMaker.
[x] Endpoint SageMaker probado.
[x] Simulador streaming implementado.
[x] Inferencia streaming contra SageMaker validada.
[x] Pipeline end-to-end trazable implementado.
[x] Logs y resumen JSON generados.
[x] Resultados streaming almacenados en S3.
[~] Base técnica de Grafana validada.
[ ] Dashboard Grafana final pendiente.
[ ] Documentación final de entrega pendiente.
```

-
## Ejecución del pipeline en AWS

Desde JupyterLab en AWS, ejecutar:

```bash
cd ~/bigdata-salmonicultura-aws

python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 10 \
  --interval-seconds 1 \
  --streaming-upload-every 5
```
````
