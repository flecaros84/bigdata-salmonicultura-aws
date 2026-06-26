"""
Validaciones AWS y S3 utilizadas por el pipeline.

Estas funciones permiten dejar evidencia de:
- identidad AWS activa;
- existencia del dataset RAW;
- existencia de datos procesados;
- existencia del modelo;
- existencia de métricas del modelo.
"""

import logging
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

from pipeline.config import (
    METRICS_KEY,
    MODEL_KEY,
    PROCESSED_PREFIX,
    RAW_KEY,
)


def get_aws_identity() -> Dict[str, Any]:
    """
    Obtiene la identidad AWS activa.

    Sirve como evidencia de que la ejecución se realizó con el rol
    correspondiente del laboratorio AWS.
    """
    sts = boto3.client("sts")
    return sts.get_caller_identity()


def s3_object_exists(bucket: str, key: str) -> bool:
    """
    Valida si existe un objeto específico en S3.
    """
    s3 = boto3.client("s3")

    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code")

        if code in {"404", "NoSuchKey", "NotFound"}:
            return False

        raise


def s3_prefix_has_objects(bucket: str, prefix: str) -> bool:
    """
    Valida si un prefijo S3 contiene al menos un objeto.

    En S3 las carpetas son prefijos, por eso se valida si existe
    al menos un archivo bajo la ruta indicada.
    """
    s3 = boto3.client("s3")

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix,
        MaxKeys=1,
    )

    return response.get("KeyCount", 0) > 0


def validate_s3_inputs(bucket: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Valida las rutas base del proyecto en S3.

    Esta función se ejecuta antes y después del batch para dejar evidencia
    de los insumos y artefactos principales.
    """
    logger.info("[START] Validando rutas base en S3")

    checks = {
        "raw_dataset": s3_object_exists(bucket, RAW_KEY),
        "processed_prefix": s3_prefix_has_objects(bucket, PROCESSED_PREFIX),
        "model_joblib": s3_object_exists(bucket, MODEL_KEY),
        "model_metrics": s3_object_exists(bucket, METRICS_KEY),
    }

    for name, ok in checks.items():
        if ok:
            logger.info("[OK] S3 validado: %s", name)
        else:
            logger.warning("[WARN] No encontrado en S3: %s", name)

    logger.info("[END] Validación S3 finalizada")

    return checks