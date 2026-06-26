import argparse
import tarfile
from pathlib import Path

import boto3


DEFAULT_BUCKET = "bigdata-salmonicultura-fabian"
DEFAULT_MODEL_KEY = "models/low_growth_logistic_model.joblib"
DEFAULT_OUTPUT_KEY = "sagemaker/model-artifacts/low_growth_model.tar.gz"


def download_model(bucket: str, model_key: str, local_model_path: Path) -> None:
    local_model_path.parent.mkdir(parents=True, exist_ok=True)

    s3 = boto3.client("s3")
    s3.download_file(bucket, model_key, str(local_model_path))

    print(f"Modelo descargado desde s3://{bucket}/{model_key}")
    print(f"Ruta local: {local_model_path}")


def create_tar(local_model_path: Path, tar_path: Path) -> None:
    tar_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(local_model_path, arcname="low_growth_logistic_model.joblib")

    print(f"Artefacto creado: {tar_path}")


def upload_artifact(bucket: str, output_key: str, tar_path: Path) -> None:
    s3 = boto3.client("s3")
    s3.upload_file(str(tar_path), bucket, output_key)

    print(f"Artefacto subido a s3://{bucket}/{output_key}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Empaqueta el modelo existente para SageMaker."
    )

    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--model-key", default=DEFAULT_MODEL_KEY)
    parser.add_argument("--output-key", default=DEFAULT_OUTPUT_KEY)

    args = parser.parse_args()

    workdir = Path("outputs/sagemaker_model")
    local_model_path = workdir / "low_growth_logistic_model.joblib"
    tar_path = workdir / "low_growth_model.tar.gz"

    download_model(args.bucket, args.model_key, local_model_path)
    create_tar(local_model_path, tar_path)
    upload_artifact(args.bucket, args.output_key, tar_path)

    print("Empaquetado finalizado correctamente.")


if __name__ == "__main__":
    main()