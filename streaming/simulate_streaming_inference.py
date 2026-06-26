import argparse
import csv
import json
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import boto3


# ============================================================
# Configuración general del simulador
# ============================================================

DEFAULT_BUCKET = "bigdata-salmonicultura-fabian"
DEFAULT_S3_PREFIX = "streaming/inference_events"
DEFAULT_OUTPUT_DIR = Path("outputs/streaming")

SPECIES_VALUES = ["Atlantic Salmon", "Coho Salmon", "Rainbow Trout"]

SITE_VALUES = [
    "SITE_001",
    "SITE_002",
    "SITE_003",
    "SITE_004",
    "SITE_005",
]


# ============================================================
# Utilidades de fecha
# ============================================================

def utc_now_iso() -> str:
    """
    Retorna la fecha/hora actual en UTC con formato ISO.
    Se usa para trazabilidad de eventos.
    """
    return datetime.now(timezone.utc).isoformat()


def build_streaming_run_id() -> str:
    """
    Genera un identificador único para la corrida streaming.

    Este run_id se usa para crear una carpeta estable en S3.
    Durante la subida incremental, los archivos se sobrescriben dentro
    de esa misma carpeta, permitiendo que Grafana o un exporter lean
    siempre la versión más reciente.
    """
    return datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")


# ============================================================
# Generación de eventos simulados
# ============================================================

def generate_raw_event(event_id: int) -> Dict[str, Any]:
    """
    Genera un evento productivo simulado con estructura cercana al dataset RAW original.

    Se incorporan dos escenarios:
    - normal: condiciones productivas más estables;
    - risk: condiciones más exigentes o de mayor riesgo.
    """
    open_count = random.randint(80_000, 950_000)
    open_biomass = round(random.uniform(100.0, 4_500.0), 4)
    open_weight = round(open_biomass * 1000 / max(open_count, 1), 6)

    scenario = random.choices(
        population=["normal", "risk"],
        weights=[0.65, 0.35],
        k=1,
    )[0]

    if scenario == "normal":
        feed_per_biomass = random.uniform(0.18, 0.38)
        temperature_avg = round(random.uniform(10.0, 14.0), 6)
        density_avg = round(random.uniform(10.0, 26.0), 6)
        mortality_factor = random.uniform(0.0001, 0.0008)
    else:
        feed_per_biomass = random.uniform(0.001, 0.08)
        temperature_avg = round(
            random.choice(
                [
                    random.uniform(6.5, 9.0),
                    random.uniform(14.5, 16.5),
                ]
            ),
            6,
        )
        density_avg = round(random.uniform(26.0, 38.0), 6)
        mortality_factor = random.uniform(0.001, 0.003)

    feed_weight = round(open_biomass * feed_per_biomass, 6)

    live_days = random.randint(5, 7)
    fish_days = open_count * live_days

    mortality_count = random.randint(
        0,
        max(1, int(open_count * mortality_factor)),
    )

    harvest_count = random.randint(0, max(1, int(open_count * 0.002)))
    ship_out_count = random.randint(0, max(1, int(open_count * 0.001)))
    ship_in_count = random.randint(0, max(1, int(open_count * 0.001)))

    biomass_variation_factor = random.uniform(-0.015, 0.025)
    close_biomass = round(open_biomass * (1 + biomass_variation_factor), 4)

    year_value = datetime.now().year
    week_value = int(datetime.now().strftime("%U"))

    return {
        "event_id": event_id,
        "event_timestamp": utc_now_iso(),
        "Site": random.choice(SITE_VALUES),
        "Unit": f"UNIT_{random.randint(1, 80):03d}",
        "Year": year_value,
        "Week": week_value,
        "Species": random.choice(SPECIES_VALUES),
        "Scenario": scenario,
        "Year class": random.randint(year_value - 4, year_value),
        "Open Count": open_count,
        "Open Biomass": open_biomass,
        "Open Weight": open_weight,
        "Feed Weight": feed_weight,
        "Temperature Avg": temperature_avg,
        "Density Avg": density_avg,
        "Live Days": live_days,
        "Fish Days": fish_days,
        "Mortality Count": mortality_count,
        "Harvest Count": harvest_count,
        "Ship Out Count": ship_out_count,
        "Ship In Count": ship_in_count,
        "Close Biomass": close_biomass,
    }


