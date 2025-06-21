# HisaabFlow - Codebase Structure & Key Files

## Project Directory Structure
```
HisaabFlow/
├── backend/               # FastAPI backend service
│   ├── api/              # API endpoints and routers
│   ├── bank_detection/   # Bank identification logic
│   ├── csv_parser/       # CSV parsing strategies
│   ├── csv_preprocessing/# Data preprocessing
│   ├── data_cleaning/    # Data validation and cleaning
│   ├── services/         # Business logic services
│   ├── transfer_detection/# Transfer matching logic
│   ├── main.py          # FastAPI entry point (125 lines)
│   ├── requirements.txt  # Python dependencies
│   └── venv/            # Virtual environment
├── frontend/             # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.js       # Main React app (74 lines)
│   │   └── ...
│   ├── package.json     # Node.js dependencies
│   └── node_modules/    # Frontend dependencies
├── configs/             # Bank configuration files
├── sample_data/         # Test data for development
├── memory/              # AI assistant memory files
├── start_app.sh         # One-command launcher script
├── README.md            # Project documentation
├── CURRENT_STATE.md     # Development progress tracker
├── CODEBASE_MAP.md      # File inventory and sizes
├── AI_WORKFLOW.md       # Development guidelines
└── SYSTEM_DESIGN.md     # Architecture documentation
```

## Critical File Size Status
- **✅ Ready for modification**: main.py (125 lines), App.js (74 lines)
- **🚨 Requires splitting**: Many backend modules over 200 lines
- **📝 Documentation**: 4 core tracking files (CURRENT_STATE, CODEBASE_MAP, etc.)

## Key Entry Points
- **Backend**: `backend/main.py` - FastAPI application
- **Frontend**: `frontend/src/App.js` - React application
- **Startup**: `start_app.sh` - Complete setup and launch
- **Config**: `configs/app.conf` - Application configuration