# HisaabFlow Architecture

This document provides a detailed overview of the HisaabFlow application's architecture, covering the backend, frontend, and the data processing pipeline.

## High-Level Overview

HisaabFlow is a web application that runs locally in a single Docker container. A React frontend talks to a Python/FastAPI backend, and the backend also serves the built frontend, so the browser uses one origin (`http://127.0.0.1:8000`). All data processing happens on the user's machine.

```
                               +--------------------+
                               |   Frontend (UI)    |
                               | (React, browser)   |
                               +--------------------+
                                        |
                                        | (API Calls)
                                        v
+--------------------------------------------------------------------------+
|                               Backend (API)                              |
|                                 (FastAPI)                                |
+--------------------------------------------------------------------------+
|        |                |                  |                 |           |
|        v                v                  v                 v           v
|  +-----------+    +-----------+    +---------------+    +-----------+    +---------+
|  | File Mgmt |    | Parsing   |    | Transformation|    | Transfer  |    | Config  |
|  | Service   |    | Service   |    | Service       |    | Detection |    | Service |
|  +-----------+    +-----------+    +---------------+    +-----------+    +---------+
|        |                |                  |                 |           |
|        |                |                  |                 |           |
|        v                v                  v                 v           v
|  +--------------------------------------------------------------------------+
|  |                              Core Logic                                |
|  +--------------------------------------------------------------------------+
|  | Bank Detection | CSV Processing | Data Cleaning | Transfer Matching | ... |
|  +--------------------------------------------------------------------------+

```

## Backend Architecture

The backend is a FastAPI application that exposes a RESTful API for the frontend. It is responsible for all data processing, including parsing, cleaning, transformation, and transfer detection.

### Key Components:

*   **API Endpoints**: The `backend/api` directory contains the FastAPI routers that define the API endpoints. Each file corresponds to a specific set of related endpoints (e.g., `file_endpoints.py`, `parse_endpoints.py`).

*   **Services Layer**: The `backend/services` directory contains the business logic of the application. Each service is responsible for a specific part of the workflow:
    *   `MultiCSVService`: Orchestrates the processing of multiple CSV files.
    *   `ParsingService`: Handles the parsing of individual CSV files.
    *   `TransformationService`: Manages the transformation of data into the standard Cashew format.
    *   `TransferProcessingService`: Contains the logic for detecting transfers between accounts.
    *   `UnknownBankService`: Provides the functionality for handling unknown banks.
    *   `ExportService`: Manages the export of data to a CSV file.

*   **Core Logic**: The `backend/core` directory contains the core data processing algorithms:
    *   `BankDetector`: Identifies the source bank for each CSV file.
    *   `CSVProcessingService`: Handles the low-level details of CSV parsing.
    *   `DataCleaningService`: Cleans and standardizes the data.
    *   `CashewTransformationService`: Transforms the data into the internal standard format.
    *   `TransferDetection`: Contains the sophisticated algorithms for matching transfers between accounts.

### Data Processing Pipeline:

The backend follows a well-defined data processing pipeline:

1.  **File Upload**: The user uploads one or more CSV files.
2.  **Bank Detection**: The `BankDetector` identifies the bank for each file.
3.  **Parsing**: The `ParsingService` uses the appropriate `.conf` file to parse each CSV.
4.  **Cleaning**: The `DataCleaningService` standardizes and cleans the parsed data.
5.  **Transformation**: The `TransformationService` converts the data into the standard Cashew format.
6.  **Transfer Detection**: The `TransferProcessingService` analyzes the data to identify transfers.
7.  **Export**: The `ExportService` generates the final, unified CSV file.

## Frontend Architecture

The frontend is a single-page application built with React (Create React App). In Docker the backend serves the production build; during development the CRA dev server proxies `/api` to the backend (`src/setupProxy.js`).

### Key Components:

*   **`App.js`**: The main entry point of the React application.
*   **`AppLogic.js`**: The core component that manages the application's state and renders the different steps of the workflow.
*   **Components**: The UI is built from a set of reusable React components located in the `frontend/src/components` directory.
*   **Steps**: The application is divided into a series of steps, each corresponding to a specific part of the workflow (e.g., `FileUploadStep`, `ConfigureAndReviewStep`).
*   **State Management**: The application currently uses a combination of local component state (managed with React's `useState` hook) and props to manage the application's state. A planned Zustand migration was dropped; state handling will be revisited once the app has persistent storage.
*   **API Services**: The frontend communicates with the backend through a set of API service functions located in the `frontend/src/services` directory.

## Key Technologies

*   **Backend**: Python, FastAPI, Pydantic
*   **Frontend**: React, axios, react-hot-toast
*   **Data Processing**: Pandas
*   **Configuration**: `.conf` files (parsed with Python's `configparser`)

## Deployment

*   **Image** (`Dockerfile`): a Node stage builds the frontend; a `python:3.11-slim` stage runs `uvicorn backend.main:app` on port 8000 and serves both `/api/v1` and the UI.
*   **Data** (`docker-compose.yml`): `./data` on the host is mounted at `/data`. Bank and app configs live in `/data/configs` (`HISAABFLOW_CONFIG_DIR`). `docker/entrypoint.sh` copies shipped configs that are missing there, never overwriting existing files, then drops root.
*   **Config location** (`backend/infrastructure/config/paths.py`): `HISAABFLOW_CONFIG_DIR` if set, otherwise the repository's `configs/`.
*   **Network**: compose publishes the port on `127.0.0.1` only. There is no authentication and no CORS; the app is meant for one user on their own machine.

