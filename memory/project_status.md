# Bank Statement Parser - Project Memory

## Current Status (June 2025)
- Project: Bank Statement/CSV Parser for Cashew
- Main issue: Codebase has grown unwieldy with many large files
- Refactoring needed to improve maintainability

## Architecture Overview
- Backend: FastAPI server with multiple CSV parsers and transfer detectors
- Frontend: Web interface for uploading and processing statements
- Core modules: CSV parsing, transfer detection, data cleaning, transformations

## Files Requiring Immediate Refactoring (>300 lines)
1. **backend/transfer_detector_enhanced_ammar.py** (858 lines) - PRIMARY TARGET
2. **backend/main.py** (724 lines) - FastAPI server
3. **backend/transfer_detector_enhanced.py** (604 lines) 
4. **backend/data_cleaner.py** (587 lines)
5. **backend/enhanced_csv_parser.py** (549 lines)
6. **transformation/universal_transformer.py** (499 lines)
7. **backend/csv_parser.py** (336 lines)
8. **launch_gui.py** (327 lines)

## Current Refactoring Plan
- Target: 300 lines max per file
- Approach: Modular design with single responsibility
- Start with largest file: transfer_detector_enhanced_ammar.py

## Known Issues
- Multiple duplicate/backup versions of transfer detectors
- Large monolithic files difficult to maintain
- Need cleaner separation of concerns

## Recent Refactoring (Current Session)

### ✅ COMPLETED: transfer_detector_enhanced_ammar.py Refactoring
- **Original file**: 858 lines → **Broken into 7 modules** (50-150 lines each)
- **New structure**: `backend/transfer_detection/` package with:
  - `main_detector.py` - Main orchestration (150 lines)
  - `cross_bank_matcher.py` - Cross-bank transfer logic (200 lines)
  - `currency_converter.py` - Currency conversion matching (120 lines)
  - `exchange_analyzer.py` - Exchange amount detection (80 lines)
  - `confidence_calculator.py` - Confidence scoring (60 lines)
  - `amount_parser.py` - Amount parsing utilities (30 lines)
  - `date_parser.py` - Date parsing utilities (50 lines)
  - `__init__.py` - Package exports (15 lines)
- **Backward compatibility**: `transfer_detector_enhanced_ammar_refactored.py` wrapper
- **Benefits**: Single responsibility, easier testing, better maintainability

## Next Steps
1. ✅ **DONE**: Refactor transfer_detector_enhanced_ammar.py 
2. Test the refactored module to ensure functionality
3. Continue with next largest file: backend/main.py (724 lines)
4. Update imports in dependent files if needed
