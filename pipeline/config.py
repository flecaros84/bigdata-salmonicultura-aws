"""
Configuración central del pipeline end-to-end.

Este archivo concentra constantes del proyecto para evitar repetir rutas
S3, nombres de bucket y rutas de notebooks en distintos módulos.
"""

DEFAULT_BUCKET = "bigdata-salmonicultura-fabian"

# Rutas principales dentro del Data Lake en S3.
RAW_KEY = "raw/productive_data/productive_data.csv"
PROCESSED_PREFIX = "processed/productive_kpi/"
MODEL_KEY = "models/low_growth_logistic_model.joblib"
METRICS_KEY = "models/low_growth_model_metrics.json"
SAGEMAKER_ARTIFACT_KEY = "sagemaker/model-artifacts/low_growth_model.tar.gz"

# Notebooks batch que forman parte del procesamiento histórico.
NOTEBOOKS = [
    "notebook/pipeline_batch_salmonicultura01.ipynb",
    "notebook/pipeline_batch_salmonicultura02.ipynb",
    "notebook/pipeline_batch_salmonicultura03.ipynb",
]