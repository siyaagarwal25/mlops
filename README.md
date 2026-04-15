🩺 Diabetes Prediction Model – MLOps Project

FastAPI + Docker + Kubernetes (Kind)

This beginner-friendly MLOps project demonstrates how to build, containerize, and deploy a Machine Learning model for diabetes prediction.

📌 Overview

This project walks you through the complete ML lifecycle:

✅ Train a Machine Learning model (Random Forest)
✅ Serve predictions using FastAPI
✅ Containerize using Docker
✅ Deploy on Kubernetes (Kind cluster)
✅ Understand CI/CD & monitoring (future scope)
📊 Problem Statement

Predict whether a person is diabetic based on the following features:

Pregnancies
Glucose
Blood Pressure
BMI
Age

Model Used: Random Forest Classifier
Dataset: Pima Indians Diabetes Dataset

🚀 Quick Start
1. Clone the Repository
git clone https://github.com/iam-veeramalla/first-mlops-project.git
cd first-mlops-project
💻 Setup & Model Training
2. Create a Virtual Environment
🔹 Windows (CMD)
python -m venv .mlops
.mlops\Scripts\activate
🔹 Windows (PowerShell)
python -m venv .mlops
.\.mlops\Scripts\Activate.ps1
🔹 macOS/Linux
python3 -m venv .mlops
source .mlops/bin/activate
🔹 Windows (Git Bash)
python -m venv .mlops
source .mlops/Scripts/activate
3. Install Dependencies
pip install -r requirements.txt
4. Train the Model
python train.py

➡️ This generates a model.pkl file used for predictions.

🌐 Run FastAPI Locally
5. Start the Server
uvicorn main:app --reload

Open in browser:
👉 http://localhost:8000/docs

6. Sample Input for /predict
{
  "Pregnancies": 2,
  "Glucose": 130,
  "BloodPressure": 70,
  "BMI": 28.5,
  "Age": 45
}
🐳 Docker Setup
7. Build Docker Image
docker build -t diabetes-prediction-model .
8. Run Docker Container
docker run -p 8000:8000 diabetes-prediction-model
9. Tag Docker Image
docker tag <image-id> iamvikramkumar/diabetes-prediction-model:v1

➡️ Find <image-id> using:

docker images
10. Push to Docker Hub
docker login
docker push iamvikramkumar/diabetes-prediction-model:v1
☸️ Kubernetes Deployment (Kind)

⚠️ Ensure Docker Desktop, kubectl, and Kind are installed.

11. Create Cluster
kind create cluster --name demo-mlops
12. Verify Cluster
kubectl config current-context
kubectl get nodes
13. Deploy Application
kubectl apply -f deploy.yaml
14. Monitor Resources
kubectl get pods -w
kubectl get svc
15. Access API
kubectl port-forward svc/diabetes-api-service 1111:80 --address=0.0.0.0

Open in browser:
👉 http://localhost:1111/docs

🔄 Future Scope
🧪 CI/CD (Not Implemented Yet)
Automate testing and validation
Build Docker images automatically
Push images to Docker Hub
Deploy to Kubernetes

Tools to use:

GitHub Actions
Jenkins (optional)
📈 Monitoring (Not Implemented Yet)
Track API performance and latency
Monitor model accuracy and drift

Tools to use:

Prometheus + Grafana
Evidently AI / WhyLogs
