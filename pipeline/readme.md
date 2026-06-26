# Pipeline end-to-end trazable

Esta carpeta contiene el orquestador principal del proyecto Big Data de salmonicultura.

El objetivo del pipeline es coordinar, ejecutar y registrar las etapas principales del flujo cloud del proyecto, conectando procesamiento batch, modelo en SageMaker, simulación streaming, almacenamiento de resultados y evidencia trazable.

---

## Objetivo

El pipeline permite demostrar un flujo end-to-end del proyecto:

```text
Datos históricos en S3
        ↓
Validación de insumos
        ↓
Ejecución opcional de notebooks batch
        ↓
Validación de modelo entrenado
        ↓
Empaquetado para SageMaker
        ↓
Endpoint SageMaker temporal
        ↓
Prueba de inferencia
        ↓
Simulador streaming
        ↓
Eventos + features + predicciones
        ↓
Resultados en S3
        ↓
Eliminación del endpoint
        ↓
Logs y resumen JSON
```

Este flujo busca evitar que los componentes del proyecto queden aislados. En vez de ejecutar cada parte manualmente sin trazabilidad, el pipeline registra cada etapa, sus resultados y las rutas de evidencia generadas.

---

## Estructura del módulo

```text
pipeline/
    __init__.py
    config.py
    command_runner.py
    aws_checks.py
    steps.py
    summary.py
    run_end_to_end_pipeline.py
    README.md
```

---

## Rol de cada archivo

```text
config.py
    Define constantes del proyecto, como bucket S3, rutas RAW, processed,
    modelo, métricas y notebooks batch.

command_runner.py
    Contiene utilidades para ejecutar comandos externos y registrar logs.

aws_checks.py
    Contiene validaciones AWS y S3:
    identidad activa, existencia de objetos y existencia de prefijos.

steps.py
    Contiene los pasos ejecutables del pipeline:
    notebooks, SageMaker, endpoint, simulador y limpieza.

summary.py
    Genera el resumen JSON de la corrida y sube evidencias a S3.

run_end_to_end_pipeline.py
    Es el orquestador principal. Coordina todos los pasos anteriores.
```

---

## Requisitos previos

El pipeline debe ejecutarse desde un entorno AWS con permisos sobre S3 y SageMaker.

En la implementación del proyecto, la ejecución se realiza desde JupyterLab en AWS usando el rol del laboratorio:

```text
arn:aws:sts::601270941236:assumed-role/LabRole/SageMaker
```

También se requiere que existan previamente las rutas base del proyecto en S3:

```text
s3://bigdata-salmonicultura-fabian/raw/productive_data/productive_data.csv
s3://bigdata-salmonicultura-fabian/processed/productive_kpi/
s3://bigdata-salmonicultura-fabian/models/low_growth_logistic_model.joblib
s3://bigdata-salmonicultura-fabian/models/low_growth_model_metrics.json
```

---

## Ejecución recomendada

La ejecución recomendada durante pruebas o demostración es saltando notebooks, cuando ya existen los artefactos batch en S3:

```bash
python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 30 \
  --interval-seconds 1
```

Esta ejecución valida el flujo cloud desde el modelo ya existente:

```text
Validación S3
        ↓
Empaquetado SageMaker
        ↓
Endpoint temporal
        ↓
Prueba de inferencia
        ↓
Simulador streaming
        ↓
Resultados en S3
        ↓
Eliminación de endpoint
        ↓
Evidencias del pipeline
```

---

## Ejecución completa

Para ejecutar también los notebooks batch:

```bash
python -m pipeline.run_end_to_end_pipeline \
  --events 30 \
  --interval-seconds 1
```

Esta modalidad ejecuta los notebooks configurados en `pipeline/config.py`:

```text
notebook/pipeline_batch_salmonicultura01.ipynb
notebook/pipeline_batch_salmonicultura02.ipynb
notebook/pipeline_batch_salmonicultura03.ipynb
```

Los notebooks ejecutados quedan como evidencia local dentro de la carpeta de corrida.

---

## Ejecución para demo con Grafana

Para una demostración con actualización incremental de datos, se puede ejecutar:

```bash
python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 100 \
  --interval-seconds 2 \
  --streaming-upload-every 10
```

