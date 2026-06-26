"""
Orquestador principal del pipeline end-to-end.

Este archivo no concentra toda la lógica interna. Su responsabilidad es coordinar
los módulos del pipeline y dejar evidencia trazable de la ejecución.
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pipeline.aws_checks import (
    get_aws_identity,
    s3_object_exists,
    validate_s3_inputs,
)
from pipeline.command_runner import setup_logging
from pipeline.config import (
    DEFAULT_BUCKET,
    SAGEMAKER_ARTIFACT_KEY,
)
from pipeline.steps import (
    delete_sagemaker_endpoint,
    deploy_sagemaker_endpoint,
    execute_notebooks,
    list_active_low_growth_endpoints,
    package_sagemaker_model,
    run_streaming_simulator,
    test_sagemaker_endpoint,
)
from pipeline.summary import (
    extract_s3_paths_from_output,
    upload_run_artifacts,
    write_summary,
)


def utc_now_compact() -> str:
    """
    Retorna fecha/hora UTC en formato compacto para usar en nombres de corrida.
    """
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def utc_now_iso() -> str:
    """
    Retorna fecha/hora UTC en formato ISO para registrar trazabilidad.
    """
    return datetime.now(timezone.utc).isoformat()


def build_initial_summary(
    run_id: str,
    bucket: str,
    events: int,
    interval_seconds: float,
    skip_notebooks: bool,
) -> Dict[str, Any]:
    """
    Construye el resumen inicial de la corrida.

    Este diccionario se completa durante la ejecución y luego se guarda como
    run_summary.json.
    """
    return {
        "run_id": run_id,
        "started_at": utc_now_iso(),
        "finished_at": None,
        "status": "running",
        "bucket": bucket,
        "events_requested": events,
        "interval_seconds": interval_seconds,
        "skip_notebooks": skip_notebooks,
        "endpoint_name": None,
        "s3_checks": {},
        "s3_checks_after_batch": {},
        "executed_notebooks": [],
        "streaming_s3_paths": [],
        "pipeline_artifacts_s3": {},
        "error": None,
    }


def main() -> None:
    """
    Ejecuta el flujo end-to-end del proyecto.

    Flujo general:
    1. Validar identidad AWS.
    2. Validar rutas base en S3.
    3. Ejecutar notebooks batch, salvo que se use --skip-notebooks.
    4. Validar artefactos batch.
    5. Empaquetar modelo para SageMaker.
    6. Crear endpoint SageMaker temporal.
    7. Probar endpoint.
    8. Ejecutar simulador streaming.
    9. Eliminar endpoint.
    10. Guardar logs y resumen JSON.
    11. Subir evidencia a S3.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline end-to-end trazable del proyecto Big Data salmonicultura."
    )

    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--events", type=int, default=30)
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--notebook-timeout", type=int, default=-1)

    # Permite ejecutar solo SageMaker + streaming sin volver a correr notebooks.
    parser.add_argument("--skip-notebooks", action="store_true")

    # Permite mantener el endpoint para depuración.
    # No se recomienda para la entrega final, porque deja recursos activos.
    parser.add_argument("--keep-endpoint", action="store_true")

    args = parser.parse_args()

    run_id = f"run_{utc_now_compact()}"
    run_dir = Path("outputs/runs") / run_id

    logger = setup_logging(run_dir)

    endpoint_name: Optional[str] = None

    summary = build_initial_summary(
        run_id=run_id,
        bucket=args.bucket,
        events=args.events,
        interval_seconds=args.interval_seconds,
        skip_notebooks=args.skip_notebooks,
    )

    logger.info("[START] Pipeline end-to-end salmonicultura")
    logger.info("Run ID: %s", run_id)

    try:
        # ------------------------------------------------------------
        # 1. Validación de identidad AWS
        # ------------------------------------------------------------
        identity = get_aws_identity()
        summary["aws_identity"] = identity
        logger.info("[OK] AWS identity validada: %s", identity.get("Arn"))

        # ------------------------------------------------------------
        # 2. Validación inicial de insumos y artefactos en S3
        # ------------------------------------------------------------
        summary["s3_checks"] = validate_s3_inputs(args.bucket, logger)

        # ------------------------------------------------------------
        # 3. Ejecución opcional de notebooks batch
        # ------------------------------------------------------------
        if args.skip_notebooks:
            logger.info("[SKIP] Ejecución de notebooks omitida por parámetro")
        else:
            summary["executed_notebooks"] = execute_notebooks(
                run_dir=run_dir,
                logger=logger,
                timeout=args.notebook_timeout,
            )

        # ------------------------------------------------------------
        # 4. Validación posterior al batch
        # ------------------------------------------------------------
        summary["s3_checks_after_batch"] = validate_s3_inputs(args.bucket, logger)

        # ------------------------------------------------------------
        # 5. Empaquetado del modelo para SageMaker
        # ------------------------------------------------------------
        package_sagemaker_model(logger)

        if not s3_object_exists(args.bucket, SAGEMAKER_ARTIFACT_KEY):
            raise RuntimeError(
                f"No se encontró artefacto SageMaker en "
                f"s3://{args.bucket}/{SAGEMAKER_ARTIFACT_KEY}"
            )

        logger.info(
            "[OK] Artefacto SageMaker validado: s3://%s/%s",
            args.bucket,
            SAGEMAKER_ARTIFACT_KEY,
        )

        # ------------------------------------------------------------
        # 6. Despliegue temporal del endpoint SageMaker
        # ------------------------------------------------------------
        endpoint_name = deploy_sagemaker_endpoint(logger)
        summary["endpoint_name"] = endpoint_name

        # ------------------------------------------------------------
        # 7. Prueba puntual del endpoint
        # ------------------------------------------------------------
        test_sagemaker_endpoint(endpoint_name, logger)

        # ------------------------------------------------------------
        # 8. Ejecución del simulador streaming
        # ------------------------------------------------------------
        streaming_output = run_streaming_simulator(
            endpoint_name=endpoint_name,
            events=args.events,
            interval_seconds=args.interval_seconds,
            logger=logger,
        )

        summary["streaming_s3_paths"] = extract_s3_paths_from_output(streaming_output)

        # ------------------------------------------------------------
        # 9. Eliminación del endpoint temporal
        # ------------------------------------------------------------
        if args.keep_endpoint:
            logger.warning("[WARN] Endpoint se mantiene activo por parámetro --keep-endpoint")
        else:
            delete_sagemaker_endpoint(endpoint_name, logger)
            endpoint_name = None

        # ------------------------------------------------------------
        # 10. Validación final de endpoints activos
        # ------------------------------------------------------------
        list_active_low_growth_endpoints(logger)

        summary["status"] = "success"
        logger.info("[END] Pipeline completado correctamente")

    except Exception as error:
        # ------------------------------------------------------------
        # Manejo centralizado de errores
        # ------------------------------------------------------------
        summary["status"] = "failed"
        summary["error"] = str(error)

        logger.exception("[ERROR] Pipeline falló: %s", error)

        # Si el pipeline falla después de crear un endpoint, se intenta
        # eliminar automáticamente para evitar consumo innecesario.
        if endpoint_name and not args.keep_endpoint:
            logger.warning("[CLEANUP] Intentando eliminar endpoint por falla: %s", endpoint_name)

            try:
                delete_sagemaker_endpoint(endpoint_name, logger)
                endpoint_name = None
            except Exception as cleanup_error:
                logger.exception("[ERROR] Falló cleanup de endpoint: %s", cleanup_error)

        raise

    finally:
        # ------------------------------------------------------------
        # 11. Escritura local y subida a S3 de evidencias
        # ------------------------------------------------------------
        summary["finished_at"] = utc_now_iso()

        summary_path = write_summary(run_dir, summary)
        logger.info("[OK] Resumen local generado: %s", summary_path)

        try:
            uploaded = upload_run_artifacts(
                bucket=args.bucket,
                run_id=run_id,
                run_dir=run_dir,
                logger=logger,
            )

            summary["pipeline_artifacts_s3"] = uploaded

            # Se reescribe el resumen para incluir las rutas S3 de evidencia.
            write_summary(run_dir, summary)

            # Se vuelve a subir el summary actualizado.
            upload_run_artifacts(
                bucket=args.bucket,
                run_id=run_id,
                run_dir=run_dir,
                logger=logger,
            )

        except Exception as upload_error:
            logger.exception("[ERROR] No se pudo subir evidencia del pipeline: %s", upload_error)

        logger.info("Run dir local: %s", run_dir)


if __name__ == "__main__":
    main()