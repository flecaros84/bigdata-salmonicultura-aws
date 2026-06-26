"""
Utilidades para ejecutar comandos externos y configurar logs.

El pipeline coordina scripts ya existentes del proyecto, por ejemplo:
- scripts de SageMaker;
- simulador streaming;
- ejecución de notebooks con nbconvert.

Para mantener trazabilidad, cada comando registra su salida en consola
y en el archivo pipeline.log.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def setup_logging(run_dir: Path) -> logging.Logger:
    """
    Configura un logger que escribe simultáneamente en consola y archivo.

    Cada corrida genera su propio directorio:

    outputs/runs/run_YYYYMMDD_HHMMSS/pipeline.log
    """
    run_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("pipeline_end_to_end")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_path = run_dir / "pipeline.log"

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def run_command(
    command: List[str],
    logger: logging.Logger,
    cwd: Optional[Path] = None,
) -> str:
    """
    Ejecuta un comando del sistema y registra toda su salida.

    Si el comando termina con código distinto de cero, se lanza un error
    para detener el pipeline y activar el manejo de limpieza.
    """
    logger.info("Ejecutando comando: %s", " ".join(command))

    process = subprocess.Popen(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    output_lines: List[str] = []

    assert process.stdout is not None

    # Se registra línea por línea para dejar trazabilidad durante la ejecución.
    for line in process.stdout:
        clean_line = line.rstrip()
        output_lines.append(clean_line)
        logger.info(clean_line)

    return_code = process.wait()
    output = "\n".join(output_lines)

    if return_code != 0:
        raise RuntimeError(
            f"Comando falló con código {return_code}: {' '.join(command)}"
        )

    return output