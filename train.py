# train.py
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import joblib


# -----------------------------
# 1) Load dataset
# -----------------------------
url = "https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv"
df = pd.read_csv(url)
print("Columns:", df.columns.tolist())


# -----------------------------
# 2) Select features and target
# -----------------------------
X = df[["Pregnancies", "Glucose", "BloodPressure", "BMI", "Age"]]
y = df["Outcome"]


# -----------------------------
# 3) Train-test split
# -----------------------------
# Stratify keeps class balance similar in train and test sets.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)


# -----------------------------
# 5) Build end-to-end pipeline
# -----------------------------
# In this dataset, 0 can be medically invalid for Glucose/BloodPressure/BMI.
# We directly impute 0 as missing for these columns using median values.
preprocessor = ColumnTransformer(
    transformers=[
        (
            "impute_zero_medical_fields",
            SimpleImputer(missing_values=0, strategy="median"),
            ["Glucose", "BloodPressure", "BMI"],
        ),
        (
            "impute_other_fields",
            SimpleImputer(strategy="median"),
            ["Pregnancies", "Age"],
        ),
    ],
    remainder="drop",
)

model_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestClassifier(
                random_state=42,
                n_estimators=300,
                class_weight="balanced",
            ),
        ),
    ]
)


# -----------------------------
# 6) Train model
# -----------------------------
model_pipeline.fit(X_train, y_train)


# -----------------------------
# 7) Evaluate model performance
# -----------------------------
y_pred = model_pipeline.predict(X_test)
y_proba = model_pipeline.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)
roc_auc = roc_auc_score(y_test, y_proba)

print("\n=== Model Evaluation Metrics ===")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))


# -----------------------------
# 8) Save trained pipeline
# -----------------------------
# We save the full pipeline (preprocessing + model),
# so inference uses the same preprocessing automatically.
joblib.dump(model_pipeline, "diabetes_model.pkl")
print("Model saved as diabetes_model.pkl")
