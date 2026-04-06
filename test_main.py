"""
Test suite for Diabetes Prediction API
Uses pytest and FastAPI's TestClient
"""

import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

if not os.path.exists("diabetes_model.pkl"):
    subprocess.run([sys.executable, "train.py"], check=True)

from main import app

client = TestClient(app)


class TestHealth:
    """Test health check endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns 200"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "healthy"

    def test_health_check(self):
        """Test /health endpoint (liveness probe)"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_readiness_check(self):
        """Test /ready endpoint (readiness probe)"""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["model_loaded"] is True


class TestPredictions:
    """Test prediction endpoint"""

    def test_predict_positive_case(self):
        """Test prediction with diabetic person"""
        payload = {
            "Pregnancies": 6,
            "Glucose": 148,
            "BloodPressure": 72,
            "BMI": 35.0,
            "Age": 52,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "diabetic" in data
        assert "prediction_value" in data
        assert "timestamp" in data
        assert isinstance(data["diabetic"], bool)

    def test_predict_negative_case(self):
        """Test prediction with non-diabetic person"""
        payload = {
            "Pregnancies": 1,
            "Glucose": 85,
            "BloodPressure": 66,
            "BMI": 26.6,
            "Age": 31,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "diabetic" in data
        assert isinstance(data["diabetic"], bool)

    def test_predict_edge_case_min_values(self):
        """Test prediction with minimum valid values"""
        payload = {
            "Pregnancies": 0,
            "Glucose": 0,
            "BloodPressure": 0,
            "BMI": 0.0,
            "Age": 0,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200

    def test_predict_edge_case_high_values(self):
        """Test prediction with high values"""
        payload = {
            "Pregnancies": 15,
            "Glucose": 200,
            "BloodPressure": 122,
            "BMI": 60.0,
            "Age": 120,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200

    def test_predict_missing_field(self):
        """Test prediction with missing required field"""
        payload = {
            "Pregnancies": 2,
            "Glucose": 100,
            "BMI": 28.0,
            "Age": 45,
            # Missing BloodPressure
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error

    def test_predict_invalid_type(self):
        """Test prediction with invalid data type"""
        payload = {
            "Pregnancies": "invalid",  # Should be int
            "Glucose": 100,
            "BloodPressure": 70,
            "BMI": 28.0,
            "Age": 45,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error

    def test_predict_negative_value_validation(self):
        """Test prediction rejects invalid negative values"""
        payload = {
            "Pregnancies": -1,
            "Glucose": 100,
            "BloodPressure": 70,
            "BMI": 28.0,
            "Age": 45,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422

    def test_predict_age_upper_bound_validation(self):
        """Test prediction rejects out-of-range age"""
        payload = {
            "Pregnancies": 2,
            "Glucose": 120,
            "BloodPressure": 70,
            "BMI": 28.0,
            "Age": 131,
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422


class TestMetrics:
    """Test metrics endpoint"""

    def test_metrics_endpoint(self):
        """Test /metrics endpoint returns prometheus metrics"""
        # Trigger endpoints so metrics counters/histograms are populated.
        client.get("/")
        client.get("/health")

        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        # Should contain prometheus metrics format
        content = response.text
        assert "HELP" in content or "TYPE" in content or "#" in content
        assert "http_requests_total" in content
        assert "http_request_duration_seconds" in content
        assert "model_loaded" in content


class TestDocumentation:
    """Test API documentation"""

    def test_docs_available(self):
        """Test that FastAPI documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
