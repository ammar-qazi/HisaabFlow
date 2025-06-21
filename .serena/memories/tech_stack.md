# HisaabFlow - Tech Stack & Architecture

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Dependencies**: 
  - pandas >= 2.0.0 (data manipulation)
  - pydantic >= 2.0.0 (data validation)
  - uvicorn >= 0.20.0 (ASGI server)
  - python-multipart >= 0.0.6 (file uploads)

### Frontend
- **Framework**: React 18.2.0 with JavaScript
- **Build Tool**: react-scripts 5.0.1
- **HTTP Client**: axios 1.4.0
- **Data Grid**: ag-grid-react 30.0.0 & ag-grid-community 30.0.0
- **Desktop App**: Electron 25.0.0
- **Development**: concurrently & wait-on for dev server coordination

### Data Storage & Processing
- **File Storage**: Temporary files using Python's `tempfile` module
- **Configuration**: File-based `.conf` files in `configs/` directory
- **Data Processing**: In-memory using pandas DataFrames
- **Results**: CSV file exports (no persistent database)

## Architecture

### Service Architecture
```
Frontend (React/JavaScript)
    ↓
Backend API (FastAPI/Python)
    ↓
In-Memory Processing (pandas)
    ↓
File Export (CSV downloads)
```

### Data Flow
1. File Upload → Frontend uploads to temporary files
2. File Validation → Backend API validates format
3. Parse Processing → In-memory pandas processing
4. Configuration Application → Rules applied from .conf files
5. Results Export → CSV download to user

### Storage Reality
- **No Database**: Application is stateless, no persistent data storage
- **Temporary Processing**: Files processed in-memory and discarded
- **Configuration-Driven**: Bank rules stored as filesystem .conf files
- **Export-Focused**: Results downloaded as CSV files

### Module Structure
- **Backend**: Modular API with endpoint routers, configuration-based parsing
- **Frontend**: Modern 3-step workflow (Upload → Configure → Review & Export)
- **Configuration**: `.conf` files for bank-specific parsing rules
- **Processing**: Stateless in-memory data transformation pipeline