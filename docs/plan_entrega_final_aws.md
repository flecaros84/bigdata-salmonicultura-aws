````markdown
# Plan de entrega final AWS

## Objetivo

Mejorar el proyecto Big Data de salmonicultura ya existente, incorporando ejecución de procesamiento batch en AWS, entrenamiento o reentrenamiento cloud del modelo, disponibilización del modelo en línea mediante SageMaker, simulación de datos operacionales en tiempo real, trazabilidad integral del flujo y visualización final mediante Grafana.

El proyecto mantiene como base el pipeline batch ya construido en notebooks y agrega componentes cloud para completar una arquitectura Big Data más integral, combinando procesamiento histórico, machine learning en la nube, inferencia operacional y visualización de resultados.

El objetivo final no es solo ejecutar componentes aislados, sino construir un flujo demostrable de extremo a extremo, donde cada etapa deje evidencia, logs y salidas verificables.

---

## Alcance de la entrega

La entrega final considera los siguientes bloques:

1. Procesamiento batch en AWS mediante notebooks ejecutados en JupyterLab.
2. Generación o actualización de datasets procesados en S3.
3. Entrenamiento o reentrenamiento cloud del modelo usando datos históricos.
4. Disponibilización del modelo en línea mediante AWS SageMaker.
5. Simulación de datos operacionales generados continuamente.
6. Inferencia en tiempo real usando el modelo desplegado en SageMaker.
7. Almacenamiento de eventos simulados, features y predicciones.
8. Pipeline end-to-end con logs, trazabilidad y resumen de ejecución.
9. Dashboard en Grafana para visualizar métricas de la simulación e inferencia.
10. Controles mínimos de calidad, errores, duplicidad y registro de actividad.
11. Documentación final con evidencias de ejecución.

---

## Enfoque general

El proyecto separa el procesamiento batch del procesamiento streaming, pero ambos quedan conectados mediante un pipeline trazable.

El procesamiento batch se utiliza para trabajar con datos históricos, limpiar información, calcular indicadores, generar datasets procesados y entrenar o actualizar el modelo predictivo.

El modelo entrenado se almacena en S3, se prepara como artefacto compatible con SageMaker y se disponibiliza mediante un endpoint de inferencia en línea.

El procesamiento streaming se utiliza para simular datos nuevos de operación, transformarlos en las features requeridas por el modelo y enviarlos a SageMaker para obtener predicciones en tiempo real.

De esta forma, el modelo no se entrena continuamente con cada evento nuevo. En esta versión, el streaming se usa principalmente para inferencia. Los eventos generados pueden almacenarse para alimentar procesos futuros de análisis o reentrenamiento batch.

Además, se incorpora una capa de orquestación end-to-end para ejecutar las etapas principales del proyecto en orden, registrar logs, generar un resumen JSON de ejecución y dejar evidencia trazable de cada paso.

---

## Arquitectura objetivo

```text
BLOQUE BATCH / HISTÓRICO

Dataset histórico
        ↓
S3 RAW
        ↓
JupyterLab en AWS
        ↓
Notebooks batch
        ↓
Limpieza y transformación
        ↓
S3 processed
        ↓
Entrenamiento / reentrenamiento del modelo
        ↓
Modelo joblib en S3
```

```text
BLOQUE MODELO EN LÍNEA

Modelo joblib en S3
        ↓
Empaquetado model.tar.gz
        ↓
Artefacto SageMaker en S3
        ↓
Creación de modelo SageMaker
        ↓
Endpoint SageMaker temporal
        ↓
Predicción en la nube
        ↓
Eliminación de recursos temporales
```

```text
BLOQUE STREAMING / OPERACIONAL

Simulador de datos
        ↓
Eventos productivos simulados
        ↓
Escenarios normales y de riesgo
        ↓
Transformación a features del modelo
        ↓
Endpoint SageMaker
        ↓
Predicción de bajo crecimiento
        ↓
Almacenamiento de eventos, features y predicciones
        ↓
S3 streaming results
```

