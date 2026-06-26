import argparse
import time

import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel


DEFAULT_BUCKET = "bigdata-salmonicultura-fabian"
DEFAULT_MODEL_ARTIFACT_KEY = "sagemaker/model-artifacts/low_growth_model.tar.gz"
DEFAULT_INSTANCE_TYPE = "ml.m5.large"
DEFAULT_FRAMEWORK_VERSION = "1.4-2"


def get_default_role_arn() -> str:
    """
    Construye el ARN del rol LabRole a partir de la cuenta AWS activa.
    """
    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    return f"arn:aws:iam::{account_id}:role/LabRole"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Despliega el modelo low_growth en un endpoint SageMaker."
    )

    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--model-artifact-key", default=DEFAULT_MODEL_ARTIFACT_KEY)
    parser.add_argument("--instance-type", default=DEFAULT_INSTANCE_TYPE)
    parser.add_argument("--framework-version", default=DEFAULT_FRAMEWORK_VERSION)
    parser.add_argument("--role-arn", default=None)
    parser.add_argument("--endpoint-name", default=None)

    args = parser.parse_args()

    role_arn = args.role_arn or get_default_role_arn()
    timestamp = int(time.time())

    endpoint_name = args.endpoint_name or f"low-growth-endpoint-{timestamp}"
    model_name = f"low-growth-model-{timestamp}"

    model_data = f"s3://{args.bucket}/{args.model_artifact_key}"

    session = sagemaker.Session()

    print("Configuración de despliegue:")
    print("Modelo:", model_data)
    print("Rol:", role_arn)
    print("Instancia:", args.instance_type)
    print("Framework:", args.framework_version)
    print("Endpoint:", endpoint_name)

    model = SKLearnModel(
        name=model_name,
        model_data=model_data,
        role=role_arn,
        entry_point="inference.py",
        source_dir="sagemaker",
        framework_version=args.framework_version,
        py_version="py3",
        sagemaker_session=session,
    )

    model.deploy(
        initial_instance_count=1,
        instance_type=args.instance_type,
        endpoint_name=endpoint_name,
        wait=True,
    )

    print("Endpoint creado correctamente.")
    print("EndpointName:", endpoint_name)
    print("ModelName:", model_name)


if __name__ == "__main__":
    main()