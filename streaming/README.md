# Simulador de inferencia streaming

Esta carpeta contiene el simulador de datos operacionales del proyecto Big Data de salmonicultura.

El simulador genera eventos productivos de forma continua, calcula las features requeridas por el modelo de bajo crecimiento y envía cada evento a un endpoint de AWS SageMaker.

---

## Script principal

```text
simulate_streaming_inference.py