```text
BLOQUE TRAZABILIDAD Y VISUALIZACIÓN

Pipeline end-to-end
        ↓
Logs de ejecución
        ↓
Resumen JSON de la corrida
        ↓
Rutas S3 generadas
        ↓
Resultados streaming con carga incremental
        ↓
Grafana
        ↓
Dashboard operacional
```

---

## Flujo end-to-end esperado

```text
S3 RAW
  ↓
Ejecución notebooks batch en AWS
  ↓
S3 processed
  ↓
Modelo entrenado en S3
  ↓
Empaquetado para SageMaker
  ↓
Endpoint SageMaker
  ↓
Simulador streaming
  ↓
Eventos + features + predicciones
  ↓
S3 streaming results
  ↓
Grafana
```

Cada etapa debe dejar evidencia mediante logs, archivos de salida o rutas S3 verificables.

---

## Features de trabajo

### 1. aws-jupyterlab-notebooks

Ejecutar los notebooks existentes en un entorno JupyterLab dentro de AWS.

Resultado esperado:

* entorno JupyterLab disponible;
* acceso a datos del proyecto en S3;
* ejecución de notebooks batch;
* evidencia de resultados;
* generación o actualización de artefactos del pipeline.

Estado:

* implementado.

---

### 2. sagemaker-modelos-cloud

Llevar a SageMaker uno de los modelos ya utilizados en los notebooks.

Resultado esperado:

* modelo seleccionado desde el trabajo existente;
* artefacto preparado para SageMaker;
* endpoint creado en SageMaker;
* predicción ejecutada en la nube;
* evidencia de entrada y salida del modelo;
* eliminación del endpoint después de la prueba.

Estado:

* implementado.

---

### 3. simulador-inferencia-streaming

Crear un simulador de datos operacionales que genere eventos continuamente y los envíe al modelo desplegado en SageMaker para obtener predicciones.

Resultado esperado:

* generador de eventos simulados compatible con el dominio del proyecto;
* eventos generados con campos equivalentes o derivados de la data original;
* escenarios operacionales normales y de riesgo;
* cálculo de features requeridas por el modelo;
* invocación automática del endpoint SageMaker;
* almacenamiento de eventos, features y predicciones;
* salida local en JSONL y CSV;
* carga de resultados a S3;
* evidencia de ejecución continua o por lotes simulados.

Esta feature representa la capa streaming del proyecto.

Estado:

* implementado.

---

### 4. pipeline-end-to-end-trazabilidad

Crear un pipeline ejecutable que coordine las etapas principales del proyecto y deje evidencia trazable de cada paso.

Resultado esperado:

* script orquestador end-to-end;
* validación de ambiente AWS;
* validación de rutas S3 principales;
* ejecución o coordinación del pipeline batch;
* validación del modelo generado;
* empaquetado del modelo para SageMaker;
* despliegue temporal del endpoint SageMaker;
* prueba de inferencia;
* ejecución del simulador streaming;
* almacenamiento de resultados en S3;
* subida incremental de resultados streaming para demo Grafana;
* eliminación del endpoint al finalizar;
* generación de logs;
* generación de resumen de ejecución en JSON;
* registro de rutas S3 y artefactos generados;
* limpieza automática de recursos temporales;
* validación final de endpoints activos.

Esta feature conecta los componentes ya construidos y permite demostrar el flujo completo del proyecto de forma ordenada.

Evidencia validada:

