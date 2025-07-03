# GödelOS - A Cognitive Architecture with Real-time Transparency

[![Version](https://img.shields.io/badge/version-0.3-blue.svg)](https://github.com/yourusername/godelos)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

GödelOS is a sophisticated cognitive architecture system that demonstrates human-like reasoning processes through multiple cognitive layers, featuring real-time transparency into AI decision-making.

## 🚀 Getting Started

This guide will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8+
- Node.js and npm (for the Svelte frontend)

### Installation

1.  **Set up the Python Environment:**

    Run the setup script to create a virtual environment and install all Python dependencies.
    ```bash
    chmod +x setup_venv.sh
    ./setup_venv.sh
    ```
    This will create a `godelos_venv` directory with all the necessary packages.

2.  **Activate the Virtual Environment:**

    Before running the application, you must activate the virtual environment.
    ```bash
    source godelos_venv/bin/activate
    ```

3.  **Set up the Frontend:**

    Navigate to the frontend directory and install the Node.js dependencies.
    ```bash
    cd svelte-frontend
    npm install
    cd ..
    ```

## 🏗️ Running the Application

### 1. Start the Backend Server

With the virtual environment activated, start the FastAPI backend server.

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

### 2. Start the Frontend Development Server

In a separate terminal, navigate to the frontend directory and start the development server.

```bash
cd svelte-frontend
npm run dev
```
- **Frontend UI**: `http://localhost:5173` (or the port specified by Vite)

## ��️ Project Structure

The project is organized into several key directories:

```
GödelOS/
├── backend/              # FastAPI backend application
├── svelte-frontend/      # Svelte frontend application
├── godelOS/              # Core cognitive architecture logic
├── tests/                # Python test suite
├── scripts/              # Utility and maintenance scripts
├── docs/                 # Project documentation
├── logs/                 # Application logs
├── project_archive/      # Old scripts and reports
├── requirements.txt      # Core Python dependencies
├── setup_venv.sh         # Environment setup script
└── README.md             # This file
```

## 🧪 Running Tests

### Backend Tests

To run the Python test suite, use `pytest`:

```bash
# Make sure the virtual environment is activated
source godelos_venv/bin/activate

# Run all tests
pytest
```

### Frontend Tests

To run the Playwright tests for the frontend:

```bash
cd svelte-frontend
npm test
```

## 📄 License

This project is licensed under the MIT License.
