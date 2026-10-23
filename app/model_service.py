
from pathlib import Path

import joblib
import pandas as pd
import numpy as np


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "fraud_model.joblib"

_model_artifact = None


def load_model():
    """Load and cache the trained fraud detection model."""
    global _model_artifact

    if _model_artifact is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model file not found: {MODEL_PATH}. "
                "Run train.py first to train the model."
            )

        _model_artifact = joblib.load(MODEL_PATH)

    return _model_artifact


def predict_transaction(features: dict):
    """Predict whether a transaction may be fraudulent."""
    artifact = load_model()

    # Support the artifact format saved by train.py.
    if isinstance(artifact, dict):
        model = artifact.get("model") or artifact.get("pipeline")
        threshold = float(artifact.get("threshold", 0.5))
        feature_names = artifact.get("feature_names")
        model_name = artifact.get("model_name", type(model).__name__)
    else:
        model = artifact
        threshold = 0.5
        feature_names = getattr(model, "feature_names_in_", None)
        model_name = type(model).__name__

    if model is None:
        raise ValueError(
            "The saved model artifact does not contain a model or pipeline."
        )

    if feature_names is None:
        raise ValueError(
            "Model feature names are missing from the saved artifact."
        )

    expected_features = list(feature_names)
    supplied_features = set(features.keys())
    expected_set = set(expected_features)

    missing = sorted(expected_set - supplied_features)
    unexpected = sorted(supplied_features - expected_set)

    if missing or unexpected:
        details = []
        if missing:
            details.append(f"Missing features: {missing}")
        if unexpected:
            details.append(f"Unexpected features: {unexpected}")
        raise ValueError("; ".join(details))

    row = pd.DataFrame(
        [[float(features[name]) for name in expected_features]],
        columns=expected_features,
    )

    if not np.isfinite(row.to_numpy(dtype=float)).all():
        raise ValueError("All feature values must be finite numbers.")

    if not hasattr(model, "predict_proba"):
        raise ValueError(
            "The saved model does not support probability predictions."
        )

    probabilities = model.predict_proba(row)[0]
    classes = list(getattr(model, "classes_", [0, 1]))

    if 1 not in classes:
        raise ValueError("The model does not have a fraud class (1).")

    fraud_probability = float(probabilities[classes.index(1)])
    is_fraud = fraud_probability >= threshold

    return {
        "is_fraud": bool(is_fraud),
        "fraud_probability": fraud_probability,
        "threshold": threshold,
        "model_name": model_name,
        "prediction": int(is_fraud),
    }
