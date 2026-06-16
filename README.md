# 🐛 Bug Severity Predictor

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?logo=supabase&logoColor=white)
![Render](https://img.shields.io/badge/Backend-Render-46E3B7?logo=render&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

An AI-powered web application that predicts the **severity of software bugs** (Critical, High, Medium, Low) using a neural network classifier trained on historical bug-tracking data. Built with a FastAPI backend, a Streamlit frontend, JWT-based authentication, and role-based access for customers and admins.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [How the Model Works](#-how-the-model-works)
- [Getting Started Locally](#-getting-started-locally)
- [API Reference](#-api-reference)
- [Deployment](#-deployment)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 📖 Overview

When a bug is reported in a software project, triaging it correctly — deciding how urgent it is — is a critical but time-consuming task. **Bug Severity Predictor** automates this by analyzing structured bug metadata (component, environment, affected users, response time, business impact, and more) and instantly predicting how severe the bug is, along with a confidence score for each possible severity class.

The app supports two types of users:

- **Customers** can submit bug details and get instant predictions, view their personal prediction history, and see their own analytics dashboard.
- **Admins** get a control panel with access to all predictions, all registered users, login activity logs, and aggregate statistics across the system.

---

##  Live Demo

| Component | URL |
|---|---|
| **Frontend (Streamlit)** | https://bug-severity-predictor-jhbig6p4ztbgfd3vzzwql6.streamlit.app/ |
| **Backend (FastAPI)** | https://bug-severity-predictor-ucxb.onrender.com |
| **API Docs (Swagger)** | https://bug-severity-predictor-ucxb.onrender.com/docs |

> ⚠️ Note: The backend runs on Render's free tier, so the first request after a period of inactivity may take 30-50 seconds while the server "wakes up." Subsequent requests will be fast.

---

## ✨ Features

- 🔐 **Secure Authentication** — JWT-based login/register system with hashed passwords (bcrypt)
- 🎯 **AI-Powered Predictions** — Severity classification (Critical / High / Medium / Low) with per-class confidence scores
- 📊 **Interactive Visualizations** — Probability bar charts, severity distribution pie charts, and confidence box plots (Plotly)
- 📋 **Personal History** — Every user can filter, view, and download their own past predictions as CSV
- 🛡️ **Role-Based Admin Panel** — Admins can view all predictions, all users, login logs, and system-wide statistics
- 🌐 **Persistent Cloud Database** — All data (users, predictions, login logs) stored permanently in PostgreSQL (Supabase), surviving backend restarts and redeploys
- ⚡ **Lightweight ML Model** — Uses scikit-learn's MLPClassifier instead of a heavy deep learning framework, keeping memory usage low enough to run on free-tier cloud hosting

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit, Plotly, Pandas |
| **Backend / API** | FastAPI, Uvicorn, Pydantic |
| **Authentication** | JWT (python-jose), Passlib (bcrypt) |
| **Machine Learning** | scikit-learn (MLPClassifier), NumPy |
| **Database** | PostgreSQL (hosted on Supabase) |
| **Backend Hosting** | Render |
| **Frontend Hosting** | Streamlit Community Cloud |

---

## 🏗 Architecture

```
┌─────────────────┐        HTTPS / JSON         ┌──────────────────┐
│                  │  ───────────────────────▶   │                  │
│  Streamlit App   │                              │   FastAPI App    │
│  (Frontend UI)   │  ◀───────────────────────   │   (Backend API)  │
│                  │        JWT-authenticated     │                  │
└─────────────────┘                              └─────────┬────────┘
                                                              │
                                          ┌───────────────────┼───────────────────┐
                                          │                   │                   │
                                 ┌────────▼───────┐  ┌────────▼────────┐ ┌────────▼────────┐
                                 │  ML Model       │  │  PostgreSQL DB  │ │  Auth Module     │
                                 │  (scikit-learn) │  │  (Supabase)     │ │  (JWT + bcrypt)  │
                                 └─────────────────┘  └─────────────────┘ └──────────────────┘
```

The frontend never talks to the database or the model directly — every interaction goes through the FastAPI backend, which handles authentication, prediction logic, and data persistence.

---

## 📂 Project Structure

```
bug-severity-predictor/
│
├── data/
│   ├── bugs.csv                  # Raw training dataset
│   └── processed_bugs.csv        # Cleaned dataset
│
├── notebooks/
│   └── analysis.ipynb            # EDA, training experiments, evaluation
│
├── model/
│   ├── train_sklearn.py          # Training script (scikit-learn MLPClassifier)
│   ├── train.py                  # Original training script (TensorFlow/Keras reference)
│   ├── model_sklearn.pkl         # Trained model (production)
│   ├── scaler.pkl                # Fitted StandardScaler
│   └── label_encoder.pkl         # Fitted LabelEncoders (features + target)
│
├── backend/
│   ├── app.py                    # FastAPI application & routes
│   ├── predict.py                # Model loading & prediction logic
│   ├── database.py               # PostgreSQL connection + queries
│   └── auth.py                   # JWT creation/validation, password hashing
│
├── frontend/
│   ├── streamlit_app.py          # Streamlit UI (login, predict, dashboards, admin)
│   └── requirements.txt          # Frontend-only dependencies (lightweight)
│
├── tests/
│   ├── test_api.py               # API endpoint tests
│   └── test_model.py             # Model prediction tests
│
├── docs/
│   └── report.pdf                # Project report
│
├── requirements.txt              # Backend dependencies
├── runtime.txt                   # Python version pin (for Render)
├── README.md
├── .env                          # Environment variables (not committed)
└── .gitignore
```

---

## 🧠 How the Model Works

1. **Input features** — 31 fields describing a bug: its type, the affected component, environment, platform, OS, browser, who reported it, current status, plus numeric/behavioral metrics like affected users, response time, business impact score, reproduction rate, memory/CPU usage, fix time, reopen count, and security/SLA flags.
2. **Preprocessing** — Categorical fields are label-encoded; all features are scaled using a `StandardScaler` fitted during training.
3. **Model** — A Multi-Layer Perceptron (`MLPClassifier`) with hidden layers `(256, 128, 64, 32)`, ReLU activation, and L2 regularization, trained with early stopping to prevent overfitting.
4. **Output** — A predicted severity class (`Critical`, `High`, `Medium`, `Low`) along with a probability distribution across all four classes, which the frontend renders as a confidence score and a bar chart.

The model achieves **~91% accuracy** on a held-out test set.

> **Why scikit-learn instead of a deep learning framework?** The model was originally trained as a TensorFlow/Keras ANN. However, TensorFlow's memory footprint exceeded the limits of free-tier cloud hosting, causing the deployed API to crash. Re-training the same architecture as a scikit-learn `MLPClassifier` preserved comparable accuracy while reducing memory usage enough to run reliably on free infrastructure — a common trade-off when deploying ML models under resource constraints.

---

## 💻 Getting Started Locally

### Prerequisites
- Python 3.11
- A PostgreSQL database (Supabase free tier works well) **or** modify `database.py` to use SQLite for local-only testing

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/bug-severity-predictor.git
cd bug-severity-predictor
```

### 2. Set up the backend
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file (or set environment variables) with:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET=your-secret-key
```

Run the backend:
```bash
cd backend
uvicorn app:app --reload --port 8000
```

### 3. Set up the frontend
In a new terminal:
```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Update `API_URL` in `streamlit_app.py` to point to `http://localhost:8000` for local development.

### 4. (Optional) Retrain the model
```bash
cd model
python train_sklearn.py
```

---

## 📡 API Reference

Interactive documentation is auto-generated by FastAPI and available at `/docs` (Swagger UI) once the backend is running.

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/` | No | Health check |
| `POST` | `/register` | No | Create a new user account |
| `POST` | `/login` | No | Authenticate and receive a JWT token |
| `POST` | `/predict` | Yes | Submit bug details, get severity prediction |
| `GET` | `/my-history` | Yes | Get the current user's past predictions |
| `GET` | `/my-stats` | Yes | Get severity breakdown for the current user |
| `GET` | `/admin/all-predictions` | Admin | Get every prediction in the system |
| `GET` | `/admin/all-users` | Admin | List all registered users |
| `GET` | `/admin/stats` | Admin | System-wide severity statistics |
| `GET` | `/admin/login-logs` | Admin | View login activity history |

All authenticated routes expect a header: `Authorization: Bearer <token>`.

---

## ☁️ Deployment

| Component | Platform | Notes |
|---|---|---|
| **Backend API** | [Render](https://render.com) (Free Web Service) | Root directory left blank; start command: `uvicorn backend.app:app --host 0.0.0.0 --port 10000` |
| **Frontend** | [Streamlit Community Cloud](https://share.streamlit.io) | Main file path: `frontend/streamlit_app.py`; uses its own lightweight `requirements.txt` |
| **Database** | [Supabase](https://supabase.com) (Free PostgreSQL) | Connected via the **Transaction Pooler** connection string for IPv4 compatibility with Render |

Environment variables required on the backend host:
```
DATABASE_URL=<your Supabase transaction pooler connection string>
```

> **Note on Render's free tier:** The service spins down after periods of inactivity and "cold starts" on the next request, which can take up to a minute. This is expected behavior on the free plan, not a bug.

---

## 🔮 Future Improvements

- Add password reset / forgot-password flow
- Move secrets fully to environment variables across all environments
- Add automated CI tests on push (GitHub Actions)
- Add pagination for large prediction history tables
- Containerize the backend with Docker for more portable deployment
- Add model versioning so retrained models can be rolled back if needed

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Latika Chaudhary

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY ARISING FROM THE USE OF THE SOFTWARE.
```

---

## 🙋 Author

**Latika Chaudhary**

MCA graduate currently focused on AI/ML projects. This project was built to explore end-to-end machine learning deployment — from model training to a fully authenticated, cloud-hosted full-stack application covering the backend API, database design, and frontend UI.

Feel free to explore the code or reach out with feedback!
