# Bug Analysis and Fix Strategy: July 22

This document outlines the bugs identified from the application logs on July 22, their root causes, and potential solutions.

---

### Bug 1: Incorrect Column Mapping in Transformation (Critical)

-   **Symptom:** The transformation process fails, producing zero valid rows. The logs show that a generic, case-sensitive column mapping is used (`{'Amount': 'Amount', 'Date': 'Date', ...}`) instead of the correct, bank-specific mapping from `Bunq.conf` (`amount = Amount`, `date = Date`).
-   **Root Cause:** The `TransformationService` is not using the column mapping from the detected bank's configuration. It appears to be falling back to a default mapping created from the headers of the raw CSV data. The `MultiCSVService`, which prepares the data for transformation, fails to retrieve and inject the correct mapping for the `Bunq` bank.
-   **Potential Fixes:**
    1.  **Modify `TransformationService` (Recommended):** Update the service to explicitly fetch the `column_mapping` from the `UnifiedConfigService` using the provided bank name before it begins the transformation.
    2.  **Modify `MultiCSVService`:** Ensure that when `MultiCSVService` processes the files, it correctly retrieves the bank-specific column mapping and includes it in the data payload sent to the `TransformationService`.
    3.  **Modify Frontend:** The frontend could send the correct mapping, but a backend fix is more robust and reliable.

---

### Bug 2: Stale Data from Initial Parse (High)

-   **Symptom:** The frontend sends stale data to the transformation endpoint. The logs show that even after the bank is correctly identified as `Bunq`, the data still contains artifacts from the initial, incorrect parse (e.g., `Currency: 'PKR'`).
-   **Root Cause:** The frontend's state management is incomplete. After a new bank configuration is created, the `handleConfigCreated` function in `ConfigureAndReviewStep.js` triggers a *preview*, which updates the bank detection result, but it does not re-trigger the *parsing and cleaning* process. Therefore, the application proceeds with the old, incorrectly processed data.
-   **Potential Fixes:**
    1.  **Update Frontend State Logic (Recommended):** In `ConfigureAndReviewStep.js`, after the `previewFile` call in `handleConfigCreated` successfully completes, trigger the `parseAllFiles` function. This will ensure the data is re-processed with the correct configuration, refreshing the frontend's state completely.
    2.  **Defensive Backend Logic:** The `TransformationService` could be enhanced to detect a mismatch between the provided `bank_name` and the `_source_bank` in the data. If a mismatch is found, it could re-parse the data. This would make the backend more resilient but doesn't fix the underlying frontend issue.

---

### Bug 3: Invalid Regex Patterns in Bank Detection (Medium)

-   **Symptom:** The logs show warnings like `[WARNING] Invalid regex pattern '*statement*': nothing to repeat at position 0`.
-   **Root Cause:** The `BankDetector` treats all filename patterns from `.conf` files as regular expressions. The "unknown bank" workflow saves glob-style patterns (`*...*`) which are not valid regex syntax, causing `re.match` to fail.
-   **Potential Fixes:**
    1.  **Smarter Pattern Matching (Recommended):** Modify the `BankDetector` to differentiate between simple and regex patterns. For example, only treat patterns that start with `^` or end with `$` as regex, and use simple substring containment for others.
    2.  **Update Config Format:** Introduce separate keys in the `.conf` file for `filename_patterns` (for simple matching) and `filename_regex` (for regex matching). This is a cleaner but more involved change.
    3.  **Improve "Unknown Bank" Workflow:** Update the workflow to generate valid regex patterns (e.g., `.*statement.*`) instead of glob patterns when saving a new configuration.

---

### Bug 4: Incomplete Saved Configuration (Medium)

-   **Symptom:** The `Bunq.conf` file created by the "unknown bank" workflow is missing the `header_row` setting in the `[csv_config]` section.
-   **Root Cause:** The `UnknownBankService` and its corresponding API endpoint (`/api/v1/unknown-bank/save-config`) do not have a mechanism to determine or save the header row. The UI does not prompt for it, and the backend analysis does not auto-detect and save it.
-   **Potential Fixes:**
    1.  **Enhance `analyze-csv` Endpoint (Recommended):** The `/api/v1/unknown-bank/analyze-csv` endpoint should be improved to auto-detect the most likely header row and include it in its analysis results.
    2.  **Update `save-config` Endpoint:** The `/api/v1/unknown-bank/save-config` endpoint must be updated to accept a `header_row` parameter and write it to the `[csv_config]` section of the new `.conf` file.
    3.  **Add UI Input:** The `UnknownBankPanel` component in the frontend should be updated to include a field where the user can confirm or manually enter the correct header row number.
