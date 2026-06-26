"""
Sincronizador de resultados streaming hacia SQLite para Grafana.

Este script permite tomar los resultados generados por el simulador streaming
y cargarlos en una base SQLite local. La base queda preparada para ser leída
por Grafana mediante el plugin de SQLite.

Puede trabajar de dos formas:

1. Desde S3:
   - busca el último run dentro del prefijo streaming/inference_events/
   - descarga inference_events.csv
   - lo carga en SQLite

2. Desde un CSV local:
   - útil para pruebas locales sin depender de credenciales AWS
"""

import argparse
import sqlite3
from pathlib import Path
from typing import Optional

import boto3
import pandas as pd


DEFAULT_BUCKET = "bigdata-salmonicultura-fabian"
DEFAULT_S3_PREFIX = "streaming/inference_events"
DEFAULT_OUTPUT_DB = Path("data/grafana/salmonicultura.db")
DEFAULT_TABLE = "streaming_predictions"
DEFAULT_DOWNLOAD_DIR = Path("outputs/grafana_sync")


def find_latest_streaming_run(bucket: str, s3_prefix: str) -> str:
    """
    Busca el último run streaming disponible en S3.

    Se asume una estructura como:

    streaming/inference_events/run_YYYYMMDD_HHMMSS/inference_events.csv
    """
    s3 = boto3.client("s3")

    paginator = s3.get_paginator("list_objects_v2")

    latest_key: Optional[str] = None
    latest_modified = None

    for page in paginator.paginate(Bucket=bucket, Prefix=s3_prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if not key.endswith("inference_events.csv"):
                continue

            modified = obj["LastModified"]

            if latest_modified is None or modified > latest_modified:
                latest_modified = modified
                latest_key = key

    if latest_key is None:
        raise FileNotFoundError(
            f"No se encontraron archivos inference_events.csv en "
            f"s3://{bucket}/{s3_prefix}/"
        )

    parts = latest_key.split("/")

    # Estructura esperada:
    # streaming / inference_events / run_YYYYMMDD_HHMMSS / inference_events.csv
    if len(parts) < 4:
        raise ValueError(f"No se pudo obtener run_id desde la ruta S3: {latest_key}")

    return parts[-2]


def download_streaming_csv(
    bucket: str,
    s3_prefix: str,
    run_id: str,
    download_dir: Path,
) -> Path:
    """
    Descarga el CSV de resultados streaming desde S3.
    """
    s3 = boto3.client("s3")

    download_dir.mkdir(parents=True, exist_ok=True)

    s3_key = f"{s3_prefix}/{run_id}/inference_events.csv"
    local_path = download_dir / f"{run_id}_inference_events.csv"

    s3.download_file(bucket, s3_key, str(local_path))

    print(f"CSV descargado desde s3://{bucket}/{s3_key}")
    print(f"Ruta local: {local_path}")

    return local_path


def load_streaming_csv(csv_path: Path) -> pd.DataFrame:
    """
    Lee el CSV streaming y normaliza columnas útiles para Grafana.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el archivo CSV: {csv_path}")

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError(f"El CSV no contiene registros: {csv_path}")

    # Normalización de fechas para facilitar consultas temporales en Grafana.
    if "processed_timestamp" in df.columns:
        df["processed_timestamp"] = pd.to_datetime(
            df["processed_timestamp"],
            errors="coerce",
            utc=True,
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    if "event_timestamp" in df.columns:
        df["event_timestamp"] = pd.to_datetime(
            df["event_timestamp"],
            errors="coerce",
            utc=True,
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Campos derivados para consultas y paneles.
    if "prediction" in df.columns:
        df["is_low_growth"] = df["prediction"].fillna(0).astype(int)

    if "probability_low_growth" in df.columns:
        df["probability_low_growth_pct"] = df["probability_low_growth"] * 100

    if "scenario" in df.columns:
        df["is_risk_scenario"] = (df["scenario"] == "risk").astype(int)

    # ID incremental para ordenar en Grafana cuando no se use fecha.
    df.insert(0, "grafana_row_id", range(1, len(df) + 1))

    return df


def write_sqlite(
    df: pd.DataFrame,
    db_path: Path,
    table_name: str,
) -> None:
    """
    Escribe el DataFrame en SQLite.

    Se reemplaza la tabla completa en cada sincronización, porque la fuente
    oficial de esta etapa es el CSV generado por el pipeline.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        # Vista simple para KPIs generales.
        conn.execute(
            f"""
            CREATE VIEW IF NOT EXISTS vw_streaming_kpis AS
            SELECT
                COUNT(*) AS total_events,
                SUM(CASE WHEN is_low_growth = 1 THEN 1 ELSE 0 END) AS low_growth_events,
                AVG(probability_low_growth) AS avg_probability_low_growth,
                AVG(probability_low_growth_pct) AS avg_probability_low_growth_pct,
                SUM(CASE WHEN scenario = 'risk' THEN 1 ELSE 0 END) AS risk_events,
                SUM(CASE WHEN scenario = 'normal' THEN 1 ELSE 0 END) AS normal_events
            FROM {table_name};
            """
        )

        # Vista para series temporales.
        conn.execute(
            f"""
            CREATE VIEW IF NOT EXISTS vw_streaming_timeseries AS
            SELECT
                grafana_row_id,
                processed_timestamp,
                event_timestamp,
                site,
                unit,
                species,
                scenario,
                prediction,
                is_low_growth,
                probability_low_growth,
                probability_low_growth_pct,
                temperature_avg,
                density_avg,
                mortality_rate,
                feed_per_open_biomass,
                feed_per_fish,
                open_biomass
            FROM {table_name};
            """
        )

    print(f"Base SQLite actualizada: {db_path}")
    print(f"Tabla principal: {table_name}")
    print(f"Registros cargados: {len(df)}")


def print_validation_summary(df: pd.DataFrame) -> None:
    """
    Muestra un resumen breve para validar la carga.
    """
    total_events = len(df)

    low_growth_events = (
        int(df["is_low_growth"].sum())
        if "is_low_growth" in df.columns
        else 0
    )

    avg_probability = (
        float(df["probability_low_growth"].mean())
        if "probability_low_growth" in df.columns
        else 0.0
    )

    print("Resumen de carga:")
    print(f"- eventos totales: {total_events}")
    print(f"- eventos con bajo crecimiento: {low_growth_events}")
    print(f"- probabilidad promedio bajo crecimiento: {avg_probability:.4f}")

    if "scenario" in df.columns:
        print("- eventos por escenario:")
        print(df["scenario"].value_counts().to_string())


def main() -> None:
    """
    Punto de entrada del sincronizador.
    """
    parser = argparse.ArgumentParser(
        description="Sincroniza resultados streaming hacia SQLite para Grafana."
    )

    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--s3-prefix", default=DEFAULT_S3_PREFIX)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--csv-path", default=None)
    parser.add_argument("--output-db", default=str(DEFAULT_OUTPUT_DB))
    parser.add_argument("--table-name", default=DEFAULT_TABLE)
    parser.add_argument("--download-dir", default=str(DEFAULT_DOWNLOAD_DIR))

    args = parser.parse_args()

    output_db = Path(args.output_db)

    if args.csv_path:
        csv_path = Path(args.csv_path)
        print(f"Usando CSV local: {csv_path}")
    else:
        run_id = args.run_id

        if run_id is None:
            run_id = find_latest_streaming_run(
                bucket=args.bucket,
                s3_prefix=args.s3_prefix,
            )
            print(f"Último run streaming detectado: {run_id}")

        csv_path = download_streaming_csv(
            bucket=args.bucket,
            s3_prefix=args.s3_prefix,
            run_id=run_id,
            download_dir=Path(args.download_dir),
        )

    df = load_streaming_csv(csv_path)

    write_sqlite(
        df=df,
        db_path=output_db,
        table_name=args.table_name,
    )

    print_validation_summary(df)


if __name__ == "__main__":
    main()