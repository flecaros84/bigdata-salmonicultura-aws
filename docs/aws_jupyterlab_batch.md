# Feature: AWS JupyterLab Notebooks

## 1. Objetivo

Ejecutar los notebooks existentes del proyecto en un entorno JupyterLab dentro de AWS, validando que el pipeline batch pueda operar desde la nube y acceder a los datos del proyecto.

Esta feature busca demostrar que el procesamiento histórico del proyecto no depende exclusivamente de un entorno local.

---

## 2. Enfoque técnico

La opción principal será utilizar un entorno JupyterLab dentro de AWS.

Opciones consideradas:

```text
Opción principal:
AWS SageMaker Notebook Instance o SageMaker Studio con JupyterLab.

Opción alternativa:
Instancia EC2 con JupyterLab instalado manualmente.
```

La opción principal es preferida porque se integra mejor con el resto de mejoras del proyecto, especialmente con SageMaker para machine learning en la nube.

---

## 3. Flujo esperado

```text
Repositorio GitHub
        ↓
JupyterLab en AWS
        ↓
Clonación del proyecto
        ↓
Instalación de dependencias
        ↓
Acceso a datos del proyecto
        ↓
Ejecución de notebooks batch
        ↓
Generación de salidas y evidencias
```

---

## 4. Notebooks a validar

Pendiente de confirmar con el estado real del repositorio.

Inicialmente se consideran los notebooks existentes del pipeline batch:

```text
notebook/pipeline_batch_salmonicultura01.ipynb
notebook/pipeline_batch_salmonicultura02.ipynb
notebook/pipeline_batch_salmonicultura03.ipynb
```

---

## 5. Validaciones mínimas

La ejecución en AWS debe permitir evidenciar:

- apertura del proyecto desde JupyterLab;
- instalación de dependencias necesarias;
- lectura de datos desde la fuente definida;
- ejecución de al menos un notebook batch;
- generación de salidas o resultados;
- ausencia de errores críticos durante la ejecución.

---

## 6. Evidencias esperadas

Durante la implementación se deben capturar evidencias como:

```text
- entorno JupyterLab abierto en AWS;
- repositorio clonado;
- notebook ejecutado;
- lectura correcta de datos;
- resultados generados;
- archivos de salida si corresponde.
```

Las capturas se guardarán posteriormente en una carpeta de evidencias del proyecto.

---

## 7. Resultado esperado de la feature

Al finalizar esta feature, el proyecto debe demostrar que el pipeline batch puede ejecutarse desde un entorno cloud en AWS usando JupyterLab.

Esto servirá como base para las siguientes mejoras:

```text
JupyterLab en AWS
        ↓
Modelo trabajado desde notebooks
        ↓
SageMaker
        ↓
Predicción en la nube
```

---

## 8. Resultado de implementación

La feature fue implementada utilizando una instancia de AWS SageMaker Notebook Instance con JupyterLab.

Desde el entorno JupyterLab se realizaron las siguientes acciones:

- clonación del repositorio desde GitHub;
- validación del entorno Python;
- validación del rol AWS asociado a la instancia;
- validación de acceso al bucket S3 del proyecto;
- lectura de datos RAW desde S3;
- lectura de datos procesados en formato Parquet desde S3;
- ejecución de los notebooks batch del proyecto;
- actualización del modelo y de las predicciones en S3.

---

## 9. Configuración utilizada

Entorno utilizado:

```text
Servicio AWS: SageMaker Notebook Instance
Entorno: JupyterLab
Instancia: ml.t3.medium
Sistema base: Amazon Linux 2023
Python: 3.10.20
Rol AWS: LabRole/SageMaker
Java utilizado para PySpark: Amazon Corretto 17
```

Bucket utilizado:

```text
s3://bigdata-salmonicultura-fabian
```

Rutas principales:

```text
RAW:
s3://bigdata-salmonicultura-fabian/raw/productive_data/productive_data.csv

PROCESSED:
s3://bigdata-salmonicultura-fabian/processed/productive_kpi/

MODELO:
s3://bigdata-salmonicultura-fabian/models/low_growth_logistic_model.joblib

MÉTRICAS:
s3://bigdata-salmonicultura-fabian/models/low_growth_model_metrics.json

PREDICCIONES:
s3://bigdata-salmonicultura-fabian/exports/ml_predictions/ml_predictions_low_growth.csv
```

---

## 10. Validaciones realizadas

### 10.1 Validación de acceso AWS

Se validó que la instancia JupyterLab operaba con el rol del laboratorio:

```text
arn:aws:sts::601270941236:assumed-role/LabRole/SageMaker
```

También se validó acceso al bucket S3 del proyecto:

```text
bigdata-salmonicultura-fabian
```

