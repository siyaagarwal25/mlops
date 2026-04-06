# Diabetes Prediction - DevOps for AI Capstone (Unit V)

This repository is suitable for your Unit V mini project: DevOps for AI using open-source tools.

Open-source stack used:
- Scikit-learn (model training)
- FastAPI (model serving)
- Docker (containerization)
- Kubernetes + Kind (orchestration)
- GitHub Actions (CI/CD)
- Prometheus client (metrics)
- Pytest (test automation)

## Suitability Analysis

Verdict: Suitable and recommended for Capstone Project 5.

Why this matches Unit V requirements:
- AI model lifecycle is present: training + inference endpoint.
- DevOps practices are present: containerization, deployment manifests, automation.
- Open-source framework requirement is satisfied by the full toolchain.

Initial gap analysis:
- Missing/weak previously: health probes, CI/CD workflow, monitoring endpoint, test coverage, deployment hardening.
- These have been started in this implementation.

## What Has Been Implemented So Far

- Improved API in main.py:
  - Added /health and /ready endpoints for K8s probes.
  - Added /metrics endpoint for Prometheus scraping.
  - Added HTTP request count and latency metrics.
  - Added API error counter metrics.
  - Added model loaded status gauge metric.
  - Added basic logging and configurable model path via environment variable.

- Added test suite in test_main.py:
  - Health, prediction, validation, docs, and metrics tests.
  - Auto-trains model in test setup if missing.

- Enhanced container setup in Dockerfile:
  - Multi-stage build with Python 3.12 slim images.
  - Non-root runtime user.
  - Built-in model generation at image build time.
  - Proper PID1/signal handling via tini.
  - Healthcheck configured.

- Improved Kubernetes manifest in k8s-deploy.yml:
  - Liveness/readiness probes.
  - Startup probe for safer cold start.
  - Resource requests/limits.
  - Security context hardening.
  - Rolling update strategy.
  - Horizontal Pod Autoscaler.
  - PodDisruptionBudget for availability.

- Added CI/CD workflow:
  - .github/workflows/ci-cd.yml for lint, tests, build, and scan stages.

- Added Docker optimization:
  - .dockerignore

## Quick Start (Windows PowerShell)

Recommended Python version: 3.10 to 3.12 for CI parity (3.14 also works with current requirements).

1. Create virtual environment

```powershell
python -m venv .mlops
.\.mlops\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Train model

```powershell
python train.py
```

4. Run API

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. Verify endpoints

- Swagger: http://localhost:8000/docs
- Liveness: http://localhost:8000/health
- Readiness: http://localhost:8000/ready
- Metrics: http://localhost:8000/metrics

Main Prometheus metrics now available:
- `http_requests_total`
- `http_request_duration_seconds`
- `predictions_total`
- `prediction_latency_seconds`
- `api_errors_total`
- `model_loaded`

## Run Tests

```powershell
pytest -v
```

## Docker Run

```powershell
docker build -t diabetes-prediction-model:latest .
docker run -p 8000:8000 diabetes-prediction-model:latest
```

Quick verification:
- http://localhost:8000/health
- http://localhost:8000/docs

## Kubernetes Run (Kind)

1. Create cluster

```powershell
kind create cluster --name demo-mlops
```

2. Update image name in k8s-deploy.yml to your Docker Hub repo.

3. Apply deployment

```powershell
kubectl apply -f k8s-deploy.yml
kubectl get pods -w
kubectl get svc
kubectl get hpa
kubectl get pdb
```

4. Port forward

```powershell
kubectl port-forward svc/diabetes-api-service 1111:80 --address=0.0.0.0
```

Open: http://localhost:1111/docs

Or use the automated Windows deployment script:

```powershell
.\deploy.ps1
```

Note: service type is ClusterIP (recommended for Kind + port-forward workflow).

## CI/CD Setup (GitHub Actions)

Add these repository secrets in GitHub:
- DOCKER_USERNAME
- DOCKER_PASSWORD

On push to main, the pipeline runs lint, test, build, and security checks.

Pipeline file:
- .github/workflows/ci-cd.yml

Current CI stages:
- Lint and formatting checks
- Unit tests
- Docker image build on PR/develop (no push)
- Docker image build and push on main (with secrets)
- Security scan (Bandit) on production Python files

## Suggested Capstone Report Sections

- Problem statement and dataset
- Architecture diagram (train -> API -> Docker -> K8s -> monitoring)
- DevOps workflow and CI/CD stages
- Test strategy and results
- Deployment screenshots (pods, svc, docs)
- Lessons learned and future improvements

## Notes

- Keep using this repository as your base project.
- The implementation has already started and aligns with Unit V outcomes.
- Final verification and submission checklist: see PHASE8_EVIDENCE.md
