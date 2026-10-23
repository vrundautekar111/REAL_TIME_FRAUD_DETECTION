
from pathlib import Path
import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "creditcard.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "fraud_model.joblib"
METRICS_PATH = MODEL_DIR / "evaluation_metrics.json"

RANDOM_STATE = 42


def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}. "
            "Download creditcard.csv into the data folder."
        )

    df = pd.read_csv(DATA_PATH)

    if "Class" not in df.columns:
        raise ValueError("Expected target column: Class")

    if df.empty or df["Class"].isna().any():
        raise ValueError("Dataset is empty or has missing labels.")

    if not set(df["Class"].unique()).issubset({0, 1}):
        raise ValueError("Class must contain only 0 and 1.")

    if set(df["Class"].unique()) != {0, 1}:
        raise ValueError("Both fraud and legitimate examples are required.")

    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names detected.")

    if df.drop(columns="Class").select_dtypes(
        exclude=np.number
    ).shape[1]:
        raise ValueError("All model features must be numeric.")

    if not np.isfinite(
        df.select_dtypes(include=np.number).to_numpy()
    ).all():
        raise ValueError("Missing or infinite numeric values detected.")

    duplicates = int(df.duplicated().sum())
    if duplicates:
        print(f"Removing {duplicates} exact duplicate rows.")
        df = df.drop_duplicates().reset_index(drop=True)

    return df


def build_pipeline(model_name):
    # Scale Time and Amount; preserve PCA features V1-V28.
    preprocessor = ColumnTransformer(
        transformers=[
            ("scale", StandardScaler(), ["Time", "Amount"]),
        ],
        remainder="passthrough",
        verbose_feature_names_out=False,
    )

    if model_name == "logistic_regression":
        classifier = LogisticRegression(
            class_weight="balanced",
            max_iter=2000,
            random_state=RANDOM_STATE,
        )
    elif model_name == "random_forest":
        classifier = RandomForestClassifier(
            n_estimators=120,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")

    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", classifier),
    ])


def choose_threshold(y_true, probabilities):
    precision, recall, thresholds = precision_recall_curve(
        y_true, probabilities
    )

    precision = precision[:-1]
    recall = recall[:-1]

    if len(thresholds) == 0:
        raise ValueError("No threshold candidates available.")

    f1 = (
        2 * precision * recall
        / np.maximum(precision + recall, 1e-12)
    )

    index = int(np.argmax(f1))

    return {
        "threshold": float(thresholds[index]),
        "precision": float(precision[index]),
        "recall": float(recall[index]),
        "f1": float(f1[index]),
    }


def evaluate_model(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true, predictions, labels=[0, 1]
    ).ravel()

    return {
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "precision": float(
            precision_score(y_true, predictions, zero_division=0)
        ),
        "recall": float(
            recall_score(y_true, predictions, zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_true, predictions, zero_division=0)
        ),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "classification_report": classification_report(
            y_true,
            predictions,
            labels=[0, 1],
            target_names=["legitimate", "fraud"],
            output_dict=True,
            zero_division=0,
        ),
    }


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    X = df.drop(columns="Class")
    y = df["Class"].astype(int)

    print(f"Transactions: {len(df):,}")
    print(f"Fraud transactions: {int(y.sum()):,}")
    print(f"Fraud percentage: {y.mean() * 100:.4f}%")

    # Stratified split: 70% train, 15% validation, 15% test.
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=0.30,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=RANDOM_STATE,
    )

    scores = {}
    models = {}

    for name in ["logistic_regression", "random_forest"]:
        print(f"\nTraining {name}...")
        model = build_pipeline(name)
        model.fit(X_train, y_train)

        probabilities = model.predict_proba(X_val)[:, 1]
        scores[name] = float(
            average_precision_score(y_val, probabilities)
        )
        models[name] = model
        print(f"Validation PR-AUC: {scores[name]:.6f}")

    # Select by validation PR-AUC, not test performance.
    best_name = max(scores, key=scores.get)
    best_model = models[best_name]

    val_probabilities = best_model.predict_proba(X_val)[:, 1]
    threshold_results = choose_threshold(y_val, val_probabilities)
    threshold = threshold_results["threshold"]

    test_probabilities = best_model.predict_proba(X_test)[:, 1]
    metrics = evaluate_model(y_test, test_probabilities, threshold)

    print(f"\nSelected model: {best_name}")
    print(f"Decision threshold: {threshold:.6f}")
    print(json.dumps(metrics, indent=2))

    # Reference statistics are used later for basic drift monitoring.
    reference_stats = {}
    for column in X.columns:
        values = X_train[column].astype(float)
        reference_stats[column] = {
            "mean": float(values.mean()),
            "std": float(values.std()),
            "q01": float(values.quantile(0.01)),
            "q25": float(values.quantile(0.25)),
            "q50": float(values.quantile(0.50)),
            "q75": float(values.quantile(0.75)),
            "q99": float(values.quantile(0.99)),
        }

    artifact = {
        "model": best_model,
        "threshold": threshold,
        "feature_names": list(X.columns),
        "selected_model": best_name,
        "validation_pr_auc_by_model": scores,
        "threshold_selection": threshold_results,
        "test_metrics": metrics,
        "reference_stats": reference_stats,
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    joblib.dump(artifact, MODEL_PATH)

    report = {
        "dataset_rows": int(len(df)),
        "fraud_rate": float(y.mean()),
        "selected_model": best_name,
        "validation_pr_auc_by_model": scores,
        "threshold": threshold,
        "threshold_selection": threshold_results,
        "test_metrics": metrics,
        "trained_at_utc": artifact["trained_at_utc"],
    }

    METRICS_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(f"\nModel saved: {MODEL_PATH}")
    print(f"Metrics saved: {METRICS_PATH}")


if __name__ == "__main__":
    main()
