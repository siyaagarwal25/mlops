# main.py
from datetime import datetime
from typing import Any
import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import joblib
import pandas as pd
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Prometheus metrics
prediction_counter = Counter("predictions_total", "Total predictions made", ["result"])
prediction_latency = Histogram(
    "prediction_latency_seconds", "Prediction latency in seconds"
)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
api_errors_total = Counter(
    "api_errors_total", "Total API errors", ["endpoint", "error_type"]
)
model_loaded_gauge = Gauge(
    "model_loaded", "Whether the ML model is loaded (1=yes, 0=no)"
)

# Initialize FastAPI app
app = FastAPI(
    title="Diabetes Prediction API",
    description="ML API for predicting diabetes using Random Forest",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.getenv("MODEL_PATH", "diabetes_model.pkl")
FEATURE_COLUMNS = ["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]


def _load_model() -> tuple[Any, bool]:
    """Load the model artifact and return model with readiness state."""
    try:
        loaded_model = joblib.load(MODEL_PATH)
        logger.info("Model loaded from %s", MODEL_PATH)
        return loaded_model, True
    except FileNotFoundError:
        logger.error("Model not found at %s", MODEL_PATH)
    except Exception as exc:
        logger.exception("Unexpected model load error: %s", exc)
    return None, False


model, model_loaded = _load_model()
model_loaded_gauge.set(1 if model_loaded else 0)


class DiabetesInput(BaseModel):
    Pregnancies: int = Field(ge=0, le=30, description="Number of pregnancies")
    Glucose: float = Field(ge=0, le=300, description="Plasma glucose concentration")
    BloodPressure: float = Field(
        ge=0, le=200, description="Diastolic blood pressure (mm Hg)"
    )
    BMI: float = Field(ge=0, le=100, description="Body mass index")
    Age: int = Field(ge=0, le=130, description="Age in years")


class PredictionOutput(BaseModel):
    diabetic: bool
    prediction_value: int
    timestamp: str


@app.middleware("http")
async def prometheus_http_middleware(request: Request, call_next):
    """Capture request count and latency for all endpoints."""
    path = request.url.path
    method = request.method

    with http_request_duration_seconds.labels(method=method, path=path).time():
        response = await call_next(request)

    http_requests_total.labels(
        method=method,
        path=path,
        status_code=str(response.status_code),
    ).inc()
    return response


@app.get("/")
def read_root():
    return {
        "message": "Diabetes Prediction API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe - checks if API is running"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/ready", tags=["Health"])
def readiness_check():
    """Readiness probe - checks if API is ready to handle predictions"""
    if not model_loaded:
        api_errors_total.labels(endpoint="/ready", error_type="model_not_loaded").inc()
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "status": "ready",
        "model_loaded": model_loaded,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/predict", tags=["Predictions"], response_model=PredictionOutput)
def predict(data: DiabetesInput) -> PredictionOutput:
    """Predict diabetes probability from input features"""
    if not model_loaded:
        api_errors_total.labels(
            endpoint="/predict", error_type="model_not_loaded"
        ).inc()
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        with prediction_latency.time():
            input_data = pd.DataFrame(
                [
                    [
                        data.Pregnancies,
                        data.Glucose,
                        data.BloodPressure,
                        data.BMI,
                        data.Age,
                    ]
                ],
                columns=FEATURE_COLUMNS,
            )
            prediction = model.predict(input_data)[0]
            prediction_counter.labels(result=bool(prediction)).inc()

            logger.info(
                "Prediction generated. diabetic=%s age=%s glucose=%s",
                bool(prediction),
                data.Age,
                data.Glucose,
            )

            return PredictionOutput(
                diabetic=bool(prediction),
                prediction_value=int(prediction),
                timestamp=datetime.now().isoformat(),
            )
    except Exception as exc:
        logger.exception("Prediction error: %s", exc)
        api_errors_total.labels(
            endpoint="/predict", error_type="prediction_failure"
        ).inc()
        raise HTTPException(
            status_code=500, detail="Prediction failed due to internal error"
        )


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Return Prometheus metrics"""
    return Response(
        generate_latest(), media_type="text/plain; version=0.0.4; charset=utf-8"
    )
