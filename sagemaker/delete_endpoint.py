import argparse

import boto3
from botocore.exceptions import ClientError


def safe_call(description: str, fn, *args, **kwargs) -> None:
    try:
        fn(*args, **kwargs)
        print(f"OK: {description}")
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "")
        if code in {"ValidationException", "ResourceNotFound"}:
            print(f"No encontrado o ya eliminado: {description}")
        else:
            raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Elimina endpoint, endpoint config y modelo SageMaker."
    )

    parser.add_argument("--endpoint-name", required=True)

    args = parser.parse_args()

    sm = boto3.client("sagemaker")

    endpoint_desc = sm.describe_endpoint(EndpointName=args.endpoint_name)
    endpoint_config_name = endpoint_desc["EndpointConfigName"]

    config_desc = sm.describe_endpoint_config(
        EndpointConfigName=endpoint_config_name
    )

    model_names = [
        variant["ModelName"]
        for variant in config_desc.get("ProductionVariants", [])
    ]

    print("Recursos a eliminar:")
    print("Endpoint:", args.endpoint_name)
    print("EndpointConfig:", endpoint_config_name)
    print("Modelos:", model_names)

    safe_call(
        f"eliminar endpoint {args.endpoint_name}",
        sm.delete_endpoint,
        EndpointName=args.endpoint_name,
    )

    waiter = sm.get_waiter("endpoint_deleted")
    waiter.wait(EndpointName=args.endpoint_name)
    print("Endpoint eliminado.")

    safe_call(
        f"eliminar endpoint config {endpoint_config_name}",
        sm.delete_endpoint_config,
        EndpointConfigName=endpoint_config_name,
    )

    for model_name in model_names:
        safe_call(
            f"eliminar modelo {model_name}",
            sm.delete_model,
            ModelName=model_name,
        )


if __name__ == "__main__":
    main()