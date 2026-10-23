# Real-Time Credit Card Fraud Detection API



## Project Overview

The Real-Time Credit Card Fraud Detection API is a machine learning-based application designed to identify potentially fraudulent credit card transactions by analyzing transaction features and predicting whether a transaction is legitimate or suspicious. The project integrates machine learning, backend API development, an interactive dashboard, and basic monitoring to demonstrate an end-to-end machine learning workflow.

The system uses Python and Scikit-learn to train classification models on historical credit card transaction data. The trained model is integrated with a FastAPI backend that receives transaction requests, validates input data, and returns predictions through REST API endpoints. A Streamlit dashboard provides an interactive interface for submitting transaction features, viewing prediction results, and monitoring available system metrics.



## Technologies Used

- **Python:** Core programming language for data processing and model development.
- **Pandas and NumPy:** Data manipulation and numerical computation.
- **Scikit-learn:** Machine learning model training and evaluation.
- **FastAPI:** Backend REST API for transaction predictions.
- **Pydantic:** Request data validation.
- **Streamlit:** Interactive web dashboard.
- **Plotly:** Interactive charts and data visualization.
- **Joblib:** Saving and loading trained model artifacts.
- **HTTPX:** Communication between the dashboard and backend API.
- **Pytest:** Automated API testing.
- **Docker:** Containerization and deployment support.
- **Git and GitHub:** Version control and source code management.



## Dataset and Preprocessing

The project uses a credit card transaction dataset stored in `data/creditcard.csv`. The dataset contains historical transaction records with numerical features and a target label identifying fraudulent and legitimate transactions.

Data preprocessing includes inspecting missing values, handling duplicate records where appropriate, separating input features from the target variable, and preparing data for model training. Since fraudulent transactions are relatively rare, the project accounts for class imbalance and uses suitable evaluation metrics rather than relying only on accuracy.




## Machine Learning Model Development

The `train.py` script manages the training workflow, including loading data, preparing features, splitting the dataset, training classification models, and evaluating their performance.

Models such as Logistic Regression and Random Forest can be compared using precision, recall, F1-score, confusion matrix, and Precision-Recall AUC. The classification threshold can be tuned to balance fraud detection and false-positive rates.

The trained model is saved as `models/fraud_model.joblib`, while evaluation results are stored in `models/evaluation_metrics.json`. The backend loads the saved model to generate predictions without retraining it each time the application starts.



## FastAPI Backend

The backend is developed using FastAPI and organized into separate modules:

- `app/main.py` defines API routes and handles requests.
- `app/schemas.py` validates incoming transaction data.
- `app/model_service.py` loads the trained model and performs prediction operations.

The API provides endpoints for application information, health checks, monitoring metrics, individual transaction predictions, and batch predictions. When a request is received, the backend validates the input, processes the transaction using the trained model, and returns the prediction in JSON format.



## Streamlit Dashboard

The Streamlit dashboard, implemented in `streamlit_app.py`, provides a user-friendly interface for interacting with the fraud detection system. Users can enter transaction features, submit prediction requests, and view whether the model classifies a transaction as potentially fraudulent or legitimate.

The dashboard can display prediction results, summary metrics, recent predictions, interactive charts, and available API health information. HTTPX connects the dashboard to the FastAPI backend, while Plotly provides interactive visualizations.



## Monitoring and Testing

The project includes basic API monitoring for request counts, prediction counts, fraud predictions, errors, and uptime. The `monitoring/drift_monitor.py` module provides a foundation for checking changes in incoming transaction features compared with reference data.

The `tests/test_api.py` module contains automated API tests. Docker configuration files provide a foundation for containerized execution. These features should be tested to confirm that they work correctly in the target environment.



## How to Run the Backend and Dashboard



### Step 1: Open the project directory

Open Visual Studio Code and select the project folder:

`REAL_TIME_FRAUD_DETECTION_API`

Open a PowerShell terminal in this directory.



### Step 2: Install dependencies

Run the following command to install the required Python packages into the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the trained model does not exist, verify that `data/creditcard.csv` is present and run the training script:

```powershell
.\.venv\Scripts\python.exe train.py
```

Wait for training to finish successfully.



### Step 3: Start the FastAPI backend

Open the first PowerShell terminal in the project directory and run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal open while using the dashboard.

The backend will be available at:

- API home: `http://127.0.0.1:8000/`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

The API documentation can be used to inspect endpoints and test transaction prediction requests.



### Step 4: Start the Streamlit dashboard

Open a **second PowerShell terminal** in the same project directory. Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

Streamlit will display a local URL in the terminal. Open the displayed address, normally:

`http://localhost:8501`



### Step 5: Test the application

1. Confirm that the FastAPI backend is running on port `8000`.
2. Open the Streamlit dashboard on port `8501`.
3. Enter the transaction features required by the trained model.
4. Submit the transaction for analysis.
5. Review the prediction returned by the API and displayed on the dashboard.

The dashboard depends on the backend being available. If predictions fail, verify that the API is running, the model artifact exists, the required features are supplied, and the dashboard is configured to call the correct API URL.



## Expected Outcomes

The intended outcome is an integrated machine learning application that accepts transaction features, predicts potential fraud, exposes prediction services through REST endpoints, and presents results in an interactive dashboard. It demonstrates practical skills in data preprocessing, model development, API integration, data visualization, testing, and deployment concepts.

Actual prediction quality depends on the trained model and its evaluation results. The system's predictions are risk indicators and should not be treated as guaranteed fraud determinations.



## Conclusion

The Real-Time Credit Card Fraud Detection API demonstrates how machine learning can be integrated into a usable software application. By combining Python, Scikit-learn, FastAPI, Streamlit, and supporting tools, the project covers model training, prediction services, interactive visualization, basic monitoring, and deployment preparation. It provides a strong foundation for an aspiring Machine Learning Engineer's portfolio and can be extended with authentication, persistent monitoring, model versioning, and cloud deployment.
 
