# Product Requirements Document: HisaabFlow

**Version:** 1.1
**Date:** 2025-07-12

## 1. Introduction

HisaabFlow is a cross-platform desktop application designed to simplify and automate the process of preparing bank statement data for personal budgeting applications. It addresses the common pain point of manually cleaning, formatting, and reconciling CSV exports from multiple different banks, each with its own unique format. By providing a powerful, configuration-driven pipeline, HisaabFlow transforms messy, inconsistent bank statements into a single, clean, and standardized dataset ready for import into popular budgeting tools.

The core philosophy of HisaabFlow is **privacy and control**. All data processing occurs locally on the user's machine, ensuring that sensitive financial information never leaves their computer.

## 2. Target Audience

The primary users of HisaabFlow are financially-conscious individuals who:
- Use personal budgeting software (e.g., YNAB, Cashew, Aspire Budgeting).
- Manage accounts across multiple banks and financial institutions.
- Regularly download and import transaction data via CSV files.
- Are comfortable with desktop software and value data privacy.

## 3. Goals and Objectives

- **Primary Goal:** To drastically reduce the time and effort required to aggregate and standardize bank statement CSVs from multiple sources.
- **Secondary Goal:** To provide a secure, private, and offline-first tool for handling sensitive financial data.
- **User Experience Goal:** To offer an intuitive, step-by-step workflow that guides the user from raw file upload to clean data export with minimal friction, including a guided setup for unknown banks.

## 4. Core Features (Functional Requirements)

### 4.1. Multi-File CSV Upload
- Users must be able to upload one or more CSV files simultaneously via a drag-and-drop interface.

### 4.2. Automatic Bank Detection
- The system must automatically identify the source bank for each uploaded CSV file.
- Detection shall be based on a confidence scoring system using file name patterns and content signatures defined in configuration files.

### 4.3. Configuration-Driven Parsing
- All parsing logic (e.g., column mapping, date format, currency handling) must be driven by bank-specific `.conf` files.
- This allows for easy extension to new banks without changing the core application code.

### 4.4. Interactive Data Preview and Review
- The application must display a preview of the parsed data in an interactive grid.
- Users must be able to review the parsed data and, if necessary, override suggested parsing parameters (e.g., header row, data start row).

### 4.5. Data Cleaning and Standardization
- The system must perform automated data cleaning, including:
  - Standardizing date formats.
  - Cleaning transaction descriptions (e.g., removing redundant text).
  - Converting currency amounts to a consistent numerical format.

### 4.6. Automated Transfer Detection
- The system must intelligently identify and categorize transfer transactions between different accounts.
- Detection should be based on a confidence algorithm that matches transaction amounts and dates across different files.

### 4.7. Manual Transfer Confirmation
- The UI must present users with potential transfer pairs that the system is not 100% confident about.
- Users must be able to manually review and confirm these pairs, improving the accuracy of the final dataset.

### 4.8. Standardized Data Export
- The final, processed data must be exportable as a single, clean CSV file.
- The export format should be standardized and ready for direct import into budgeting applications.

### 4.9. Cross-Platform Desktop Application
- The application must be available as a standalone desktop application for Windows, macOS, and Linux.

### 4.10. Local-First Data Processing
- All file processing, parsing, and transformation must occur entirely on the user's local machine. No financial data should be transmitted over the network.

### 4.11. Advanced Configuration Mode for Unknown Banks
- **Trigger:** If the automatic bank detection for an uploaded CSV results in a confidence score below a configurable threshold, the system will not attempt to parse it automatically.
- **Advanced Mode UI:** The file will be presented in an "Advanced Configuration" view where the user can:
    - Preview the raw CSV data.
    - Visually map columns (e.g., "Transaction Date", "Description", "Amount") to the standard HisaabFlow fields.
    - Specify the header row and the first data row.
    - Provide a name for the new bank configuration.
- **Dynamic Configuration Saving:** The user can save these settings as a new `.conf` file directly from the UI.
- **Immediate Reload:** Upon saving, the backend will immediately load the new configuration file.
- **Dynamic UI Update:** The frontend will refresh its list of available banks, and the newly created configuration will be automatically selected for the file, allowing the user to proceed with parsing and transformation without restarting the application.

## 5. User Flow

The following diagram illustrates the user's journey through the HisaabFlow application:

```
(Start) --> [Launch App] --> [Upload CSVs]
              ^
              |
              +---- (User has more files to process)

[Upload CSVs] --> [For each CSV] --> |Auto-detect Bank?|

|Auto-detect Bank?| -- Yes --> [Apply Config] --> [Parse Data] --> |All files parsed?|
|Auto-detect Bank?| -- No ---> [Enter Advanced Config Mode]

[Enter Advanced Config Mode] --> [User maps columns] --> [User saves new config] --> [Apply Config]

|All files parsed?| -- Yes --> [Transform & Analyze Data]
|All files parsed?| -- No ---> (Wait for other files)

[Transform & Analyze Data] --> [Run Transfer Detection] --> [Display Unified Data]

[Display Unified Data] --> |Manual Transfer Confirmation?| -- Yes --> [User confirms pairs]
|Manual Transfer Confirmation?| -- No ---> [Export CSV]

[User confirms pairs] --> [Export CSV]

[Export CSV] --> (End)
```

### Step-by-Step Description:

1.  **Launch & Upload**: The user starts the application and uploads one or more CSV files.
2.  **Bank Detection**: The system analyzes each file to identify the bank.
3.  **Configuration**: 
    *   If the bank is **known**, the system automatically applies the existing configuration.
    *   If the bank is **unknown**, the user is guided through the **Advanced Configuration Mode** to create a new configuration by mapping columns and setting parameters.
4.  **Parsing**: Each file is parsed into a standard format based on its configuration.
5.  **Transformation & Analysis**: Once all files are parsed, the system unifies the data, performs data cleaning, and runs the transfer detection algorithm.
6.  **Review & Confirmation**: The user reviews the combined dataset and can manually confirm any potential transfer pairs.
7.  **Export**: The user exports the final, clean dataset as a single CSV file.

## 6. Non-Functional Requirements

- **Performance:** The application should be responsive and able to process typical bank statements (hundreds to thousands of rows) within a few seconds.
- **Usability:** The interface must be clean, modern, and intuitive, guiding the user through the workflow with clear instructions and feedback.
- **Security & Privacy:** As a local-first application, it must not make any external network requests with user data. The bundled backend must be sandboxed within the application.
- **Compatibility:** The application must be compatible with the latest versions of Windows, macOS (Intel & Apple Silicon), and major Linux distributions (via AppImage).

## 7. Assumptions & Dependencies

- Users have access to their bank statements in CSV format.
- The structure of a bank's CSV export does not change frequently.
- The user's machine has sufficient resources to run a React/Electron application.

## 8. Out of Scope (Future Considerations)

- Direct integration with bank APIs (Plaid, etc.).
- Cloud synchronization or multi-device support.
- Multi-user accounts or collaboration features.
- Advanced data visualization or budgeting features within the app itself.