---

### 10.2 Validación de datos RAW

El archivo RAW fue identificado en la siguiente ruta:

```text
s3://bigdata-salmonicultura-fabian/raw/productive_data/productive_data.csv
```

Durante la validación se detectó que el archivo utiliza:

```text
Separador: ;
Decimal: ,
Columnas: 19
```

La lectura corregida se realizó usando:

```python
pd.read_csv(
    raw_path,
    sep=";",
    decimal=","
)
```

En una muestra de 10.000 registros se obtuvieron las siguientes métricas de calidad:

```text
Registros muestra: 10.000
Columnas: 19

Nulos principales:
Site                  0
Unit                  0
Year                  0
Week                  0
Open Biomass          0
Feed Weight        2047
Temperature Avg     910
Density Avg           0
```

---

### 10.3 Validación de datos procesados

La capa procesada fue leída correctamente desde formato Parquet:

```text
s3://bigdata-salmonicultura-fabian/processed/productive_kpi/
```

Resultado de validación:

```text
Registros: 783.244
Columnas: 28
Sites: 101
Units: 5.108
```

---

## 11. Ejecución de notebooks en AWS

Se ejecutaron los tres notebooks principales del pipeline batch desde JupyterLab en AWS usando `nbconvert`.

Comando base utilizado:

```bash
jupyter nbconvert \
  --to notebook \
  --execute notebook/NOMBRE_NOTEBOOK.ipynb \
  --output NOMBRE_NOTEBOOK_executed.ipynb \
  --output-dir outputs/jupyterlab_aws \
  --ExecutePreprocessor.timeout=-1
```

Resultado:

```text
pipeline_batch_salmonicultura01.ipynb: ejecutado correctamente.
pipeline_batch_salmonicultura02.ipynb: ejecutado correctamente.
pipeline_batch_salmonicultura03.ipynb: ejecutado correctamente.
```

Archivos generados:

```text
outputs/jupyterlab_aws/pipeline_batch_salmonicultura01_executed.ipynb
outputs/jupyterlab_aws/pipeline_batch_salmonicultura02_executed.ipynb
outputs/jupyterlab_aws/pipeline_batch_salmonicultura03_executed.ipynb
```

---

## 12. Incidencias y resolución

### 12.1 Kernel no encontrado

Al ejecutar los notebooks, inicialmente apareció un error porque el kernel esperado por los notebooks no existía en la instancia AWS:

```text
No such kernel named bigdata-salmonicultura-aws
```

Solución aplicada:

```bash
python -m ipykernel install \
  --user \
  --name bigdata-salmonicultura-aws \
  --display-name "Python (bigdata-salmonicultura-aws)"
```

---

### 12.2 Variables de entorno no cargadas

El notebook 01 falló inicialmente porque `S3_BUCKET` no estaba definido en el entorno AWS.

Solución aplicada:

Se creó un archivo `.env` local en la instancia con las variables necesarias del proyecto:

```text
AWS_DEFAULT_REGION
S3_BUCKET
S3_RAW_PREFIX
S3_RAW_KEY
ATHENA_DATABASE
ATHENA_RAW_TABLE
ATHENA_OUTPUT
CSV_DELIMITER
```

El archivo `.env` no debe subirse al repositorio.

---

### 12.3 Compatibilidad Java y Spark

El notebook 02 falló inicialmente porque la instancia estaba usando Java 25, incompatible con la ejecución de PySpark/Hadoop utilizada en el proyecto.

Error observado:

```text
java.lang.UnsupportedOperationException: getSubject is not supported
```

Solución aplicada:

Se configuró temporalmente Java 17 usando Amazon Corretto:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-amazon-corretto.x86_64
export PATH=$JAVA_HOME/bin:$PATH
```

Validación:

```text
openjdk version "17.0.19"
Amazon Corretto 17
```

---

### 12.4 Credenciales temporales para Spark S3A

PySpark/S3A requirió credenciales temporales explícitas para acceder al bucket mediante `s3a://`.

Solución aplicada:

Se obtuvieron las credenciales temporales del rol activo de la instancia mediante `boto3` y se agregaron al `.env` local.

Estas credenciales son temporales y no deben versionarse en Git.

---

## 13. Resultado final de la feature

La feature `aws-jupyterlab-notebooks` queda completada.

El proyecto demuestra que el pipeline batch puede ejecutarse desde AWS utilizando JupyterLab, accediendo a datos en S3, procesando información con PySpark y actualizando los artefactos de machine learning generados por el proyecto.

Esta feature deja preparada la base para la siguiente etapa:

```text
Notebook ejecutado en AWS
        ↓
Modelo generado en S3
        ↓
SageMaker para inferencia en la nube
```