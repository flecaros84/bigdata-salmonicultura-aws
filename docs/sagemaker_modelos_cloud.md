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

---

## 10. Resultado de implementación

La feature `sagemaker-modelos-cloud` fue implementada correctamente.

Se tomó el modelo generado previamente por los notebooks batch del proyecto y se preparó como artefacto compatible con AWS SageMaker.

Modelo base utilizado:

```text
s3://bigdata-salmonicultura-fabian/models/low_growth_logistic_model.joblib
```

Artefacto SageMaker generado:

```text
s3://bigdata-salmonicultura-fabian/sagemaker/model-artifacts/low_growth_model.tar.gz
```

El empaquetado se realizó mediante el script:

```text
sagemaker/package_model.py
```

Resultado del empaquetado:

```text
Modelo descargado desde S3.
Artefacto low_growth_model.tar.gz creado correctamente.
Artefacto subido a S3 correctamente.
```

---

## 11. Despliegue en SageMaker

Se desplegó el modelo como endpoint de inferencia en tiempo real utilizando AWS SageMaker.

Configuración utilizada:

```text
EndpointName: low-growth-endpoint-1782506140
ModelName: low-growth-model-1782506140
Rol: arn:aws:iam::601270941236:role/LabRole
Instancia: ml.m5.large
Framework: Scikit-learn 1.4-2
Modelo S3: s3://bigdata-salmonicultura-fabian/sagemaker/model-artifacts/low_growth_model.tar.gz
```

El despliegue fue ejecutado mediante:

```text
sagemaker/deploy_endpoint.py
```

Resultado:

```text
Endpoint creado correctamente.
```

---

## 12. Prueba de inferencia

Se ejecutó una predicción de prueba contra el endpoint SageMaker utilizando el script:

```text
sagemaker/test_endpoint.py
```

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

Respuesta del endpoint:

```json
{
  "predictions": [0],
  "probabilities": [0.01267890500889963]
}
```

Interpretación:

```text
El modelo predijo clase 0, equivalente a no bajo crecimiento.
La probabilidad estimada de bajo crecimiento fue aproximadamente 1,27%.
```

---

## 13. Eliminación del endpoint

Después de validar la inferencia, el endpoint fue eliminado para evitar consumo innecesario de recursos del laboratorio AWS.

Script utilizado:

```text
sagemaker/delete_endpoint.py
```

Recursos eliminados:

```text
Endpoint: low-growth-endpoint-1782506140
EndpointConfig: low-growth-endpoint-1782506140
Modelo SageMaker: low-growth-model-1782506140
```

Validación final:

```json
{
  "Endpoints": []
}
```

Esto confirma que no quedaron endpoints activos asociados al modelo `low-growth`.

---

## 14. Resultado final de la feature

La feature `sagemaker-modelos-cloud` queda completada.

El proyecto demuestra que el modelo de machine learning generado en los notebooks puede ser preparado, empaquetado, desplegado y consumido desde AWS SageMaker mediante inferencia en tiempo real.

Flujo validado:

```text
Notebook batch
        ↓
Modelo joblib en S3
        ↓
Empaquetado model.tar.gz
        ↓
SageMaker Model
        ↓
SageMaker Endpoint
        ↓
Predicción en la nube
        ↓
Eliminación del endpoint
```