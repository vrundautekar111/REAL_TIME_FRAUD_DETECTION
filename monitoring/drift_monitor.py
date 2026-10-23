
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "fraud_model.joblib"


def detect_drift(
    batch: pd.DataFrame,
    z_threshold: float = 3.0,
) -> dict:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Train the model first using python train.py."
        )

    artifact = joblib.load(MODEL_PATH)
    reference = artifact["reference_stats"]
    features = artifact["feature_names"]

    missing = set(features) - set(batch.columns)
    unexpected = set(batch.columns) - set(features)

    if missing or unexpected:
        raise ValueError(
            f"Feature mismatch. Missing: {sorted(missing)}; "
            f"unexpected: {sorted(unexpected)}"
        )

    if batch.empty:
        raise ValueError("Cannot monitor an empty batch.")

    X = batch[features].apply(pd.to_numeric, errors="raise")

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError("Batch contains missing or infinite values.")

    results = []

    for feature in features:
        ref = reference[feature]
        current_mean = float(X[feature].mean())
        ref_std = float(ref["std"])

        if ref_std > 1e-12:
            z_score = (current_mean - ref["mean"]) / ref_std
        else:
            z_score = 0.0 if abs(
                current_mean - ref["mean"]
            ) < 1e-12 else float("inf")

        results.append({
            "feature": feature,
            "reference_mean": ref["mean"],
            "current_mean": current_mean,
            "mean_shift_z": float(z_score),
            "drift_flag": abs(z_score) > z_threshold,
        })

    flagged = [r for r in results if r["drift_flag"]]

    return {
        "batch_rows": int(len(X)),
        "threshold": z_threshold,
        "features_checked": len(results),
        "drifted_features": len(flagged),
        "drift_detected": bool(flagged),
        "details": results,
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Check transaction feature drift."
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to a CSV containing model input features.",
    )
    args = parser.parse_args()

    batch = pd.read_csv(args.csv)
    report = detect_drift(batch)
    print(json.dumps(report, indent=2))
