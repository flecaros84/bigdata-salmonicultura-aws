# Feature: SageMaker Modelos Cloud

## 1. Objetivo

Implementar en AWS SageMaker un modelo de machine learning ya utilizado en los notebooks del proyecto.

La mejora busca demostrar que el modelo predictivo del pipeline batch no queda limitado al entorno local o al notebook, sino que puede prepararse como artefacto de machine learning en la nube y ejecutarse mediante servicios de AWS.

---

## 2. Criterio de consistencia

Para mantener continuidad con el proyecto existente, no se entrenará un modelo nuevo desconectado del análisis previo.

El modelo utilizado será el mismo modelo generado por los notebooks batch del proyecto:

```text
low_growth_logistic_model.joblib
```

Este modelo corresponde a la predicción de bajo crecimiento productivo mediante la variable objetivo:

```text
low_growth_flag
```

---

## 3. Artefactos base

Modelo:

```text
s3://bigdata-salmonicultura-fabian/models/low_growth_logistic_model.joblib
```

Métricas:

```text
s3://bigdata-salmonicultura-fabian/models/low_growth_model_metrics.json
```

Predicciones batch:

```text
s3://bigdata-salmonicultura-fabian/exports/ml_predictions/ml_predictions_low_growth.csv
```

---

## 4. Métricas actuales del modelo

Las métricas generadas por el notebook son:

```text
accuracy: 0.8521
precision: 0.8564
recall: 0.8437
f1_score: 0.8500
```

---

## 5. Enfoque técnico

La implementación en SageMaker se realizará en etapas:

1. descargar el modelo existente desde S3;
2. empaquetar el modelo como artefacto `model.tar.gz`;
3. crear un script de inferencia compatible con SageMaker;
4. subir el artefacto empaquetado a S3;
5. crear un modelo SageMaker;
6. desplegar un endpoint de inferencia;
7. ejecutar una predicción de prueba;
8. documentar input, output y evidencias.

---

## 6. Estructura esperada

Se agregará la siguiente estructura al repositorio:

```text
sagemaker/
    inference.py
    package_model.py
    deploy_endpoint.py
    test_endpoint.py
    delete_endpoint.py
    README.md
```

---

## 7. Contrato de entrada del modelo

El endpoint recibirá un registro JSON con las features utilizadas por el modelo.

Features esperadas:

```text
feed_per_open_biomass
feed_per_fish
temperature_avg
density_avg
mortality_rate
open_biomass
```

Ejemplo de entrada:

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

---

## 8. Resultado esperado

Al finalizar esta feature, el proyecto debe demostrar:

- modelo existente preparado para SageMaker;
- artefacto `model.tar.gz` creado;
- artefacto subido a S3;
- endpoint SageMaker creado;
- predicción de prueba ejecutada;
- resultado documentado;
- procedimiento para eliminar el endpoint.

---

## 9. Estado de implementación

Pendiente.

Se completará después de ejecutar la implementación en AWS.