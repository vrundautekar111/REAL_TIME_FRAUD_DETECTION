
# Real-Time Fraud Detection API

An end-to-end machine learning project that detects potentially fraudulent
credit card transactions and serves predictions through a REST API.

## Features

- Imbalanced transaction classification using class weights
- Logistic Regression and Random Forest comparison
- Validation-based decision threshold tuning
- Precision, recall, F1-score, PR-AUC and confusion matrix
- FastAPI prediction and batch prediction endpoints
- Request validation and automated Pytest tests
- Streamlit dashboard for predictions and evaluation metrics
- Basic feature drift detection
- Docker and Docker Compose deployment

## Tech Stack

Python, Pandas, NumPy, Scikit-learn, FastAPI, Streamlit, Plotly,
Joblib, Pytest, Docker.

## Dataset

Credit Card Fraud Detection dataset:
https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

Download creditcard.csv into the data/ directory.

Do not commit the dataset or real financial information to GitHub.

## Setup on Windows

Create a virtual environment:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install -r requirements.txt

Train and evaluate:

    python train.py

## Start the API

    python -m uvicorn app.main:app --reload

Swagger documentation:
http://127.0.0.1:8000/docs

Health:
http://127.0.0.1:8000/health

## Start the Dashboard

Open a second terminal and activate the same virtual environment:

    .\.venv\Scripts\Activate.ps1
    python -m streamlit run streamlit_app.py

Dashboard:
http://localhost:8501

## Run Tests

    python -m pytest -v

Train the model before running prediction tests.

## Run Drift Monitoring

Prepare a CSV containing only model input features, then run:

    python monitoring/drift_monitor.py --csv data/new_transactions.csv

## Docker

Train the model locally first so that models/fraud_model.joblib exists.

    docker compose up --build

API:
http://localhost:8000/docs

Dashboard:
http://localhost:8501

## Important Limitations

This project uses a public historical dataset. It demonstrates a
machine learning workflow and is not a bank-approved fraud prevention
system. Threshold selection, drift alerts and predictions require
business validation before production use.
