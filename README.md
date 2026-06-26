# 🧪 AI Laboratory: Dynamic Model Selection (Stage 1)

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

This project is an interactive, sandbox-driven educational platform designed to teach students (Class 6-12) the fundamentals of Artificial Intelligence. It features a dual-login architecture, a modular pedagogical dashboard, and dynamic data variant selection for Regression, Classification, and Neural Network models.

## ✨ Features

*   **🎓 4-Pillar Educational Dashboard:**
    *   **AI Foundations:** Learn the core concepts and the emergence of intelligence.
    *   **Prediction Engine (Lab Workspace):** A visual workspace where students can plot and interpret data before running ML models.
    *   **Data Lab:** Explore and manipulate data variants to understand data-centric AI.
    *   **Agentic Sandbox:** An interactive sandbox for exploring agentic flows and AI decision-making.
*   **👥 Dual-Login Architecture:** Separate portals for Students and Administrators.
*   **📊 Dynamic Data Variants:** Real-time selection of data scenarios for Regression, Classification, and Neural Networks.
*   **🔒 Secure Execution:** Uses Gemini LLM to securely execute machine learning code inside an isolated Docker sandbox.

## 🏗️ Architecture Overview

The project is split into two main components:
*   **Backend (Django + Django REST Framework):** Handles user authentication, manages the "Scenarios" and "Data Variants" catalogs, generates synthetic data on the fly via python scripts (`dataset_generators.py`), and executes tasks asynchronously.
*   **Frontend (React + Vite):** A minimalist, pure Single-Page Application (SPA) styled with Vanilla CSS and Glassmorphism.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
*   **Python 3.10+**
*   **Node.js 18+** (with npm)
*   **Docker** (Required for the `classification-sandbox` image used to execute the student models securely).

---

## 🚀 Setup Instructions

### 1. Backend Setup (Django)

Open a terminal and navigate to the backend directory:
```bash
cd Stage1/backend
```

**Create and activate a virtual environment:**
*   *Windows:* `python -m venv venv` and `.\venv\Scripts\activate`
*   *Mac/Linux:* `python3 -m venv venv` and `source venv/bin/activate`

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file at the root of the project (next to this README) and add your database and API keys:
```env
DATABASE_URL="postgresql://<user>:<password>@<host>/<db>"
GEMINI_API_KEY="your_google_gemini_key_here"
DJANGO_SECRET_KEY="your_secret_key"
REDIS_URL="redis://127.0.0.1:6379/0"
```

**Run Database Migrations:**
```bash
python manage.py migrate
```

**Seed the Database (Important):**
The UI requires the scenarios and variants to exist in the database. Run the seeder to populate the catalog:
```bash
python manage.py seed_scenarios
```

**Create an Admin / Test Account:**
Create a superuser to access both the Student and Admin portals:
```bash
python manage.py createsuperuser
```

**Start Redis:**
Redis is required for Celery tasks and WebSockets (Django Channels). If you have Docker installed, you can quickly spin one up:
```bash
docker run -d -p 6379:6379 redis
```

**Start the Celery Worker (In a new terminal window):**
Ensure your virtual environment is active, then run:
```bash
cd Stage1/backend
celery -A config worker -l info --pool=solo
```
*(Note: `--pool=solo` is often required on Windows).*

**Start the Backend Server (In a new terminal window):**
```bash
python manage.py runserver
```
*(The backend runs on `http://localhost:8000`)*

---

### 2. Frontend Setup (React/Vite)

Open a **second terminal window** and navigate to the frontend directory:
```bash
cd Stage1/frontend
```

**Install npm packages:**
```bash
npm install
```

**Start the Frontend Development Server:**
```bash
npm run dev
```
*(The frontend runs on `http://localhost:5173`)*

---

## 🧪 Testing and Usage

1.  Open `http://localhost:5173` in your browser.
2.  Use the toggle switch on the Login screen to select **Student**.
3.  Log in using the email and password you created via the `createsuperuser` command.
4.  You will land on the **Student Dashboard**. Explore the 4 core modules: AI Foundations, Prediction Engine, Data Lab, and Agentic Sandbox.
5.  In the **Prediction Engine**, select a model from the left sidebar (e.g., Regression).
6.  Select a scenario (e.g., The Haunted House Price Predictor).
7.  Click on one of the **Data Variant Cards** (e.g., "The Missing Roofs").
8.  Review the plotted graph and the **Data Story** interpretation panel.
9.  Click **Run Model** to trigger the backend execution and view the AI's explanation of the results!

*(Note: You can also use the login toggle to sign in as an **Admin** to view the structural placeholder for the Stage 2 Admin portal).*