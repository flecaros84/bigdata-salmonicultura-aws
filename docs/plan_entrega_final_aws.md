# Plan de entrega final AWS

## Objetivo

Mejorar el proyecto Big Data de salmonicultura ya existente, incorporando ejecución de notebooks en AWS, machine learning en la nube con SageMaker, simulación de datos operacionales en tiempo real e implementación de un dashboard en Grafana.

El proyecto mantiene como base el pipeline batch ya construido y agrega componentes cloud para completar una arquitectura Big Data más integral, combinando procesamiento histórico, inferencia en la nube y visualización operacional.

---

## Alcance de la entrega

La entrega final considera los siguientes bloques:

1. Procesamiento batch en AWS mediante notebooks ejecutados en JupyterLab.
2. Modelo de machine learning desplegado en AWS SageMaker.
3. Simulación de datos operacionales generados continuamente.
4. Inferencia en tiempo real usando el modelo desplegado en SageMaker.
5. Almacenamiento de eventos simulados, features y predicciones.
6. Dashboard en Grafana para visualizar métricas de la simulación.
7. Controles mínimos de calidad, errores, duplicidad y registro de actividad.
8. Documentación final con evidencias de ejecución.

---

## Enfoque general

El proyecto separa el procesamiento batch del procesamiento streaming.

El procesamiento batch se utiliza para trabajar con datos históricos, limpiar información, calcular indicadores, generar datasets procesados y entrenar el modelo predictivo.

El procesamiento streaming se utiliza para simular datos nuevos de operación, transformarlos en las features requeridas por el modelo y enviarlos a SageMaker para obtener predicciones en tiempo real.

De esta forma, el modelo no se entrena continuamente con cada evento nuevo. En esta versión, el streaming se usa principalmente para inferencia. Los eventos generados pueden almacenarse para alimentar procesos futuros de reentrenamiento batch.

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
Entrenamiento del modelo
        ↓
Modelo joblib en S3
        ↓
Artefacto SageMaker
        ↓
Endpoint SageMaker
```

```text
BLOQUE STREAMING / OPERACIONAL

Simulador de datos
        ↓
Eventos productivos simulados
        ↓
Transformación a features del modelo
        ↓
Endpoint SageMaker
        ↓
Predicción de bajo crecimiento
        ↓
Almacenamiento de resultados
        ↓
Grafana
        ↓
Dashboard tiempo real
```

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
* cálculo de features requeridas por el modelo;
* invocación automática del endpoint SageMaker;
* almacenamiento de eventos, features y predicciones;
* evidencia de ejecución continua o por lotes simulados.

Esta feature representa la capa streaming del proyecto.

---

### 4. grafana-dashboard-tiempo-real

Implementar un dashboard en Grafana para visualizar los resultados generados por la simulación streaming.

Resultado esperado:

* fuente de datos conectada a Grafana;
* dashboard con métricas operacionales;
* visualización de eventos simulados;
* visualización de predicciones del modelo;
* visualización de alertas o indicadores de bajo crecimiento;
* evidencia visual del panel funcionando.

---

### 5. controles-calidad-trazabilidad

Agregar controles mínimos al proyecto para dejar evidencia de robustez del pipeline.

Resultado esperado:

* control de errores;
* control de duplicados;
* logs o registro de ejecución;
* validaciones de datos;
* métricas básicas de calidad;
* trazabilidad entre datos RAW, datos procesados, features, predicciones y resultados visualizados.

---

### 6. docs-entrega-final

Actualizar la documentación final del proyecto.

Resultado esperado:

* README actualizado;
* informe con arquitectura, procesos y evidencias;
* anexo técnico;
* presentación final;
* capturas de notebooks, SageMaker, simulador, almacenamiento y Grafana.

---

## Orden recomendado de implementación

```text
1. aws-jupyterlab-notebooks
2. sagemaker-modelos-cloud
3. simulador-inferencia-streaming
4. grafana-dashboard-tiempo-real
5. controles-calidad-trazabilidad
6. docs-entrega-final
```

---

## Estado general

```text
[x] Ejecutar notebooks batch en AWS JupyterLab.
[x] Preparar y probar modelo en SageMaker.
[ ] Crear simulador de datos streaming.
[ ] Ejecutar inferencia continua contra SageMaker.
[ ] Guardar resultados de simulación.
[ ] Construir dashboard en Grafana.
[ ] Agregar controles de calidad y trazabilidad.
[ ] Actualizar documentación final.
```