```text
Run pipeline: run_20260626_223955
Run streaming: run_20260626_224307
Eventos simulados: 10
Subida incremental: cada 5 eventos
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

Estado:

* implementado.

---

### 5. grafana-dashboard-tiempo-real

Implementar un dashboard en Grafana para visualizar los resultados generados por la simulación streaming.

Resultado esperado:

* fuente de datos conectada a Grafana;
* dashboard con métricas operacionales;
* visualización de eventos simulados;
* visualización de predicciones del modelo;
* visualización de probabilidad de bajo crecimiento;
* visualización por centro, unidad o escenario operacional;
* visualización de alertas o indicadores de bajo crecimiento;
* evidencia visual del panel funcionando.

Grafana debe colgar de los resultados generados por el flujo streaming y, preferentemente, de las salidas formales producidas por el pipeline end-to-end.

Estado:

* pendiente.

---

### 6. controles-calidad-trazabilidad

Agregar controles mínimos al proyecto para dejar evidencia de robustez del pipeline.

Resultado esperado:

* control de errores;
* control de duplicados;
* logs o registro de ejecución;
* validaciones de datos;
* métricas básicas de calidad;
* trazabilidad entre datos RAW, datos procesados, features, predicciones y resultados visualizados;
* identificación de registros inválidos o incompletos;
* resumen de calidad por corrida.

Esta feature puede apoyarse en los logs y salidas del pipeline end-to-end.

Estado:

* parcial.

Observación:

El pipeline end-to-end ya incorpora validación de identidad AWS, validación de rutas S3, manejo de errores, logs, resumen JSON, limpieza de endpoint y trazabilidad de rutas generadas. Sin embargo, aún falta una feature específica para controles de calidad de datos, duplicados, registros inválidos y métricas de calidad por corrida.

---

### 7. docs-entrega-final

Actualizar la documentación final del proyecto.

Resultado esperado:

* README actualizado;
* informe con arquitectura, procesos y evidencias;
* anexo técnico;
* presentación final;
* capturas de notebooks, SageMaker, simulador, almacenamiento, pipeline end-to-end y Grafana.

Estado:

* pendiente.

---

## Orden recomendado de implementación

```text
1. aws-jupyterlab-notebooks
2. sagemaker-modelos-cloud
3. simulador-inferencia-streaming
4. pipeline-end-to-end-trazabilidad
5. grafana-dashboard-tiempo-real
6. controles-calidad-trazabilidad
7. docs-entrega-final
```

---

## Estado general

```text
[x] Ejecutar notebooks batch en AWS JupyterLab.
[x] Preparar y probar modelo en SageMaker.
[x] Crear simulador de datos streaming.
[x] Ejecutar inferencia continua contra SageMaker.
[x] Guardar resultados de simulación en S3.
[x] Crear pipeline end-to-end trazable.
[x] Generar logs y resumen JSON de ejecución.
[x] Subir resultados streaming incrementalmente para demo Grafana.
[ ] Construir dashboard en Grafana.
[~] Agregar controles de calidad y trazabilidad.
[ ] Actualizar documentación final.
```

---

## Próximo bloque de trabajo

El siguiente bloque técnico recomendado es:

```text
feature/grafana-dashboard-tiempo-real
```

Objetivo del siguiente bloque:

```text
Construir una visualización operacional en Grafana usando los resultados streaming
generados por el pipeline end-to-end.
```

La visualización debe enfocarse en:

* cantidad de eventos simulados;
* probabilidad de bajo crecimiento;
* predicciones por escenario normal o de riesgo;
* predicciones por centro o unidad;
* evolución temporal de la probabilidad;
* indicadores o alertas visuales para eventos con predicción de bajo crecimiento.

---

## Criterio de cierre del proyecto

El proyecto se considerará completo cuando pueda demostrarse el siguiente flujo:

```text
Datos históricos en S3
        ↓
Procesamiento batch en AWS
        ↓
Modelo entrenado y almacenado
        ↓
Modelo disponible en SageMaker
        ↓
Datos simulados generados continuamente
        ↓
Inferencia streaming contra SageMaker
        ↓
Resultados almacenados en S3
        ↓
Pipeline con logs y trazabilidad
        ↓
Dashboard Grafana con métricas operacionales
```

Además, cada etapa debe contar con evidencia mínima de ejecución, ya sea mediante capturas, logs, archivos generados, rutas S3 o salidas documentadas.
````
