
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.model_service import load_artifact

client = TestClient(app)


@pytest.fixture
def valid_features():
    artifact = load_artifact()
    return {name: 0.0 for name in artifact["feature_names"]}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Fraud Detection API" in response.json()["message"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_predict_returns_valid_response(valid_features):
    response = client.post(
        "/predict",
        json={"features": valid_features},
    )

    assert response.status_code == 200
    body = response.json()

    assert 0.0 <= body["fraud_probability"] <= 1.0
    assert body["prediction"] in {"fraud", "legitimate"}
    assert 0.0 <= body["threshold"] <= 1.0
    assert body["model_name"] in {
        "logistic_regression", "random_forest"
    }


def test_missing_feature_is_rejected(valid_features):
    artifact = load_artifact()
    missing_name = artifact["feature_names"][0]
    invalid = dict(valid_features)
    invalid.pop(missing_name)

    response = client.post(
        "/predict",
        json={"features": invalid},
    )

    assert response.status_code == 422


def test_unexpected_feature_is_rejected(valid_features):
    invalid = dict(valid_features)
    invalid["unexpected_feature"] = 123.0

    response = client.post(
        "/predict",
        json={"features": invalid},
    )

    assert response.status_code == 422


def test_batch_prediction(valid_features):
    response = client.post(
        "/predict/batch",
        json={
            "transactions": [
                {"features": valid_features},
                {"features": valid_features},
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert len(body["predictions"]) == 2


def test_empty_batch_is_rejected():
    response = client.post(
        "/predict/batch",
        json={"transactions": []},
    )

    assert response.status_code == 422
