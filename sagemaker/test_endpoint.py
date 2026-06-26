import argparse
import json

import boto3


DEFAULT_PAYLOAD = {
    "feed_per_open_biomass": 0.296827,
    "feed_per_fish": 0.002963,
    "temperature_avg": 12.05714286,
    "density_avg": 30.54454607,
    "mortality_rate": 0.0000548,
    "open_biomass": 754.6475011,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prueba un endpoint SageMaker del modelo low_growth."
    )

    parser.add_argument("--endpoint-name", required=True)

    args = parser.parse_args()

    runtime = boto3.client("sagemaker-runtime")

    response = runtime.invoke_endpoint(
        EndpointName=args.endpoint_name,
        ContentType="application/json",
        Accept="application/json",
        Body=json.dumps(DEFAULT_PAYLOAD),
    )

    body = response["Body"].read().decode("utf-8")

    print("Payload enviado:")
    print(json.dumps(DEFAULT_PAYLOAD, indent=2))

    print("\nRespuesta del endpoint:")
    print(body)


if __name__ == "__main__":
    main()