def calculate_features(raw_event: Dict[str, Any]) -> Dict[str, float]:
    """
    Calcula las features requeridas por el modelo desplegado en SageMaker.
    """
    open_count = float(raw_event["Open Count"])
    open_biomass = float(raw_event["Open Biomass"])
    feed_weight = float(raw_event["Feed Weight"])
    fish_days = float(raw_event["Fish Days"])
    mortality_count = float(raw_event["Mortality Count"])

    return {
        "feed_per_open_biomass": feed_weight / open_biomass if open_biomass > 0 else 0.0,
        "feed_per_fish": feed_weight / open_count if open_count > 0 else 0.0,
        "temperature_avg": float(raw_event["Temperature Avg"]),
        "density_avg": float(raw_event["Density Avg"]),
        "mortality_rate": mortality_count / fish_days if fish_days > 0 else 0.0,
        "open_biomass": open_biomass,
    }


# ============================================================
# Inferencia SageMaker
# ============================================================

def invoke_sagemaker_endpoint(
    endpoint_name: str,
    features: Dict[str, float],
) -> Dict[str, Any]:
    """
    Envía las features al endpoint SageMaker y devuelve la respuesta del modelo.
    """
    runtime = boto3.client("sagemaker-runtime")

    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Accept="application/json",
        Body=json.dumps(features),
    )

    body = response["Body"].read().decode("utf-8")
    return json.loads(body)


def build_result_record(
    raw_event: Dict[str, Any],
    features: Dict[str, float],
    prediction_response: Dict[str, Any],
    endpoint_name: str,
) -> Dict[str, Any]:
    """
    Consolida evento RAW, features y predicción en un registro trazable.
    """
    predictions = prediction_response.get("predictions", [])
    probabilities = prediction_response.get("probabilities", [])

    prediction = predictions[0] if predictions else None
    probability_low_growth = probabilities[0] if probabilities else None

    return {
        "processed_timestamp": utc_now_iso(),
        "endpoint_name": endpoint_name,
        "event_id": raw_event["event_id"],
        "event_timestamp": raw_event["event_timestamp"],
        "site": raw_event["Site"],
        "unit": raw_event["Unit"],
        "species": raw_event["Species"],
        "scenario": raw_event.get("Scenario"),
        "year": raw_event["Year"],
        "week": raw_event["Week"],
        "open_count": raw_event["Open Count"],
        "open_biomass": raw_event["Open Biomass"],
        "feed_weight": raw_event["Feed Weight"],
        "temperature_avg": raw_event["Temperature Avg"],
        "density_avg": raw_event["Density Avg"],
        "mortality_count": raw_event["Mortality Count"],
        "feed_per_open_biomass": features["feed_per_open_biomass"],
        "feed_per_fish": features["feed_per_fish"],
        "mortality_rate": features["mortality_rate"],
        "prediction": prediction,
        "probability_low_growth": probability_low_growth,
        "raw_event_json": json.dumps(raw_event, ensure_ascii=False),
        "features_json": json.dumps(features, ensure_ascii=False),
        "prediction_response_json": json.dumps(prediction_response, ensure_ascii=False),
    }


# ============================================================
# Escritura local
# ============================================================

def append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    """
    Agrega un registro al archivo JSONL.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_csv(path: Path, record: Dict[str, Any]) -> None:
    """
    Agrega un registro al archivo CSV.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = path.exists()

    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(record.keys()))

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)


def clean_previous_outputs(jsonl_path: Path, csv_path: Path) -> None:
    """
    Elimina archivos locales previos para evitar mezclar corridas distintas.
    """
    if jsonl_path.exists():
        jsonl_path.unlink()

    if csv_path.exists():
        csv_path.unlink()


# ============================================================
# Subida a S3
# ============================================================

def upload_outputs_to_s3(
    bucket: str,
    s3_prefix: str,
    run_id: str,
    jsonl_path: Path,
    csv_path: Path,
    upload_label: str,
) -> None:
    """
    Sube los archivos de salida del simulador a S3.

    Se usa un mismo run_id durante toda la ejecución para que las cargas
    incrementales sobrescriban los mismos archivos. Esto permite que Grafana
    o un exporter lean siempre la versión más reciente del CSV/JSONL.
    """
    s3 = boto3.client("s3")

    jsonl_key = f"{s3_prefix}/{run_id}/inference_events.jsonl"
    csv_key = f"{s3_prefix}/{run_id}/inference_events.csv"

    s3.upload_file(str(jsonl_path), bucket, jsonl_key)
    s3.upload_file(str(csv_path), bucket, csv_key)

    print(f"Archivos subidos a S3 ({upload_label}):")
    print(f"s3://{bucket}/{jsonl_key}")
    print(f"s3://{bucket}/{csv_key}")


# ============================================================
# Control de ejecución
# ============================================================

def should_continue(event_counter: int, max_events: int) -> bool:
    """
    max_events = 0 significa ejecución continua hasta Ctrl+C.
    """
    return max_events == 0 or event_counter < max_events


