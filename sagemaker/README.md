# SageMaker Modelos Cloud

Esta carpeta contiene los scripts para preparar y desplegar en AWS SageMaker el modelo ya generado por los notebooks batch del proyecto.

## Modelo utilizado

```text
low_growth_logistic_model.joblib
```

## Artefacto esperado

```text
s3://bigdata-salmonicultura-fabian/sagemaker/model-artifacts/low_growth_model.tar.gz
```

## Scripts

```text
inference.py
    Script de inferencia compatible con SageMaker.

package_model.py
    Descarga el modelo existente desde S3, crea model.tar.gz y lo sube nuevamente a S3.
```

## Ejecución del empaquetado

```bash
python sagemaker/package_model.py
```