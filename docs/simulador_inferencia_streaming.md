# Simulador de inferencia streaming

## Objetivo

Implementar una simulación de datos operacionales en tiempo real para el proyecto Big Data de salmonicultura.

El simulador genera eventos productivos de forma continua, calcula las features necesarias para el modelo de bajo crecimiento y envía cada evento al endpoint de AWS SageMaker para obtener una predicción.

Esta feature complementa el procesamiento batch y el despliegue del modelo en SageMaker, agregando una capa operacional tipo streaming para demostrar inferencia continua sobre datos nuevos.

---

## Rol dentro de la arquitectura

Esta feature representa la capa streaming del proyecto.

El procesamiento batch trabaja con datos históricos, genera datasets procesados y produce el modelo predictivo. En cambio, el simulador streaming representa la llegada continua de nuevos datos operacionales.

Flujo general:

```text
Simulador de datos
        ↓
Evento productivo simulado
        ↓
Cálculo de features
        ↓
Endpoint SageMaker
        ↓
Predicción de bajo crecimiento
        ↓
Registro de resultado
        ↓
Archivo local / S3
        ↓
Base para dashboard Grafana
```

---

## Enfoque de inferencia

Los datos streaming se utilizan para predicción en tiempo real, no para entrenamiento inmediato.

El modelo ya fue entrenado previamente usando datos históricos procesados en el pipeline batch. Cada evento nuevo generado por el simulador se transforma en las features esperadas por el modelo y se envía al endpoint SageMaker.

Los eventos generados también quedan almacenados, por lo que podrían alimentar procesos futuros de análisis, auditoría o reentrenamiento batch.

---

## Modalidad de ejecución

El simulador está diseñado para ejecutarse en AWS durante la prueba del proyecto.

No queda ejecutándose de forma permanente. El flujo operativo recomendado es:

```text
Crear endpoint SageMaker
        ↓
Ejecutar simulador streaming en AWS
        ↓
Generar eventos y predicciones
        ↓
Guardar resultados locales y en S3
        ↓
Capturar evidencia
        ↓
Eliminar endpoint SageMaker
```

Esto permite demostrar un flujo online de inferencia sin dejar recursos activos innecesariamente en el laboratorio AWS.

---

## Script implementado

El script principal de la feature es:

```text
streaming/simulate_streaming_inference.py
```

Este script permite:

```text
- generar eventos productivos simulados;
- calcular features compatibles con el modelo;
- ejecutar inferencia contra un endpoint SageMaker;
- registrar resultados en JSONL y CSV;
- subir los resultados a S3;
- ejecutar pruebas locales con modo dry-run;
- ejecutar pruebas reales en AWS contra SageMaker.
```

---

## Campos simulados

El simulador genera campos equivalentes o cercanos a la estructura RAW original:

```text
Site
Unit
Year
Week
Species
Year class
Open Count
Open Biomass
Open Weight
Feed Weight
Temperature Avg
Density Avg
Live Days
Fish Days
Mortality Count
Harvest Count
Ship Out Count
Ship In Count
Close Biomass
```

Además, se incorporó un campo de escenario operacional para facilitar la generación de casos con distinto nivel de riesgo:

```text
Scenario
```

Los escenarios considerados son:

```text
normal
risk
```

El escenario `normal` genera condiciones productivas más estables. El escenario `risk` genera condiciones más exigentes, como menor alimentación relativa, temperatura menos favorable, mayor densidad o mayor mortalidad.

---

## Features enviadas al modelo

A partir del evento simulado se calculan las siguientes features:

```text
feed_per_open_biomass
feed_per_fish
temperature_avg
density_avg
mortality_rate
open_biomass
```

Estas features corresponden al contrato de entrada usado por el endpoint SageMaker.

---

## Resultado esperado por evento

Por cada evento generado, el simulador registra:

```text
processed_timestamp
endpoint_name
event_id
event_timestamp
site
unit
species
scenario
year
week
open_count
open_biomass
feed_weight
temperature_avg
density_avg
mortality_count
feed_per_open_biomass
feed_per_fish
mortality_rate
prediction
probability_low_growth
raw_event_json
features_json
prediction_response_json
```

Esto permite mantener trazabilidad entre:

```text
evento simulado
        ↓
features calculadas
        ↓
respuesta del modelo
        ↓
resultado almacenado
```

---

## Salidas esperadas

Salida local:

```text
outputs/streaming/inference_events.jsonl
outputs/streaming/inference_events.csv
```

