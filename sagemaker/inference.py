import json
import os
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd


FEATURES: List[str] = [
    "feed_per_open_biomass",
    "feed_per_fish",
    "temperature_avg",
    "density_avg",
    "mortality_rate",
    "open_biomass",
]


def model_fn(model_dir: str) -> Any:
    """
    Carga el modelo entrenado desde el directorio estándar de SageMaker.
    """
    model_path = os.path.join(model_dir, "low_growth_logistic_model.joblib")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No se encontró el modelo en: {model_path}")

    return joblib.load(model_path)


def input_fn(request_body: str, request_content_type: str) -> pd.DataFrame:
    """
    Recibe un JSON con las features esperadas y lo transforma en DataFrame.
    """
    if request_content_type != "application/json":
        raise ValueError(f"Content-Type no soportado: {request_content_type}")

    payload = json.loads(request_body)

    if isinstance(payload, dict):
        records = [payload]
    elif isinstance(payload, list):
        records = payload
    else:
        raise ValueError("El payload debe ser un objeto JSON o una lista de objetos JSON.")

    df = pd.DataFrame(records)

    missing_features = [feature for feature in FEATURES if feature not in df.columns]
    if missing_features:
        raise ValueError(f"Faltan features requeridas: {missing_features}")

    df = df[FEATURES].astype(float)

    return df


def predict_fn(input_data: pd.DataFrame, model: Any) -> Dict[str, Any]:
    """
    Ejecuta la predicción usando el modelo cargado.
    """
    predictions = model.predict(input_data)

    response: Dict[str, Any] = {
        "predictions": predictions.astype(int).tolist()
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(input_data)
        response["probabilities"] = probabilities[:, 1].tolist()

    return response


def output_fn(prediction: Dict[str, Any], response_content_type: str) -> str:
    """
    Devuelve la respuesta en JSON.
    """
    if response_content_type != "application/json":
        raise ValueError(f"Accept no soportado: {response_content_type}")

    return json.dumps(prediction)