# Plan de entrega final AWS

## Objetivo

Mejorar el proyecto Big Data de salmonicultura ya existente, incorporando ejecución de notebooks en AWS, machine learning en la nube con SageMaker y simulación de datos en tiempo real con dashboard en Grafana.

El proyecto mantiene como base el pipeline batch ya construido y agrega componentes cloud para completar una arquitectura Big Data más integral.

---

## Alcance de la entrega

La entrega final considera los siguientes bloques:

1. Procesamiento batch en AWS mediante notebooks ejecutados en JupyterLab.
2. Modelo de machine learning desplegado o ejecutado en AWS SageMaker.
3. Simulación de datos operacionales en tiempo real.
4. Dashboard en Grafana para visualizar métricas de la simulación.
5. Controles mínimos de calidad, errores, duplicidad y registro de actividad.
6. Documentación final con evidencias de ejecución.

---

## Features de trabajo

### 1. aws-jupyterlab-batch

Ejecutar los notebooks existentes en un entorno JupyterLab dentro de AWS.

Resultado esperado:

- entorno JupyterLab disponible;
- acceso a datos del proyecto;
- ejecución de notebooks batch;
- evidencia de resultados.

---

### 2. sagemaker-modelos-cloud

Llevar a SageMaker uno de los modelos ya utilizados en los notebooks.

Resultado esperado:

- modelo seleccionado desde el trabajo existente;
- artefacto o script preparado para SageMaker;
- predicción ejecutada en la nube;
- evidencia de entrada y salida del modelo.

---

### 3. streaming-grafana-dashboard

Implementar una simulación de datos en tiempo real y visualizarla en Grafana.

Resultado esperado:

- generador de datos simulados;
- almacenamiento o exposición de métricas;
- dashboard Grafana funcionando;
- evidencia visual del panel.

---

### 4. controles-calidad-trazabilidad

Agregar controles mínimos al proyecto para dejar evidencia de robustez del pipeline.

Resultado esperado:

- control de errores;
- control de duplicados;
- logs o registro de ejecución;
- validaciones de datos;
- métricas básicas de calidad.

---

### 5. docs-entrega-final

Actualizar la documentación final del proyecto.

Resultado esperado:

- README actualizado;
- informe con arquitectura, procesos y evidencias;
- anexo técnico;
- presentación final.