# Big Data Salmonicultura AWS

Proyecto académico de procesamiento batch para datos productivos históricos de centros de cultivo salmonero.

El objetivo fue implementar un flujo equivalente al solicitado en la evaluación original basada en Google Cloud Platform, pero adaptado a una arquitectura AWS. El pipeline considera ingesta, almacenamiento RAW, transformación batch, capa analítica, analítica predictiva básica y dashboard KPI.

---

## Dashboard

Dashboard final en Looker Studio:

[Ver Dashboard KPI](https://datastudio.google.com/s/s_DCOggeXLU)

---

## Arquitectura general

El flujo implementado fue el siguiente:

```text
Dataset productivo histórico
        ↓
Amazon S3 - Zona RAW
        ↓
Athena / Glue Data Catalog - Tabla RAW
        ↓
PySpark - Limpieza y transformación batch
        ↓
Amazon S3 - Zona processed en Parquet
        ↓
Athena / Glue Data Catalog - Capa analítica
        ↓
Consultas KPI + Dataset ML
        ↓
Predicciones y métricas almacenadas en S3
        ↓
Looker Studio - Dashboard final
```

---

## Servicios y herramientas utilizadas

| Componente | Herramienta / Servicio |
|---|---|
| Almacenamiento cloud | Amazon S3 |
| Capa RAW | Athena + Glue Data Catalog |
| Procesamiento batch | PySpark |
| Capa analítica | Athena + Glue Data Catalog |
| Persistencia de resultados | Amazon S3 |
| Analítica predictiva | Athena + modelo local en Python |
| Visualización | Looker Studio |
| Control y documentación | Jupyter Notebooks |

---

## Notebooks del proyecto

Los notebooks se encuentran en la carpeta `notebook/`.

| Notebook | Descripción |
|---|---|
| [`pipeline_batch_salmonicultura01.ipynb`](notebook/pipeline_batch_salmonicultura01.ipynb) | Definición del caso, ingesta del dataset en S3, validación de carga y creación de tabla RAW en Athena. |
| [`pipeline_batch_salmonicultura02.ipynb`](notebook/pipeline_batch_salmonicultura02.ipynb) | Transformación batch con PySpark, limpieza de datos, conversión de tipos, validaciones e indicadores productivos. |
| [`pipeline_batch_salmonicultura03.ipynb`](notebook/pipeline_batch_salmonicultura03.ipynb) | Creación de la capa analítica, consultas KPI, persistencia, preparación de datasets ML, entrenamiento local y almacenamiento de predicciones. |

---

## Archivos principales

| Carpeta / archivo | Descripción |
|---|---|
| `dashboard/` | Archivos CSV resumidos usados como fuente en Looker Studio. |
| `screenshots/` | Evidencias visuales del desarrollo, AWS y dashboard. |
| `docs/` | Documentación del proyecto. |
| `models/` | Métricas o artefactos generados por la etapa predictiva. |
| `.env.example` | Ejemplo de variables de entorno necesarias. |
| `requirements.txt` | Dependencias Python utilizadas. |

---

## Variables de entorno

El proyecto usa un archivo `.env` para credenciales temporales del laboratorio AWS y rutas principales.

Por seguridad, el archivo `.env` real no debe subirse al repositorio.

Se incluye un archivo de ejemplo:

```text
.env.example
```

Para ejecutar los notebooks, se debe crear un archivo `.env` propio basado en `.env.example` y completar las credenciales temporales del laboratorio AWS.

---

## Limitaciones

El dataset utilizado corresponde a información productiva histórica semanal y no representa un caso Big Data completo en volumen, velocidad y variedad.

El planteamiento original consideraba una arquitectura más cercana a alimentación automatizada, sensores y video submarino. En esta versión se trabajó con los datos disponibles, usando `Feed Weight` como variable principal de alimentación.

La analítica predictiva fue implementada como aproximación metodológica. El modelo se entrenó localmente debido a restricciones del laboratorio sobre servicios como Redshift ML, SageMaker o QuickSight. Aun así, los datasets, predicciones, métricas y resultados fueron almacenados y trazados dentro del flujo AWS.

---

## Resultado

El proyecto permitió implementar un flujo batch completo, desde la ingesta hasta la visualización:

```text
S3 RAW → Athena RAW → PySpark → S3 processed → Athena DW → ML básico → Looker Studio
```

Aunque se trata de una implementación acotada, el trabajo valida la metodología de procesamiento batch y deja una base ampliable para incorporar mayor volumen de datos, sensores, eventos de alimentación y modelos predictivos más robustos.