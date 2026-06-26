"""
Funciones para generar y subir evidencias del pipeline.

El pipeline produce dos evidencias principales por corrida:
- pipeline.log
- run_summary.json
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

import boto3


def extract_s3_paths_from_output(output: str) -> List[str]:
    """
    Extrae rutas S3 desde una salida de consola.

    Se usa para capturar automáticamente las rutas que imprime el simulador
    cuando sube resultados a S3.
    """
    return re.findall(r"s3://[^\s]+", output)


def write_summary(run_dir: Path, summary: Dict[str, Any]) -> Path:
    """
    Escribe el resumen JSON de la corrida.

    Este archivo funciona como evidencia estructurada del pipeline.
    """
    summary_path = run_dir / "run_summary.json"

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    return summary_path


def upload_run_artifacts(
    bucket: str,
    run_id: str,
    run_dir: Path,
    logger: logging.Logger,
) -> Dict[str, str]:
    """
    Sube a S3 los artefactos principales de la corrida:
    - pipeline.log
    - run_summary.json
    """
    logger.info("[START] Subiendo evidencia del pipeline a S3")

    s3 = boto3.client("s3")

    artifacts = {
        "pipeline_log": run_dir / "pipeline.log",
        "run_summary": run_dir / "run_summary.json",
    }

    uploaded: Dict[str, str] = {}

    for artifact_name, local_path in artifacts.items():
        if not local_path.exists():
            logger.warning("[WARN] Artefacto no encontrado, no se sube: %s", local_path)
            continue

        key = f"pipeline_runs/{run_id}/{local_path.name}"
        s3.upload_file(str(local_path), bucket, key)

        s3_uri = f"s3://{bucket}/{key}"
        uploaded[artifact_name] = s3_uri
        logger.info("[OK] Artefacto subido: %s", s3_uri)

    logger.info("[END] Evidencia del pipeline subida a S3")

    return uploaded