Salida S3:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/
```

---

## Modo dry-run

El simulador incorpora un modo `dry-run` para validar la generación de datos sin invocar AWS.

Este modo es útil para pruebas locales, porque no requiere endpoint activo ni credenciales AWS.

Comando utilizado:

```bash
python streaming/simulate_streaming_inference.py --endpoint-name dry-run --events 5 --interval-seconds 0.5 --dry-run
```

Resultado observado:

```text
Iniciando simulador de inferencia streaming
Endpoint SageMaker: dry-run
Modo dry-run: sí
Eventos configurados: 5
Intervalo segundos: 0.5
Salida JSONL: outputs\streaming\inference_events.jsonl
Salida CSV: outputs\streaming\inference_events.csv
Evento procesado | id=1 | site=SITE_001 | prediction=0 | prob_low_growth=0.258
Evento procesado | id=2 | site=SITE_001 | prediction=1 | prob_low_growth=0.813694
Evento procesado | id=3 | site=SITE_001 | prediction=0 | prob_low_growth=0.414803
Evento procesado | id=4 | site=SITE_003 | prediction=1 | prob_low_growth=0.870873
Evento procesado | id=5 | site=SITE_001 | prediction=0 | prob_low_growth=0.079471
Simulación finalizada.
```

Esta prueba confirmó que el simulador genera eventos, calcula features, registra predicciones simuladas y escribe archivos locales correctamente.

---

## Prueba real en AWS

Para validar el flujo streaming real, se creó nuevamente un endpoint SageMaker a partir del modelo previamente empaquetado.

Endpoint utilizado:

```text
low-growth-endpoint-1782508657
```

Modelo asociado:

```text
low-growth-model-1782508657
```

Artefacto del modelo:

```text
s3://bigdata-salmonicultura-fabian/sagemaker/model-artifacts/low_growth_model.tar.gz
```

Antes de ejecutar el simulador, se validó el endpoint con un payload manual.

Comando utilizado:

```bash
python sagemaker/test_endpoint.py --endpoint-name low-growth-endpoint-1782508657
```

Respuesta obtenida:

```json
{
  "predictions": [0],
  "probabilities": [0.01267890500889963]
}
```

Esto confirmó que el endpoint estaba activo y respondiendo correctamente antes de recibir eventos del simulador.

---

## Ejecución del simulador contra SageMaker

Se ejecutó el simulador en AWS contra el endpoint SageMaker activo.

Comando utilizado:

```bash
python streaming/simulate_streaming_inference.py \
  --endpoint-name low-growth-endpoint-1782508657 \
  --events 30 \
  --interval-seconds 1 \
  --upload-s3
```

Configuración de la prueba:

```text
Eventos generados: 30
Intervalo entre eventos: 1 segundo
Modo dry-run: no
Endpoint SageMaker: low-growth-endpoint-1782508657
Subida a S3: habilitada
```

Resultado observado:

```text
Los 30 eventos fueron procesados correctamente.
Cada evento fue enviado al endpoint SageMaker.
Cada evento recibió una predicción y una probabilidad asociada.
Los resultados fueron escritos localmente en formato JSONL y CSV.
Los resultados fueron subidos a S3.
```

---

## Archivos generados

Durante la ejecución real se generaron archivos locales:

```text
outputs/streaming/inference_events.jsonl
outputs/streaming/inference_events.csv
```

Además, los resultados fueron almacenados en S3:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_212328/inference_events.csv
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_212328/inference_events.jsonl
```

Validación S3:

```text
2026-06-26 21:23:29      33909 streaming/inference_events/run_20260626_212328/inference_events.csv
2026-06-26 21:23:29      45902 streaming/inference_events/run_20260626_212328/inference_events.jsonl
```

---

## Eliminación del endpoint

Después de capturar la evidencia, el endpoint SageMaker fue eliminado para evitar consumo innecesario de recursos del laboratorio AWS.

Comando utilizado:

```bash
python sagemaker/delete_endpoint.py --endpoint-name low-growth-endpoint-1782508657
```

Recursos eliminados:

```text
Endpoint: low-growth-endpoint-1782508657
EndpointConfig: low-growth-endpoint-1782508657
Modelo SageMaker: low-growth-model-1782508657
```

Validación final:

```json
{
  "Endpoints": []
}
```

Esto confirma que no quedaron endpoints activos asociados al modelo.

---

## Relación con Grafana

Esta feature no construye aún el dashboard.

Su objetivo es generar datos de streaming e inferencia. La siguiente feature utilizará estos resultados como fuente para construir visualizaciones en Grafana.

La fuente inicial para Grafana será el archivo CSV generado por el simulador:

```text
s3://bigdata-salmonicultura-fabian/streaming/inference_events/run_20260626_212328/inference_events.csv
```

---

## Resultado final de la feature

La feature `simulador-inferencia-streaming` queda completada.

El proyecto ahora demuestra un flujo de inferencia streaming ejecutado en AWS:

```text
Simulador en AWS
        ↓
Evento operacional simulado
        ↓
Cálculo de features
        ↓
Endpoint SageMaker
        ↓
Predicción de bajo crecimiento
        ↓
Registro JSONL / CSV
        ↓
Almacenamiento en S3
```

Este resultado deja preparada la base operacional para la siguiente feature: construcción de dashboard en Grafana.
