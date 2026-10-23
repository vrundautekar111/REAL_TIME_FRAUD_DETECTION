from contextlib import asynccontextmanager
from threading import Lock
from time import monotonic

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas import TransactionRequest, BatchPredictionRequest
from app.model_service import predict_transaction, load_model


# -------------------- API METRICS --------------------

START_TIME = monotonic()
METRICS_LOCK = Lock()

METRICS = {
    "requests_total": 0,
    "predictions_total": 0,
    "fraud_predictions": 0,
    "errors_total": 0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the saved model when the API starts.
    # Training is not performed automatically here.
    try:
        load_model()
        print("Fraud detection model loaded successfully.")
    except FileNotFoundError as exc:
        print(f"Model not loaded: {exc}")
    yield


app = FastAPI(
    title="Real-Time Fraud Detection API",
    description="API for predicting fraudulent financial transactions.",
    version="1.0.0",
    lifespan=lifespan,
)


# -------------------- REQUEST MONITORING --------------------

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    with METRICS_LOCK:
        METRICS["requests_total"] += 1

    try:
        response = await call_next(request)

        if response.status_code >= 400:
            with METRICS_LOCK:
                METRICS["errors_total"] += 1

        return response

    except Exception:
        with METRICS_LOCK:
            METRICS["errors_total"] += 1
        raise


# -------------------- HELPER --------------------

def run_prediction(features: dict):
    try:
        result = predict_transaction(features)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="Model file is missing. Run train.py first.",
        ) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        ) from exc

    with METRICS_LOCK:
        METRICS["predictions_total"] += 1
        if result.get("is_fraud", False):
            METRICS["fraud_predictions"] += 1

    return result


# -------------------- ROUTES --------------------

@app.get("/")
def home():
    return {
        "message": "Real-Time Fraud Detection API is running",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.get("/health")
def health():
    try:
        load_model()
        return {"status": "healthy", "model_loaded": True}
    except FileNotFoundError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "model_loaded": False,
                "message": "Run train.py to create the model file.",
            },
        )


@app.get("/metrics")
def get_metrics():
    # Always return the keys expected by the Streamlit dashboard.
    with METRICS_LOCK:
        result = dict(METRICS)

    result["uptime_seconds"] = round(monotonic() - START_TIME, 2)
    return result


@app.post("/predict")
def predict(request: TransactionRequest):
    result = run_prediction(request.features)
    return {
        "success": True,
        "result": result,
    }


@app.post("/predict/batch")
def predict_batch(request: BatchPredictionRequest):
    results = [
        run_prediction(transaction.features)
        for transaction in request.transactions
    ]

    return {
        "success": True,
        "total_transactions": len(results),
        "fraud_count": sum(
            1 for result in results if result.get("is_fraud", False)
        ),
        "results": results,
    }