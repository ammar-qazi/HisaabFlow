# HisaabFlow Architecture

This document provides a detailed overview of the HisaabFlow application's architecture, covering the backend, frontend, and the data processing pipeline.

## High-Level Overview

HisaabFlow is a desktop application built with a modern, decoupled architecture. It consists of a React/Electron frontend and a Python/FastAPI backend. All data processing is done locally on the user's machine, ensuring privacy and security.

```
                               +--------------------+
                               |   Frontend (UI)    |
                               | (React + Electron) |
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

The frontend is a single-page application built with React and packaged as a desktop application using Electron.

### Key Components:

*   **`App.js`**: The main entry point of the React application.
*   **`AppLogic.js`**: The core component that manages the application's state and renders the different steps of the workflow.
*   **Components**: The UI is built from a set of reusable React components located in the `frontend/src/components` directory.
*   **Steps**: The application is divided into a series of steps, each corresponding to a specific part of the workflow (e.g., `FileUploadStep`, `ConfigureAndReviewStep`).
*   **State Management**: The application currently uses a combination of local component state (managed with React's `useState` hook) and props to manage the application's state. A migration to a more centralized state management solution like Zustand is planned.
*   **API Services**: The frontend communicates with the backend through a set of API service functions located in the `frontend/src/services` directory.

## Key Technologies

*   **Backend**: Python, FastAPI, Pydantic
*   **Frontend**: React, Electron, Material-UI
*   **Data Processing**: Pandas
*   **Configuration**: `.conf` files (parsed with Python's `configparser`)