Esto genera eventos cada 2 segundos y sube los archivos de resultados a S3 cada 10 eventos.

La salida S3 queda disponible en:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_YYYYMMDD_HHMMSS/
```

Esta ruta puede ser utilizada como fuente para la etapa de visualización en Grafana.

---

## Parámetros principales

```text
--bucket
    Bucket S3 del proyecto.
    Valor por defecto: bigdata-salmonicultura-fabian

--events
    Cantidad de eventos simulados que generará el simulador streaming.

--interval-seconds
    Tiempo de espera entre eventos simulados.

--notebook-timeout
    Timeout para ejecución de notebooks con nbconvert.
    Valor por defecto: -1, sin límite.

--skip-notebooks
    Omite la ejecución de notebooks batch.
    Útil cuando los datos procesados y el modelo ya existen en S3.

--keep-endpoint
    Mantiene el endpoint SageMaker activo al terminar.
    No se recomienda para entrega ni pruebas normales.

--streaming-upload-every
    Sube resultados parciales del simulador a S3 cada N eventos.
    Si el valor es 0, solo sube al finalizar la simulación.
```

---

## Salidas locales

Cada ejecución genera una carpeta local:

```text
outputs/runs/run_YYYYMMDD_HHMMSS/
```

Dentro de esa carpeta se generan:

```text
pipeline.log
run_summary.json
```

Si se ejecutan notebooks, también se genera:

```text
notebooks_executed/
```

---

## Salidas en S3

El pipeline sube sus evidencias a:

```text
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_YYYYMMDD_HHMMSS/
```

Archivos esperados:

```text
pipeline.log
run_summary.json
```

Además, el simulador streaming sube resultados a:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_YYYYMMDD_HHMMSS/
```

Archivos esperados:

```text
inference_events.csv
inference_events.jsonl
```

---

## Evidencia generada por el resumen JSON

El archivo `run_summary.json` registra información estructurada de la corrida:

```text
run_id
started_at
finished_at
status
bucket
events_requested
interval_seconds
streaming_upload_every
skip_notebooks
endpoint_name
s3_checks
s3_checks_after_batch
executed_notebooks
streaming_s3_paths
pipeline_artifacts_s3
error
aws_identity
```

Este resumen permite revisar rápidamente si la ejecución fue correcta y qué rutas S3 fueron generadas.

---

## Limpieza de recursos

El pipeline crea un endpoint SageMaker temporal.

Por defecto, el endpoint se elimina automáticamente al finalizar la ejecución:

```text
Endpoint
EndpointConfig
Modelo SageMaker temporal
```

Al final también se valida que no queden endpoints activos con nombre relacionado a:

```text
low-growth-endpoint
```

El parámetro `--keep-endpoint` solo debe utilizarse para depuración controlada.

---

## Ejecución validada

Se validó una ejecución corta del pipeline usando:

```bash
python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 5 \
  --interval-seconds 1
```

Resultado de la corrida:

```text
Run ID: run_20260626_220304
Estado: success
Eventos solicitados: 5
Endpoint temporal: low-growth-endpoint-1782511389
Endpoint eliminado al finalizar: sí
```

Evidencias del pipeline:

```text
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_20260626_220304/pipeline.log
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_20260626_220304/run_summary.json
```

Resultados streaming generados:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_220619/inference_events.csv
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_220619/inference_events.jsonl
```

Validación final:

```json
{
  "Endpoints": []
}
```

---

## Consideraciones de costo

El endpoint SageMaker consume recursos mientras está activo.

Por eso, el pipeline está diseñado para:

```text
crear endpoint
        ↓
usar endpoint durante la prueba
        ↓
eliminar endpoint automáticamente
```

Esto permite demostrar inferencia en línea sin dejar servicios activos innecesariamente.

---

## Rol en la entrega final

Este pipeline actúa como evidencia central del proyecto porque conecta las piezas principales:

```text
batch
modelo
SageMaker
streaming
S3
trazabilidad
Grafana
```

La etapa de Grafana debe utilizar las salidas del simulador streaming, preferentemente las generadas por este pipeline, para visualizar métricas operacionales y predicciones del modelo.
