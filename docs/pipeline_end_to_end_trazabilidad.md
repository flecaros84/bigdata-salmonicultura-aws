# Pipeline end-to-end y trazabilidad AWS

## 1. Propósito del documento

Este documento registra la implementación y validación del pipeline end-to-end del proyecto Big Data de salmonicultura.

El objetivo es dejar evidencia técnica de que el proyecto puede ejecutar un flujo integrado en AWS, conectando almacenamiento S3, modelo entrenado, despliegue temporal en SageMaker, inferencia streaming simulada, carga de resultados a S3 y limpieza de recursos.

## 2. Alcance de la feature

La feature `pipeline-end-to-end-trazabilidad` incorpora un orquestador modular para ejecutar y registrar el flujo principal del proyecto.

El pipeline permite:

- validar identidad AWS;
- validar insumos y artefactos en S3;
- ejecutar opcionalmente notebooks batch;
- empaquetar el modelo para SageMaker;
- desplegar un endpoint temporal;
- probar inferencia online;
- ejecutar simulación streaming;
- subir resultados a S3;
- subir evidencia del pipeline;
- eliminar recursos temporales.

## 3. Componentes involucrados

```text
pipeline/
    config.py
    command_runner.py
    aws_checks.py
    steps.py
    summary.py
    run_end_to_end_pipeline.py

streaming/
    simulate_streaming_inference.py

sagemaker/
    package_model.py
    deploy_endpoint.py
    test_endpoint.py
    delete_endpoint.py
```

## 4. Flujo lógico validado

```text
S3 RAW / processed / modelo
        ↓
validación AWS y S3
        ↓
empaquetado del modelo
        ↓
artefacto SageMaker en S3
        ↓
endpoint SageMaker temporal
        ↓
prueba de inferencia
        ↓
simulación streaming
        ↓
resultados CSV/JSONL en S3
        ↓
pipeline.log y run_summary.json
        ↓
eliminación de endpoint
```

## 5. Comando de prueba corta

```bash
python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 5 \
  --interval-seconds 1
```

Esta prueba valida el flujo principal sin volver a ejecutar notebooks batch.

## 6. Comando de prueba para demo Grafana

```bash
python -m pipeline.run_end_to_end_pipeline \
  --skip-notebooks \
  --events 10 \
  --interval-seconds 1 \
  --streaming-upload-every 5
```

Esta prueba valida la subida incremental de resultados streaming a S3.

## 7. Evidencia validada en AWS

Run pipeline:

```text
run_20260626_223955
```

Run streaming:

```text
run_20260626_224307
```

Rutas generadas:

```text
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_20260626_223955/pipeline.log
s3://bigdata-salmonicultura-fabian/pipeline_runs/run_20260626_223955/run_summary.json

s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_224307/inference_events.csv
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_224307/inference_events.jsonl
```

## 8. Validación de inferencia online

El endpoint SageMaker respondió correctamente a un payload de prueba.

Payload enviado:

```json
{
  "feed_per_open_biomass": 0.296827,
  "feed_per_fish": 0.002963,
  "temperature_avg": 12.05714286,
  "density_avg": 30.54454607,
  "mortality_rate": 0.0000548,
  "open_biomass": 754.6475011
}
```

Respuesta recibida:

```json
{
  "predictions": [0],
  "probabilities": [0.01267890500889963]
}
```

## 9. Validación de streaming incremental

Durante la prueba con `--streaming-upload-every 5`, el simulador realizó cargas a S3 en:

```text
evento 5
evento 10
carga final
```

Esto permite preparar la integración posterior con Grafana, ya que los archivos de salida pueden actualizarse durante la ejecución.

Durante la ejecución se observaron eventos simulados con escenarios normales y de riesgo. Algunos eventos de riesgo recibieron predicción positiva de bajo crecimiento.

Ejemplos:

```text
Evento 3  | scenario=risk | prediction=1 | prob_low_growth=0.8255949879233432
Evento 6  | scenario=risk | prediction=1 | prob_low_growth=0.7539907012729203
Evento 7  | scenario=risk | prediction=1 | prob_low_growth=0.6948006661361465
Evento 10 | scenario=risk | prediction=1 | prob_low_growth=0.8350658926400001
```

## 10. Limpieza de recursos

El pipeline eliminó automáticamente los recursos temporales de SageMaker:

```text
Endpoint SageMaker
EndpointConfig
Modelo temporal SageMaker
```

La validación final mostró:

```json
{
  "Endpoints": []
}
```

## 11. Relación con la entrega final

Este pipeline funciona como evidencia central de integración del proyecto, porque conecta:

```text
batch
S3
modelo entrenado
SageMaker
streaming simulado
predicciones
evidencia trazable
visualización futura en Grafana
```

## 12. Estado

```text
[x] Pipeline modular implementado.
[x] Prueba corta AWS validada.
[x] Prueba incremental para Grafana validada.
[x] Limpieza de endpoint validada.
[x] Evidencias subidas a S3.
```