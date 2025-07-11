# Plan: User-Driven Configuration via "Advanced Mode"

## 1. Executive Summary

This document outlines the plan to implement a powerful "Advanced Mode" for the HisaabFlow application. This feature will empower users to process CSV files from unknown banks by creating their own parsing configurations directly within the UI. This addresses a critical limitation where the application can only handle banks with pre-existing `.conf` files.

The core of this feature is to repurpose the existing `PreviewService` and `detect-range` capabilities to guide the user through a manual setup process, and then allow them to **save their work as a new `.conf` file**, making future processing of that bank's statements fully automatic.

## 2. Feature Proposal

-   **Trigger:** When a user uploads a CSV and the backend identifies the bank as "unknown".
-   **Frontend Workflow ("Advanced Mode"):**
    1.  The UI presents an "Advanced Configuration" panel.
    2.  The user is shown a preview of the CSV and a suggested header row (powered by the `PreviewService`).
    3.  The user confirms or corrects the header row.
    4.  The user maps the columns from their CSV (e.g., "Transaction Detail", "Debit Amount") to the application's standard fields (`Description`, `Amount`, etc.).
    5.  The user provides a name for this new bank configuration.
    6.  The user clicks "Save and Parse".
-   **Backend Action:**
    1.  A new API endpoint (`/api/v1/save-config`) receives the user-defined configuration.
    2.  The backend creates a new, properly formatted `.conf` file in the `configs/` directory.
    3.  The application immediately re-parses the file using this new configuration.

## 3. Expert Panel Analysis & Recommendations

A consultation with a simulated expert panel (Lead Backend Engineer, Senior Configuration Architect, UX-Focused Frontend Engineer) produced the following consensus and recommendations.

### 3.1. Configuration Architect's View

**Focus:** Robustness and maintainability of the configuration system.

-   **Analysis:** The current system is too rigid. The lack of a graceful fallback for unknown banks is a major architectural weakness.
-   **Recommendations:**
    1.  **Create Fallback Defaults:** Add a `[fallback_defaults]` section to `configs/app.conf`. This will contain generic rules for things like date formats and description cleaning, providing a sensible baseline for the user's manual configuration.
    2.  **Systematize Fallbacks:** The `UnifiedConfigService` must be updated to read these defaults and construct a temporary, in-memory configuration when a specific bank `.conf` file is not found. This makes the fallback behavior reliable and centralized.

### 3.2. Lead Backend Engineer's View

**Focus:** API design, data flow, and service architecture.

-   **Analysis:** The `/save-config` endpoint is currently a non-functional placeholder. A new, well-defined API contract is needed to support this feature.
-   **Recommendations:**
    1.  **Implement `save-config` Logic:** The endpoint must be implemented to accept a JSON payload, sanitize the inputs (especially the new bank name to prevent security issues), format the data into the `.conf` file structure, and write it to the filesystem.
    2.  **Define a Strict API Contract:** Create a new Pydantic model (`UserCreatedConfig`) in `backend/api/models.py`. This model will define the exact shape of the data the frontend must send, ensuring type safety and preventing invalid data from being saved.

### 3.3. UX-Focused Frontend Engineer's View

**Focus:** Creating an intuitive and empowering user experience.

-   **Analysis:** The current "dead end" for unknown banks is a poor user experience. The "Advanced Mode" must feel like a feature, not a workaround.
-   **Recommendations:**
    1.  **Clear UI Trigger:** The advanced panel should only appear when `bank_name` is "unknown".
    2.  **Guided Workflow:** The UI should guide the user step-by-step: first confirm the header, then map columns.
    3.  **Leverage Existing APIs:** The frontend should use the existing `/preview` and `/detect-range` endpoints to pre-fill information for the user, minimizing their effort.
    4.  **Instant Feedback:** After the user saves the new configuration, the frontend should automatically trigger a re-parse so the user immediately sees the successful result of their work.

## 4. Phased Implementation Plan

This plan is designed to be executed "backend-first," allowing the API to be ready before frontend development begins.

### Phase 1: Strengthen the Configuration Foundation (Backend)

-   **Action 1.1:** Add a `[fallback_defaults]` section to `configs/app.conf` with generic rules for date formats and description cleaning.
-   **Action 1.2:** Modify `UnifiedConfigService` in `backend/infrastructure/config/unified_config_service.py` to load and apply these defaults when a specific bank configuration is not found.

### Phase 2: Build the Save Configuration API (Backend)

-   **Action 2.1:** Create a new Pydantic model `UserCreatedConfig` in `backend/api/models.py` to define the request body for the save operation.
-   **Action 2.2:** Implement the full logic for the `/api/v1/save-config` endpoint in `backend/api/config_endpoints.py`. This includes receiving the `UserCreatedConfig` payload, formatting it, and writing the new `.conf` file.

### Phase 3: Implement the Advanced Mode (Frontend)

-   **Action 3.1:** Develop the conditional UI panel that appears for unknown banks.
-   **Action 3.2:** Integrate calls to the `/preview` and `/detect-range` endpoints to populate the UI with suggestions.
-   **Action 3.3:** Implement the column mapping interface (e.g., dropdowns).
-   **Action 3.4:** Implement the final "Save and Parse" functionality, which calls the new `/save-config` endpoint and then triggers a re-parse on success.

## 5. Conclusion

This plan provides a clear path to implementing a high-value feature that significantly improves the application's flexibility and user experience. It leverages existing components, adheres to the project's design principles, and follows a logical, phased rollout.
