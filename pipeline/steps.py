"""
Pasos ejecutables del pipeline end-to-end.

Este módulo concentra las acciones principales:
- ejecutar notebooks batch;
- empaquetar modelo para SageMaker;
- desplegar endpoint;
- probar endpoint;
- ejecutar simulador streaming;
- eliminar endpoint.
"""

import logging
import re
import sys
from pathlib import Path
from typing import List

from pipeline.command_runner import run_command
from pipeline.config import NOTEBOOKS


def execute_notebooks(
    run_dir: Path,
    logger: logging.Logger,
    timeout: int,
) -> List[str]:
    """
    Ejecuta los notebooks batch usando nbconvert.

    Los notebooks ejecutados se guardan como evidencia dentro de:

    outputs/runs/run_YYYYMMDD_HHMMSS/notebooks_executed/
    """
    logger.info("[START] Ejecución de notebooks batch")

    executed_paths: List[str] = []
    notebook_output_dir = run_dir / "notebooks_executed"
    notebook_output_dir.mkdir(parents=True, exist_ok=True)

    for notebook_path in NOTEBOOKS:
        notebook = Path(notebook_path)
        output_name = notebook.stem + "_executed.ipynb"

        run_command(
            [
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                str(notebook),
                "--output",
                output_name,
                "--output-dir",
                str(notebook_output_dir),
                f"--ExecutePreprocessor.timeout={timeout}",
            ],
            logger=logger,
        )

        executed_path = notebook_output_dir / output_name
        executed_paths.append(str(executed_path))
        logger.info("[OK] Notebook ejecutado: %s", executed_path)

    logger.info("[END] Ejecución de notebooks batch finalizada")

    return executed_paths


def package_sagemaker_model(logger: logging.Logger) -> str:
    """
    Ejecuta el empaquetado del modelo para SageMaker.

    Este paso usa el script existente:
    sagemaker/package_model.py
    """
    logger.info("[START] Empaquetando modelo para SageMaker")

    output = run_command(
        [sys.executable, "sagemaker/package_model.py"],
        logger=logger,
    )

    logger.info("[END] Empaquetado SageMaker finalizado")

    return output


def deploy_sagemaker_endpoint(logger: logging.Logger) -> str:
    """
    Despliega un endpoint SageMaker temporal.

    El nombre del endpoint se captura desde la salida del script
    sagemaker/deploy_endpoint.py.
    """
    logger.info("[START] Desplegando endpoint SageMaker")

    output = run_command(
        [sys.executable, "sagemaker/deploy_endpoint.py"],
        logger=logger,
    )

    match = re.search(r"EndpointName:\s*([A-Za-z0-9-]+)", output)

    if not match:
        raise RuntimeError("No se pudo capturar EndpointName desde deploy_endpoint.py")

    endpoint_name = match.group(1)

    logger.info("[OK] Endpoint capturado: %s", endpoint_name)
    logger.info("[END] Despliegue endpoint SageMaker finalizado")

    return endpoint_name


def test_sagemaker_endpoint(endpoint_name: str, logger: logging.Logger) -> str:
    """
    Ejecuta una predicción puntual contra el endpoint SageMaker.

    Esta prueba confirma que el endpoint responde antes de enviarle
    eventos generados por el simulador streaming.
    """
    logger.info("[START] Probando endpoint SageMaker")

    output = run_command(
        [
            sys.executable,
            "sagemaker/test_endpoint.py",
            "--endpoint-name",
            endpoint_name,
        ],
        logger=logger,
    )

    logger.info("[END] Prueba endpoint SageMaker finalizada")

    return output


def run_streaming_simulator(
    endpoint_name: str,
    events: int,
    interval_seconds: float,
    upload_every: int,
    logger: logging.Logger,
) -> str:
    """
    Ejecuta el simulador streaming contra el endpoint SageMaker.

    El parámetro upload_every permite subir resultados parciales a S3 cada N
    eventos. Esto facilita una demostración con Grafana, porque los archivos
    de salida se van actualizando mientras el simulador corre.
    """
    logger.info("[START] Ejecutando simulador streaming")

    command = [
        sys.executable,
        "-u",
        "streaming/simulate_streaming_inference.py",
        "--endpoint-name",
        endpoint_name,
        "--events",
        str(events),
        "--interval-seconds",
        str(interval_seconds),
        "--upload-s3",
    ]

    # Si upload_every es mayor a 0, se activa la carga incremental a S3.
    if upload_every > 0:
        command.extend(["--upload-every", str(upload_every)])

    output = run_command(
        command,
        logger=logger,
    )

    logger.info("[END] Simulador streaming finalizado")

    return output


def delete_sagemaker_endpoint(endpoint_name: str, logger: logging.Logger) -> None:
    """
    Elimina endpoint, endpoint config y modelo SageMaker temporal.

    Esto evita dejar recursos activos consumiendo presupuesto del laboratorio.
    """
    logger.info("[START] Eliminando endpoint SageMaker")

    run_command(
        [
            sys.executable,
            "sagemaker/delete_endpoint.py",
            "--endpoint-name",
            endpoint_name,
        ],
        logger=logger,
    )

    logger.info("[END] Eliminación endpoint SageMaker finalizada")


def list_active_low_growth_endpoints(logger: logging.Logger) -> str:
    """
    Lista endpoints activos relacionados con low-growth.

    Se usa al final del pipeline para demostrar que no quedaron endpoints
    activos asociados al modelo.
    """
    logger.info("[START] Validando endpoints activos low-growth")

    output = run_command(
        [
            "aws",
            "sagemaker",
            "list-endpoints",
            "--name-contains",
            "low-growth-endpoint",
        ],
        logger=logger,
    )

    logger.info("[END] Validación endpoints activos finalizada")

    return output