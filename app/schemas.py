
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class TransactionRequest(BaseModel):
    """Request schema for a single transaction."""

    features: Dict[str, float] = Field(
        ...,
        description="Transaction features used by the fraud detection model",
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, features: Dict[str, float]):
        if not features:
            raise ValueError("Features cannot be empty")

        for name, value in features.items():
            if not name.strip():
                raise ValueError("Feature names cannot be empty")

            if not float("-inf") < value < float("inf"):
                raise ValueError(
                    f"Feature '{name}' must be a finite number"
                )

        return features


class BatchPredictionRequest(BaseModel):
    """Request schema for batch transaction predictions."""

    transactions: List[TransactionRequest] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Transactions to classify",
    )