def build_dry_run_prediction() -> Dict[str, Any]:
    """
    Genera una respuesta simulada del modelo para pruebas locales sin AWS.
    """
    probability = round(random.uniform(0.0, 1.0), 6)

    return {
        "predictions": [1 if probability >= 0.5 else 0],
        "probabilities": [probability],
    }


def run_simulation(
    endpoint_name: str,
    max_events: int,
    interval_seconds: float,
    output_dir: Path,
    upload_s3: bool,
    bucket: str,
    s3_prefix: str,
    dry_run: bool,
    upload_every: int,
) -> None:
    """
    Ejecuta la simulación streaming.

    Si upload_every > 0, sube archivos parciales a S3 cada N eventos.
    Si upload_every = 0, solo sube los archivos al final.
    """
    jsonl_path = output_dir / "inference_events.jsonl"
    csv_path = output_dir / "inference_events.csv"

    # Cada ejecución tiene un identificador único para trazabilidad.
    run_id = build_streaming_run_id()

    # Se limpian salidas locales previas para no mezclar corridas.
    clean_previous_outputs(jsonl_path, csv_path)

    print("Iniciando simulador de inferencia streaming")
    print(f"Endpoint SageMaker: {endpoint_name}")
    print(f"Modo dry-run: {'sí' if dry_run else 'no'}")
    print(f"Eventos configurados: {'continuo' if max_events == 0 else max_events}")
    print(f"Intervalo segundos: {interval_seconds}")
    print(f"Salida JSONL: {jsonl_path}")
    print(f"Salida CSV: {csv_path}")
    print(f"Run streaming: {run_id}")
    print(
        "Subida incremental cada N eventos: "
        f"{upload_every if upload_every > 0 else 'solo al final'}"
    )

    event_counter = 0

    try:
        while should_continue(event_counter, max_events):
            event_counter += 1

            raw_event = generate_raw_event(event_counter)
            features = calculate_features(raw_event)

            if dry_run:
                prediction_response = build_dry_run_prediction()
            else:
                prediction_response = invoke_sagemaker_endpoint(endpoint_name, features)

            result_record = build_result_record(
                raw_event=raw_event,
                features=features,
                prediction_response=prediction_response,
                endpoint_name=endpoint_name,
            )

            append_jsonl(jsonl_path, result_record)
            append_csv(csv_path, result_record)

            print(
                "Evento procesado | "
                f"id={result_record['event_id']} | "
                f"site={result_record['site']} | "
                f"scenario={result_record['scenario']} | "
                f"prediction={result_record['prediction']} | "
                f"prob_low_growth={result_record['probability_low_growth']}"
            )

            # Subida incremental para demo con Grafana o monitoreo.
            if (
                upload_s3
                and upload_every > 0
                and event_counter % upload_every == 0
                and jsonl_path.exists()
                and csv_path.exists()
            ):
                upload_outputs_to_s3(
                    bucket=bucket,
                    s3_prefix=s3_prefix,
                    run_id=run_id,
                    jsonl_path=jsonl_path,
                    csv_path=csv_path,
                    upload_label=f"incremental evento {event_counter}",
                )

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("Simulación detenida manualmente con Ctrl+C.")

    finally:
        # Al finalizar, se sube siempre la versión final de los archivos.
        # Si hubo cargas incrementales, esta carga final sobrescribe con el
        # contenido completo de la corrida.
        if upload_s3 and jsonl_path.exists() and csv_path.exists():
            upload_outputs_to_s3(
                bucket=bucket,
                s3_prefix=s3_prefix,
                run_id=run_id,
                jsonl_path=jsonl_path,
                csv_path=csv_path,
                upload_label="final",
            )

        print("Simulación finalizada.")


# ============================================================
# Entrada CLI
# ============================================================

def main() -> None:
    """
    Punto de entrada del simulador por línea de comandos.
    """
    parser = argparse.ArgumentParser(
        description="Simulador streaming de eventos productivos con inferencia SageMaker."
    )

    parser.add_argument("--endpoint-name", required=True)
    parser.add_argument("--events", type=int, default=100)
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--upload-s3", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--s3-prefix", default=DEFAULT_S3_PREFIX)

    # Si es mayor a 0, sube resultados parciales a S3 cada N eventos.
    # Si es 0, solo sube archivos al terminar la simulación.
    parser.add_argument("--upload-every", type=int, default=0)

    args = parser.parse_args()

    run_simulation(
        endpoint_name=args.endpoint_name,
        max_events=args.events,
        interval_seconds=args.interval_seconds,
        output_dir=Path(args.output_dir),
        upload_s3=args.upload_s3,
        bucket=args.bucket,
        s3_prefix=args.s3_prefix,
        dry_run=args.dry_run,
        upload_every=args.upload_every,
    )


if __name__ == "__main__":
    main()