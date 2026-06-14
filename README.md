# Dynamic Multi-Agent AI Sandbox

A proof-of-concept architecture for a dynamic, LLM-orchestrated execution engine. This system leverages a lightweight LLM acting as a routing agent to classify user intents and dispatch tasks to specialized, isolated Docker sandboxes.

It allows users to upload files (images, CSVs) and provide natural language prompts. The system dynamically writes the necessary Python code, executes it securely in an ephemeral container with no internet access, and returns the processed output (annotated images, graphs, and terminal logs) back to a React frontend.

---

## Architecture Overview

| Layer | Technology |
|---|---|
| **Frontend** | React (Vite) — handles multipart form data (text prompts + file uploads) |
| **Backend** | FastAPI — API Gateway managing ephemeral volume mounts and container lifecycles |
| **Orchestrator** | Gemini 2.5 Flash API — handles intent routing and domain-specific code generation |
| **Execution Engine** | Isolated Docker containers tailored for specific tasks |

### Sandboxes

- `yolo-sandbox` — Object detection using Ultralytics YOLOv8
- `mobilenet-sandbox` — Image classification using PyTorch MobileNetV2
- `data-sandbox` — Time-series forecasting using Pandas and Scikit-Learn

---

## Prerequisites

Ensure the following are installed before proceeding:

- Python 3.10+
- Node.js (v18+) & npm
- Docker Desktop (must be running in the background)
- Google Gemini API Key

---

## Setup

### 1. Clone and Configure Environment

1. Navigate to the `backend` folder.
2. Create a file named `.env`.
3. Add your API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Build the Docker Sandboxes

The system relies on pre-built, domain-specific Docker images. Build them locally before starting the backend.

```bash
cd sandbox

# Object Detection environment
docker build -t yolo-sandbox -f Dockerfile.yolo .

# Image Classification environment
docker build -t mobilenet-sandbox -f Dockerfile.mobilenet .

# Data Science environment
docker build -t data-sandbox -f Dockerfile.data .
```

> **Note:** This step may take a few minutes as it downloads PyTorch and other heavy dependencies.

### 3. Start the Backend Server

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

The backend will be listening at `http://127.0.0.1:8000`.

### 4. Start the Frontend

```bash
cd frontend

npm install
npm run dev
```

Open your browser at the local address shown by Vite (usually `http://localhost:5173`).

---

## Testing the Agents

### Test 1 — Object Detection (YOLO)

- **Upload:** Any image containing multiple objects (people, cars, electronics)
- **Prompt:** `Detect all objects in this image. Draw bounding boxes around them and print their coordinates.`

### Test 2 — Image Classification (MobileNet)

- **Upload:** A clear image of a single subject (e.g., a dog, a coffee cup)
- **Prompt:** `Classify this image. Print the top 3 predicted class names.`

### Test 3 — Time-Series Forecasting (Data Science)

- **Upload:** A CSV file named `campus_toto_demand.csv` with columns `day` and `rides`, containing at least 10 rows of data
- **Prompt:** `Read the dataset. Use sklearn LinearRegression to train a model predicting 'rides' based on the 'day'. Forecast the demand for days 11, 12, and 13. Plot the historical data points and a line representing the regression forecast, and explicitly save the plot.`