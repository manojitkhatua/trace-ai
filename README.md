# TRACE — Transaction Risk Assessment & Continuous Evaluation

> An intelligent transaction risk assessment platform that combines machine learning, anomaly detection, entity intelligence, explainability, and auditability to turn transaction data into actionable decisions.

**TRACE Decisions:** `ALLOW` · `REVIEW` · `BLOCK`

### 🚀 Live Demo
[Open TRACE](https://trace-gq747476y-manojitkhatuas-projects.vercel.app/#/app/investigation)

---

## Overview

TRACE is an end-to-end fraud risk assessment system built for transaction-level decisioning.

Instead of relying only on a machine learning fraud probability, TRACE combines three complementary signals:

1. **Fraud Probability** — predicted by a LightGBM model
2. **Anomaly Score** — identifies unusual transaction behavior
3. **Entity Risk** — evaluates card, device, address, network, and relationship patterns

These signals are combined into a single **0–100 risk score**, which is converted into an operational decision.

```text
Transaction
     │
     ▼
┌─────────────────────┐
│  Fraud Prediction   │
│      LightGBM       │
└──────────┬──────────┘
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
┌─────────────────┐     ┌─────────────────┐
│ Anomaly Engine  │     │ Entity Risk     │
│                 │     │ Engine          │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
             ┌──────────────┐
             │ Risk Engine  │
             └───────┬──────┘
                     ▼
             ┌──────────────┐
             │ Decision     │
             │ Engine       │
             └───────┬──────┘
                     ▼
            ┌──────────────────┐
            │ ALLOW / REVIEW   │
            │      / BLOCK     │
            └──────────────────┘
                     │
                     ▼
          Explainability + Audit
```

---

## Problem Statement

Fraud detection is not only a binary classification problem.

A transaction can look normal from one perspective while appearing suspicious from another. For example:

- the ML model can assign a high fraud probability,
- transaction behavior can be unusual,
- a card-device relationship can be suspicious,
- missing information can contain useful signal.

A useful fraud system therefore needs to answer:

```text
How risky is this transaction?
Why is it risky?
What should the system do?
Can the decision be reviewed later?
```

TRACE is designed around these questions.

---

## Solution

TRACE transforms raw transaction information into an operational risk decision.

```text
Raw Transaction
      ↓
Preprocessing
      ↓
Feature Engineering
      ↓
LightGBM Fraud Model
      ↓
Anomaly Detection
      ↓
Entity Risk Analysis
      ↓
Combined Risk Score
      ↓
Decision Policy
      ↓
ALLOW / REVIEW / BLOCK
      ↓
Explanation + Audit
```

The system separates:

- **Prediction** — how likely a transaction is to be fraudulent
- **Risk Assessment** — how risky the transaction is overall
- **Decisioning** — what operational action should be taken

---

# Why TRACE?

TRACE follows a simple product principle:

> **Simple outside. Sophisticated inside.**

The analyst-facing workflow is:

```text
Analyze
   ↓
Decision
   ↓
Why?
   ↓
Investigation
   ↓
Audit
```

The technical complexity remains inside the system.

---

# End-to-End Architecture

```text
                         TRACE PLATFORM
                              │
                    ┌─────────▼─────────┐
                    │      Frontend     │
                    │   React + Vite    │
                    └─────────┬─────────┘
                              │
                           HTTP/API
                              │
                    ┌─────────▼─────────┐
                    │     Flask API     │
                    │      /predict     │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
     ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
     │ Fraud       │   │ Anomaly     │   │ Entity      │
     │ Predictor   │   │ Engine      │   │ Risk Engine │
     └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                     ┌────────────────┐
                     │   Risk Engine  │
                     └───────┬────────┘
                             ▼
                     ┌────────────────┐
                     │ Decision Engine│
                     └───────┬────────┘
                             ▼
                  ┌────────────────────────┐
                  │ Explanation + Audit    │
                  └────────────────────────┘
```

---

# Dataset

TRACE was developed using an IEEE-CIS-style fraud detection dataset.

The project uses a chronological train/validation split.

```text
Total transaction rows : 590,540
Training split         : 80%
Validation split       : 20%
Validation rows        : 118,108
Validation fraud rows  : 4,064
```

Transactions are sorted using `TransactionDT`, and the later portion is used for validation.

This avoids mixing future transactions into training and gives a more realistic evaluation setup.

---

# Data Preparation

The original data is separated into transaction and identity tables.

```text
train_transaction.csv
        +
train_identity.csv
        ↓
Merged transaction dataset
```

The tables are joined using:

```text
TransactionID
```

Identity information provides fields including:

- `DeviceInfo`
- `DeviceType`

---

# Feature Engineering

The final LightGBM model uses **36 features**.

## Transaction Features

- `TransactionAmt`
- `log_transaction_amount`

## Missingness Features

- `addr1_missing`
- `addr2_missing`
- `D7_missing`
- `D12_missing`
- `D13_missing`
- `D14_missing`
- `DeviceInfo_missing`

## Temporal Features

- `time_since_previous_transaction`
- `has_previous_transaction`

## Entity Features

Training-derived transaction frequency features are created for relevant card and address entities.

## Relationship Features

- Card + DeviceInfo transaction frequency
- Unique DeviceInfo count for a card
- Unique card count for a DeviceInfo

## Categorical Features

One-hot encoded:

- Product category
- Card network
- Card type
- Device type

---

# Model Development

TRACE uses a **LightGBM binary classification model** as the main fraud predictor.

Model artifact:

```text
models/lightgbm_final.pkl
```

Model configuration:

```text
models/lightgbm_config.json
```

The inference pipeline reproduces the same preprocessing used during model development.

This includes:

- training-derived entity mappings,
- card-device mappings,
- one-hot encoding,
- feature configuration,
- temporal configuration,
- exact feature order validation.

---

# Model Performance

The final LightGBM model achieved:

```text
PR-AUC  : 0.2371
ROC-AUC : 0.8217
```

Selected classification threshold:

```text
0.40
```

Validation performance at this threshold:

```text
F1 Score  : 0.3031
Precision : 0.2440
Recall    : 0.4001
```

Because the fraud dataset is imbalanced, precision-recall behavior is an important part of evaluation.

---

# Fraud Prediction Layer

The `FraudPredictor` is responsible for:

1. Loading the trained LightGBM model
2. Loading preprocessing artifacts
3. Reproducing training-time feature engineering
4. Creating the final 36-feature input
5. Generating fraud probability
6. Providing model explainability information

The predictor also checks the feature count and feature order before inference.

---

# Anomaly Detection

The Anomaly Engine asks a different question:

> Does this transaction look unusual compared with expected behavior?

The anomaly engine uses signals related to:

- transaction amount,
- entity behavior,
- missingness patterns.

Configured anomaly weights:

```text
Amount       : 30%
Entity       : 55%
Missingness  : 15%
```

The anomaly score is represented between:

```text
0 → low anomaly
1 → high anomaly
```

---

# Entity Risk

The Entity Risk Engine evaluates risk associated with transaction entities and their relationships.

Relevant signals include:

- card behavior,
- device behavior,
- address behavior,
- card-device relationships,
- network-related patterns.

Training-derived mappings are stored under:

```text
models/preprocessing/
```

Key mapping artifacts include:

```text
entity_maps.pkl
pair_map.pkl
card_device_map.pkl
device_card_map.pkl
```

---

# Risk Engine

TRACE combines the three major signals into a single operational score.

Current weights:

```text
Fraud Probability : 55%
Anomaly Score     : 20%
Entity Risk       : 25%
```

Formula:

```text
Risk Score =
    0.55 × Fraud Probability
  + 0.20 × Anomaly Score
  + 0.25 × Entity Risk
```

The result is represented on a 0–100 scale.

### Example

```text
Fraud Probability = 0.80
Anomaly Score     = 0.40
Entity Risk       = 0.60
```

Then:

```text
Risk =
    (0.80 × 100 × 0.55)
  + (0.40 × 100 × 0.20)
  + (0.60 × 100 × 0.25)

Risk = 69
```

---

# Decision Engine

TRACE converts the risk score into an operational decision.

| Risk Score | Risk Level | Decision |
|---:|---|---|
| 0–39.99 | LOW | ALLOW |
| 40–69.99 | MEDIUM | REVIEW |
| 70–100 | HIGH | BLOCK |

Therefore:

```text
LOW
 ↓
ALLOW

MEDIUM
 ↓
REVIEW

HIGH
 ↓
BLOCK
```

The decision policy is separated from the ML model.

---

# Explainability

TRACE exposes the major factors behind a transaction assessment.

The result includes:

- Fraud Probability
- Anomaly Score
- Entity Risk
- Combined Risk Score
- Risk Level
- Decision

TRACE also supports SHAP-based model contribution analysis.

Important model signals include:

- transaction amount,
- card-device relationship features,
- product category,
- entity frequency,
- temporal signals,
- missingness indicators.

SHAP is used to explain model contribution, not to claim causality.

---

# Audit Trail

TRACE records transaction analysis and decisions for later review.

The audit layer supports:

- transaction history,
- risk scores,
- decisions,
- analysis results,
- historical investigation.

The goal is to make each decision traceable:

```text
What happened?
     ↓
Why did TRACE decide this?
     ↓
What action was taken?
```

---

# Backend

TRACE uses Flask for the backend API.

Main endpoint:

```text
POST /predict
```

Backend flow:

```text
Request
  ↓
Fraud Predictor
  ↓
Anomaly Engine
  ↓
Entity Risk Engine
  ↓
Risk Engine
  ↓
Decision Engine
  ↓
Gemini Explanation
  ↓
Audit Logger
  ↓
JSON Response
```

---

# Backend Components

```text
src/backend/
│
├── app.py
├── anomaly_engine.py
├── audit_logger.py
├── decision_engine.py
├── entity_risk_engine.py
├── gemini_service.py
└── risk_engine.py
```

### `app.py`

Runs the Flask application and orchestrates the complete prediction pipeline.

### `anomaly_engine.py`

Calculates transaction anomaly risk.

### `entity_risk_engine.py`

Calculates entity and relationship risk.

### `risk_engine.py`

Combines fraud, anomaly, and entity signals.

### `decision_engine.py`

Converts the risk score into:

```text
ALLOW / REVIEW / BLOCK
```

### `gemini_service.py`

Generates natural-language explanations and recommended actions.

### `audit_logger.py`

Records analysis and decision history.

---

# Frontend

The frontend is built with React and Vite.

Main application pages:

```text
/
    Landing Page

/sign-in
    Demo Sign In

/app
    Overview

/app/analyze
    Transaction Analysis

/app/investigation
    Investigation

/app/audit-trail
    Audit Trail
```

The interface is designed around an analyst workflow rather than a generic ML dashboard.

---

# Frontend Workflow

```text
Overview
   ↓
Analyze Transaction
   ↓
Risk Assessment
   ↓
Why did TRACE decide?
   ↓
Investigation
   ↓
Audit Trail
```

The Analyze page focuses on the most useful analyst inputs.

Technical model fields are kept under:

```text
Advanced / Model Signals
```

---

# API

## POST `/predict`

Endpoint:

```text
http://localhost:5000/predict
```

### Request

```json
{
  "TransactionAmt": 44.266,
  "TransactionDT": 12352706,
  "card1": 9026,
  "card2": 545,
  "addr1": null,
  "addr2": null,
  "D7": 0,
  "D12": 0,
  "D13": null,
  "D14": 0,
  "DeviceInfo": "Moto E (4) Build/NMA26.42-69",
  "ProductCD": "C",
  "card4": "visa",
  "card6": "credit",
  "DeviceType": "desktop"
}
```

### Response

```json
{
  "fraud_probability": 0.8841,
  "anomaly_score": 0.4973,
  "entity_risk": 0.6274,
  "risk_score": 74.26,
  "risk_level": "HIGH",
  "decision": "BLOCK"
}
```

The backend response can also contain explanation, anomaly details, entity breakdown, and audit information.

---

# Real Validation Example

One of the strongest TRACE validation examples is a genuine fraud transaction from the chronological validation set.

```text
Transaction ID : 3464297
Amount         : 44.266

Fraud Probability : 88.41%
Anomaly Score     : 49.73%
Entity Risk       : 62.74%

TRACE Risk Score : 74.26
Risk Level       : HIGH
Decision         : BLOCK
```

This case was found in the real validation data rather than being manually constructed to force a BLOCK result.

---

# Demo Scenarios

TRACE supports three operational states.

## Low Risk

```text
Fraud Probability ≈ 8%
Risk Score ≈ 16.83

LOW
 ↓
ALLOW
```

## Medium Risk

```text
Risk Score between 40 and 70

MEDIUM
 ↓
REVIEW
```

## High Risk

Using the real validation transaction `3464297`:

```text
Fraud Probability = 88.41%
Anomaly Score     = 49.73%
Entity Risk       = 62.74%

Risk Score = 74.26

HIGH
 ↓
BLOCK
```

---

# Project Structure

```text
trace-ai/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── trace/
│   │   │   └── ui/
│   │   │
│   │   ├── context/
│   │   │   └── TraceContext.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Overview.jsx
│   │   │   ├── Analyze.jsx
│   │   │   ├── Investigation.jsx
│   │   │   ├── RiskIntelligence.jsx
│   │   │   ├── AuditTrail.jsx
│   │   │   ├── Landing.jsx
│   │   │   └── SignIn.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── utils/
│   │   │   ├── demoData.js
│   │   │   ├── format.js
│   │   │   ├── options.js
│   │   │   ├── risk.js
│   │   │   └── cn.ts
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── src/
│   ├── backend/
│   │   ├── app.py
│   │   ├── anomaly_engine.py
│   │   ├── audit_logger.py
│   │   ├── decision_engine.py
│   │   ├── entity_risk_engine.py
│   │   ├── gemini_service.py
│   │   └── risk_engine.py
│   │
│   └── models/
│       └── predictor.py
│
├── models/
│   ├── lightgbm_final.pkl
│   ├── lightgbm_config.json
│   ├── anomaly_config.json
│   └── preprocessing/
│       ├── entity_maps.pkl
│       ├── pair_map.pkl
│       ├── card_device_map.pkl
│       ├── device_card_map.pkl
│       ├── onehot_encoder.pkl
│       ├── feature_config.pkl
│       └── temporal_config.pkl
│
├── scripts/
│   ├── find_trace_demo_cases.py
│   ├── test_predictor.py
│   └── test_real_validation_cases_fixed.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Installation

## Prerequisites

Install:

```text
Python 3.x
Node.js
npm
Git
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/manojitkhatua/trace-ai
cd trace-ai
```

---

## 2. Create the Python Environment

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\activate
```

---

## 3. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

If required:

```powershell
pip install flask-cors
```

---

## 4. Start the Backend

From the project root:

```powershell
.\.venv\Scripts\python.exe src\backend\app.py
```

Backend:

```text
http://localhost:5000
```

---

## 5. Install Frontend Dependencies

Open another terminal:

```powershell
cd frontend
npm install
```

---

## 6. Start the Frontend

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# Running TRACE

Open:

```text
http://localhost:5173
```

Application:

```text
http://localhost:5173/app
```

Transaction analysis:

```text
http://localhost:5173/app/analyze
```

---

# Quick Start

```text
1. Start Flask backend
        ↓
2. Start React frontend
        ↓
3. Open /app/analyze
        ↓
4. Enter a transaction
        ↓
5. Run TRACE Analysis
        ↓
6. Review risk score
        ↓
7. Inspect why TRACE decided
        ↓
8. Open Investigation
        ↓
9. Review Audit Trail
```

---

# Technology Stack

## Machine Learning

- Python
- LightGBM
- scikit-learn
- pandas
- NumPy
- SHAP
- joblib

## Backend

- Flask
- Flask-CORS

## Frontend

- React
- Vite
- JSX
- Tailwind CSS
- React Router
- Lucide Icons

## AI Explanation

- Gemini service integration

---

# Security and Data Handling

Do not commit secrets or unnecessary local artifacts.

Do not push:

```text
.env
API keys
credentials
.venv/
node_modules/
raw datasets
temporary files
private secrets
```

Use environment variables for secrets and API credentials.

Recommended `.gitignore` entries include:

```gitignore
.venv/
__pycache__/
*.pyc

.env
.env.*
!.env.example

node_modules/
frontend/dist/

data/
*.csv
*.zip

.idea/
.vscode/
```

---

# Limitations

TRACE is a prototype fraud-risk decision platform.

Before production financial use, the system would require additional:

- security controls,
- authentication and authorization,
- model calibration,
- model monitoring,
- data drift monitoring,
- concept drift monitoring,
- false-positive analysis,
- adversarial testing,
- compliance review,
- production infrastructure,
- secure secret management,
- high-availability deployment.

The current demo authentication is frontend-only and should not be treated as production authentication.

---

# Future Improvements

## Real-Time Transaction Streaming

Connect TRACE to a live transaction stream for continuous monitoring.

## Online Entity Intelligence

Continuously update entity and behavioral signals as transactions arrive.

## Model Monitoring

Track:

```text
Data Drift
Concept Drift
Precision
Recall
PR-AUC
False Positive Rate
```

over time.

## Analyst Feedback

Allow investigators to mark transactions as:

```text
Confirmed Fraud
Confirmed Legitimate
Needs Review
```

and use those labels to improve future model development.

## Production Deployment

Deploy the frontend, backend, ML service, monitoring and secure infrastructure using a production cloud architecture.

---

# Design Philosophy

TRACE separates technical complexity from analyst experience.

Internally:

```text
ML
+
Anomaly Detection
+
Entity Intelligence
+
Explainability
+
Decisioning
+
Audit
```

Externally:

```text
Decision
↓
Risk
↓
Reason
↓
Action
↓
History
```

---

# Core Idea

TRACE is not simply a fraud classifier.

It is a **fraud risk decision system**.

```text
Machine Learning
      ↓
"How likely is this transaction to be fraudulent?"

Risk Layer
      ↓
"How risky is this transaction overall?"

Decision Layer
      ↓
"What should the system do?"
```

The complete workflow is:

```text
PREDICT
   ↓
ASSESS
   ↓
EXPLAIN
   ↓
DECIDE
   ↓
AUDIT
```

---

# Team

Built as an end-to-end fintech fraud detection and transaction risk assessment platform.

**TRACE — Transaction Risk Assessment & Continuous Evaluation**
