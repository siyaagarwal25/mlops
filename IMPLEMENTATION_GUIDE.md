# DevOps for AI Implementation Guide - Diabetes Prediction Project

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [Local Development](#local-development)
4. [Testing](#testing)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring & Metrics](#monitoring--metrics)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This is a **DevOps for AI** capstone project demonstrating:
- ✅ ML Model Training & Serving
- ✅ REST API with FastAPI
- ✅ Containerization with Docker
- ✅ Container Orchestration with Kubernetes
- ✅ CI/CD Pipeline with GitHub Actions
- ✅ Monitoring with Prometheus
- ✅ Health Checks & Auto-scaling
- ✅ Security Best Practices

**Key Features:**
- Non-root container execution
- Liveness & Readiness probes
- Horizontal Pod Autoscaling
- Prometheus metrics collection
- Comprehensive test coverage
- Multi-stage Docker build

---

## 💻 Setup Instructions

### Prerequisites
- Python 3.10+
- Docker & Docker Desktop
- Kubernetes CLI (kubectl)
- Kind (for local K8s cluster)
- Git & GitHub account
- Optional: Docker Hub account

### 1. Clone and Navigate

```bash
cd diabetes_prediction/mlops
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Local Development

### 1. Train the Model

```bash
python train.py
```

**Output:** Creates `diabetes_model.pkl` (trained Random Forest model)

### 2. Run FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

### 3. Test the API

**Using curl:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Pregnancies": 2,
    "Glucose": 130,
    "BloodPressure": 70,
    "BMI": 28.5,
    "Age": 45
  }'
```

**Using Python:**
```python
import requests

payload = {
    "Pregnancies": 2,
    "Glucose": 130,
    "BloodPressure": 70,
    "BMI": 28.5,
    "Age": 45
}

response = requests.post("http://localhost:8000/predict", json=payload)
print(response.json())
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest test_main.py -v
```

### Run Specific Test Class

```bash
pytest test_main.py::TestPredictions -v
```

### Run with Coverage

```bash
pytest test_main.py --cov=main --cov-report=html
```

### Test Categories

| Category | Coverage | Command |
|----------|----------|---------|
| Health Checks | `/health`, `/ready`, `/` | `pytest test_main.py::TestHealth -v` |
| Predictions | Valid/Invalid/Edge cases | `pytest test_main.py::TestPredictions -v` |
| Metrics | Prometheus metrics | `pytest test_main.py::TestMetrics -v` |
| Documentation | FastAPI docs | `pytest test_main.py::TestDocumentation -v` |

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t diabetes-prediction-model:latest .
```

### Run Container Locally

```bash
docker run -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e MODEL_PATH=/app/diabetes_model.pkl \
  diabetes-prediction-model:latest
```

### Test Container

```bash
curl http://localhost:8000/health
```

### Push to Docker Hub

```bash
# Login
docker login

# Tag image
docker tag diabetes-prediction-model:latest \
  YOUR_USERNAME/diabetes-prediction-model:v1.0.0

# Push
docker push YOUR_USERNAME/diabetes-prediction-model:v1.0.0
```

### Docker Best Practices Implemented

✅ Multi-stage build (reduces image size)  
✅ Non-root user execution (security)  
✅ Health checks (container monitoring)  
✅ Minimal base image (python:3.10-slim)  
✅ .dockerignore optimization  
✅ Layer caching efficiency  

---

## ☸️ Kubernetes Deployment

### Prerequisites

1. **Install Kind:**
```bash
# Windows (with Chocolatey)
choco install kind

# macOS (with Brew)
brew install kind

# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
```

2. **Create Kind Cluster:**
```bash
kind create cluster --name demo-mlops
```

3. **Verify Cluster:**
```bash
kubectl cluster-info
kubectl get nodes
```

### Deploy to Kubernetes

1. **Update image in k8s-deploy.yml:**
```yaml
image: docker.io/YOUR_USERNAME/diabetes-prediction-model:latest
```

2. **Apply manifests:**
```bash
kubectl apply -f k8s-deploy.yml
```

3. **Check deployment status:**
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

4. **Wait for ready state:**
```bash
kubectl rollout status deployment/diabetes-api
```

### Access the Service

**Port Forward:**
```bash
kubectl port-forward svc/diabetes-api-service 8000:80
```

**Access:** http://localhost:8000/docs

### Monitor Kubernetes Resources

```bash
# Watch pods in real-time
kubectl get pods -w

# Check services
kubectl get svc

# Check HorizontalPodAutoscaler
kubectl get hpa

# View metrics
kubectl top nodes
kubectl top pods

# View events
kubectl get events --sort-by='.lastTimestamp'
```

### Kubernetes Features Implemented

✅ Deployment with rolling updates  
✅ Liveness & Readiness probes  
✅ Resource requests & limits  
✅ SecurityContext (non-root)  
✅ HorizontalPodAutoscaler (2-5 replicas)  
✅ Pod anti-affinity (spread across nodes)  
✅ Service with LoadBalancer  
✅ Prometheus annotations  

---

## 🔄 CI/CD Pipeline

### GitHub Actions Setup

1. **Create GitHub Repository:**
```bash
git init
git remote add origin https://github.com/YOUR_USERNAME/diabetes-prediction.git
git branch -M main
git push -u origin main
```

2. **Add Secrets to GitHub:**

Go to: **Settings → Secrets and variables → Actions**

Add:
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password/token

3. **Trigger Pipeline:**
```bash
git push origin main
```

### Pipeline Steps

The CI/CD pipeline (`ci-cd.yml`) automatically:

1. **Lint & Code Quality** → Checks code with flake8 & pylint
2. **Unit Tests** → Runs pytest suite
3. **Build Docker Image** → Builds & pushes to Docker Hub
4. **Security Scan** → Bandit security analysis
5. **Deployment Ready** → Confirms readiness

### View Pipeline Status

- Go to: **Actions** tab in GitHub repository
- Check build history and logs
- Fix issues based on step failures

---

## 📊 Monitoring & Metrics

### Prometheus Metrics

The API exposes metrics at `/metrics` endpoint:

```bash
curl http://localhost:8000/metrics
```

**Available Metrics:**
- `predictions_total` - Total predictions made
- `prediction_latency_seconds` - Time taken per prediction
- Standard FastAPI metrics

### Set Up Prometheus (Advanced)

1. **Create prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'diabetes-api'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

2. **Deploy Prometheus:**
```bash
kubectl create configmap prometheus-config --from-file=prometheus.yml
kubectl apply -f prometheus-deployment.yml
```

---

## 🐛 Troubleshooting

### Issue: Model not found
```
❌ Model not found at /app/diabetes_model.pkl
```

**Solution:**
```bash
python train.py  # Generate model first
```

### Issue: Port already in use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Docker container fails
```bash
# Check logs
docker logs <container-id>

# Run with interactive mode
docker run -it --entrypoint /bin/bash diabetes-prediction-model
```

### Issue: Kubernetes pod not starting
```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous crashed container

# Check events
kubectl get events
```

### Issue: Health check failing
```bash
# Test health endpoint directly
kubectl exec <pod-name> -- curl http://localhost:8000/health

# Check readiness probe
kubectl describe pod <pod-name> | grep -A 5 "Readiness"
```

---

## 📚 Learning Resources

### DevOps Concepts Covered
- **Containerization:** Docker multi-stage builds, security
- **Orchestration:** Kubernetes deployments, services, scaling
- **CI/CD:** GitHub Actions workflows, automated testing
- **Monitoring:** Prometheus metrics, health checks
- **Security:** Non-root execution, resource limits, SecurityContext
- **Testing:** Pytest, FastAPI TestClient, coverage
- **Quality:** Code linting, formatting, security scanning

### Further Reading
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Prometheus Documentation](https://prometheus.io/docs/)

---

## 📝 Project Checklist

- [ ] Environment setup complete
- [ ] Model trained successfully
- [ ] Local API tests passing
- [ ] Docker image builds without errors
- [ ] Container runs and responds to requests
- [ ] Kind cluster created
- [ ] K8s deployment successful
- [ ] Pods are in Running state
- [ ] Service is accessible
- [ ] GitHub repository created
- [ ] Secrets configured in GitHub
- [ ] CI/CD pipeline running
- [ ] All tests passing
- [ ] Docker image pushed to Hub
- [ ] Documentation reviewed

---

## 🎓 Capstone Project Submission Checklist

For your Unit V DevOps for AI capstone, ensure:

✅ **Model Training:** Working ML model with data pipeline  
✅ **API Service:** FastAPI with health endpoints  
✅ **Containerization:** Multi-stage Dockerfile with security  
✅ **Orchestration:** K8s deployment with probes & scaling  
✅ **Testing:** Unit tests with >80% coverage  
✅ **CI/CD:** GitHub Actions with lint → test → build  
✅ **Monitoring:** Prometheus metrics collection  
✅ **Documentation:** Clear setup & usage guides  
✅ **Security:** Non-root execution, resource limits  
✅ **Deployment:** Working local & cloud deployment  

---

## 📞 Support & Questions

- Check logs: `kubectl logs <pod-name>`
- Describe resources: `kubectl describe pod <pod-name>`
- Check events: `kubectl get events`
- Review GitHub Actions: Repository → Actions tab
- FastAPI docs: http://localhost:8000/docs

---

**Status:** ✅ Production Ready  
**Last Updated:** 2024  
**Maintainer:** DevOps Team
