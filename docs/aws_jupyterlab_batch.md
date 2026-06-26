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

## 8. Estado de implementación

Pendiente.

Se completará después de ejecutar los notebooks en AWS.