# Codebase Map & File Inventory

## 🧹 CLEAN BASELINE AFTER STRATEGIC ROLLBACK
**Status:** Fresh foundation with preserved documentation
**Rollback Date:** 2025-06-21
**Baseline Commit:** 933a04c (Consolidate memory documents)
**Strategy:** Clean slate for constraint-aware development

## 📊 File Status Overview - POST-ROLLBACK

| Path | Lines | Purpose | Status | Notes |
|------|-------|---------|--------|-------|
| **📚 PRESERVED DOCUMENTATION** | | | | |
| AI_WORKFLOW.md | ~120 | Development guidelines | ✅ Preserved | **Guides constraint-aware development** |
| CURRENT_STATE.md | ~150 | Project state tracking | ✅ Updated | **Fresh start status** |
| DATA_STANDARDS.md | ~180 | Data format specs | ✅ Preserved | **Format guidelines** |
| SYSTEM_DESIGN.md | ~200 | Architecture docs | ✅ Preserved | **System overview** |
| CODEBASE_MAP.md | ~250 | File inventory | ✅ Updated | **This document** |
| **🚨 BACKEND CONSTRAINT VIOLATIONS** | | | | |
| backend/services/transformation_service.py | 688 | Transform services | 🚨 Over Limit | **CRITICAL - 244% over!** |
| backend/transfer_detection/cross_bank_matcher.py | 533 | Transfer matching | 🚨 Over Limit | **CRITICAL - 167% over!** |
| backend/services/multi_csv_service.py | 382 | Multi-CSV handling | 🚨 Over Limit | **91% over limit** |
| backend/bank_detection/config_manager.py | 316 | Bank config mgmt | 🚨 Over Limit | **58% over limit** |
| backend/csv_parser/unified_parser.py | 312 | Main CSV parser | 🚨 Over Limit | **56% over limit** |
| backend/transfer_detection/config_manager.py | 295 | Transfer config | 🚨 Over Limit | **48% over limit** |
| backend/csv_preprocessing/csv_preprocessor.py | 281 | CSV preprocessing | 🚨 Over Limit | **41% over limit** |
| backend/csv_parser/parsing_strategies.py | 277 | Parsing strategies | 🚨 Over Limit | **39% over limit** |
| backend/csv_parser/data_processor.py | 276 | Data processing | 🚨 Over Limit | **38% over limit** |
| backend/api/multi_csv_processor.py | 265 | Multi-CSV API | 🚨 Over Limit | **33% over limit** |
| backend/csv_parser/dialect_detector.py | 252 | CSV dialect detect | 🚨 Over Limit | **26% over limit** |
| backend/data_cleaning/data_cleaner.py | 246 | Data cleaning | 🚨 Over Limit | **23% over limit** |
| backend/csv_parser/encoding_detector.py | 235 | Encoding detection | 🚨 Over Limit | **18% over limit** |
| backend/services/cashew_transformer.py | 231 | Cashew transform | 🚨 Over Limit | **16% over limit** |
| backend/api/template_manager.py | 220 | Template management | 🚨 Over Limit | **10% over limit** |
| backend/api/config_manager.py | 209 | Config management | 🚨 Over Limit | **5% over limit** |
| backend/bank_detection/bank_detector.py | 205 | Bank detection | 🚨 Over Limit | **3% over limit** |
| **🚨 FRONTEND CONSTRAINT VIOLATIONS** | | | | |
| frontend/src/ModernizedPrototype.js | 883 | Modern UI prototype | 🚨 Over Limit | **CRITICAL - 342% over!** |
| frontend/src/components/modern/ModernDataReviewStep.js | 651 | Data review UI | 🚨 Over Limit | **226% over limit** |
| frontend/src/components/modern/ModernFileConfigurationStep.js | 521 | File config UI | 🚨 Over Limit | **161% over limit** |
| frontend/src/components/modern/transform-export/InteractiveDataTable.js | 399 | Data table UI | 🚨 Over Limit | **100% over limit** |
| frontend/src/components/modern/configure-review/TransactionReview.js | 322 | Transaction review | 🚨 Over Limit | **61% over limit** |
| frontend/src/components/modern/ModernFileUploadStep.js | 318 | File upload UI | 🚨 Over Limit | **59% over limit** |
| frontend/src/components/modern/ModernAppLogic.js | 313 | App logic | 🚨 Over Limit | **57% over limit** |
| frontend/src/MultiCSVApp.js | 209 | Multi-CSV UI | 🚨 Over Limit | **5% over limit** |
| **✅ COMPLIANT FILES** | | | | |
| backend/main.py | 125 | FastAPI entry | ✅ Compliant | **Ready for modification** |
| backend/api/csv_processor.py | 137 | Single CSV API | ✅ Compliant | **Ready for modification** |
| backend/api/parse_endpoints.py | 154 | CSV parsing API | ✅ Compliant | **Ready for modification** |
| frontend/src/App.js | 74 | Main React app | ✅ Compliant | **Ready for modification** |

## 🏗️ Backend Structure (Clean Baseline)
```
backend/
├── api/
│   ├── __init__.py
│   ├── config_endpoints.py        ✅ Stable endpoint handling
│   ├── config_manager.py          🚨 209 lines - needs split
│   ├── csv_processor.py           ✅ 137 lines - compliant
│   ├── file_endpoints.py          ✅ Stable file operations
│   ├── file_manager.py            ✅ File management utilities
│   ├── middleware.py              ✅ API middleware
│   ├── models.py                  ✅ 78 lines - Pydantic models
│   ├── multi_csv_processor.py     🚨 265 lines - needs split
│   ├── parse_endpoints.py         ✅ 154 lines - compliant
│   ├── routes.py                  ✅ Main router setup
│   ├── template_manager.py        🚨 220 lines - needs split
│   └── transform_endpoints.py     ✅ Transform API
├── bank_detection/
│   ├── __init__.py
│   ├── bank_detector.py           🚨 205 lines - needs split
│   └── config_manager.py          🚨 316 lines - needs split
├── csv_parser/
│   ├── __init__.py
│   ├── data_processor.py          🚨 276 lines - needs split
│   ├── dialect_detector.py        🚨 252 lines - needs split
│   ├── encoding_detector.py       🚨 235 lines - needs split
│   ├── exceptions.py              ✅ Exception definitions
│   ├── parsing_strategies.py      🚨 277 lines - needs split
│   ├── structure_analyzer.py      ✅ Structure analysis
│   ├── unified_parser.py          🚨 312 lines - needs split
│   └── utils.py                   ✅ Utility functions
├── csv_preprocessing/
│   ├── __init__.py
│   └── csv_preprocessor.py        🚨 281 lines - needs split
├── data_cleaning/
│   ├── __init__.py
│   ├── bom_cleaner.py             ✅ 102 lines - compliant
│   ├── column_standardizer.py     ✅ 158 lines - compliant
│   ├── currency_handler.py        ✅ 131 lines - compliant
│   ├── data_cleaner.py            🚨 246 lines - needs split
│   ├── data_validator.py          ✅ 153 lines - compliant
│   ├── date_cleaner.py            ✅ 155 lines - compliant
│   ├── numeric_cleaner.py         ✅ 150 lines - compliant
│   └── quality_checker.py         ✅ 174 lines - compliant
├── services/
│   ├── cashew_transformer.py      🚨 231 lines - needs split
│   ├── export_service.py          ✅ Export functionality
│   ├── multi_csv_service.py       🚨 382 lines - needs split
│   ├── parsing_service.py         ✅ Parsing coordination
│   ├── preview_service.py         ✅ File preview
│   └── transformation_service.py  🚨 688 lines - CRITICAL!
├── transfer_detection/
│   ├── __init__.py
│   ├── amount_parser.py           ✅ Amount parsing
│   ├── confidence_calculator.py   ✅ Confidence scoring
│   ├── config_loader.py           ✅ Config loading
│   ├── config_manager.py          🚨 295 lines - needs split
│   ├── config_models.py           ✅ Configuration models
│   ├── cross_bank_matcher.py      🚨 533 lines - CRITICAL!
│   ├── currency_converter.py      ✅ Currency conversion
│   ├── date_parser.py             ✅ Date parsing
│   ├── enhanced_config_manager.py ✅ Enhanced config
│   ├── exchange_analyzer.py       ✅ Exchange analysis
│   └── main_detector.py           ✅ 184 lines - compliant
├── MAIN_SIZE_CONTROL.md           📚 Size control documentation
├── data_cleaner.py                ✅ Data cleaning utilities
├── main.py                        ✅ 125 lines - FastAPI entry
└── requirements.txt               ✅ Dependencies
```

## ⚛️ Frontend Structure (Clean Baseline)
```
frontend/src/
├── App.js                         ✅ 74 lines - Main React app
├── index.css                      ✅ Global styles
├── index.js                       ✅ React entry point
├── components/
│   ├── bank/
│   │   ├── BankDetectionDisplay.js ✅ Bank detection UI
│   │   └── ColumnMapping.js       ✅ Column mapping
│   ├── config/
│   │   ├── ConfigurationSelection.js ✅ Config selection
│   │   └── ParseConfiguration.js  ✅ Parse configuration
│   ├── modern/
│   │   ├── AppHeader.js           ✅ Modern header
│   │   ├── ContentArea.js         ✅ Content area
│   │   ├── MainLayout.js          ✅ Layout component
│   │   ├── ModernAppLogic.js      🚨 313 lines - needs split
│   │   ├── ModernDataReviewStep.js 🚨 651 lines - CRITICAL!
│   │   ├── ModernFileConfigurationStep.js 🚨 521 lines - CRITICAL!
│   │   ├── ModernFileUploadStep.js 🚨 318 lines - needs split
│   │   ├── ModernMultiCSVApp.js   ✅ Multi-CSV app
│   │   ├── ModernTransformAndExportStep.js ✅ Transform step
│   │   ├── StepNavigation.js      ✅ 195 lines - compliant
│   │   ├── archive/               📁 Archived components
│   │   ├── configure-review/
│   │   │   ├── AdvancedConfigPanel.js ✅ Config panel
│   │   │   ├── AutoParseHandler.js ✅ Auto-parse handling
│   │   │   ├── ConfidenceDashboard.js ✅ 197 lines - compliant
│   │   │   ├── TransactionReview.js 🚨 322 lines - needs split
│   │   │   └── ValidationChecklist.js ✅ Validation UI
│   │   └── transform-export/
│   │       ├── ExportOptions.js   ✅ Export options
│   │       ├── InteractiveDataTable.js 🚨 399 lines - needs split
│   │       ├── TransferAnalysisPanel.js ✅ Transfer analysis
│   │       ├── TransformationProgress.js ✅ Progress UI
│   │       └── TransformationResults.js ✅ Results display
│   ├── multi/
│   │   └── [Multiple components]   ✅ Multi-CSV components
│   └── ui/
│       └── [UI components]        ✅ Reusable UI components
├── handlers/
│   └── [Handler functions]        ✅ Event handlers
├── hooks/
│   └── [Custom hooks]             ✅ React hooks
├── services/
│   └── configurationService.js    ✅ Configuration service
├── theme/
│   └── ThemeProvider.js           ✅ 193 lines - compliant
└── utils/
    └── [Utility functions]        ✅ Helper utilities
```

## 🚨 CRITICAL CONSTRAINT VIOLATIONS SUMMARY

### **📊 Violation Statistics:**
- **Total Files Over 200 Lines:** 25+ files
- **Backend Violations:** 17 files (worst: 688 lines)
- **Frontend Violations:** 8 files (worst: 883 lines)
- **Critical Files (>500 lines):** 3 files
- **Total Excess Lines:** ~3,000+ lines need refactoring

### **🎯 Priority Split Targets:**
1. **transformation_service.py** (688 lines) - Split into 4+ files
2. **cross_bank_matcher.py** (533 lines) - Split into 3+ files  
3. **ModernizedPrototype.js** (883 lines) - Split into 5+ files
4. **ModernDataReviewStep.js** (651 lines) - Split into 4+ files
5. **ModernFileConfigurationStep.js** (521 lines) - Split into 3+ files

### **⚠️ Development Impact:**
- **Backend modifications** require careful constraint awareness
- **Frontend development** needs immediate splitting for complex components
- **Any file >150 lines** should be monitored for growth
- **New features** must follow single-responsibility principle

## 🔗 Known Import Dependencies

| File | Key Dependencies | Status |
|------|------------------|--------|
| `backend/main.py` | FastAPI, all routers | ✅ Working |
| `backend/services/multi_csv_service.py` | All parsers, cleaners, detectors | 🚨 Complex |
| `backend/services/transformation_service.py` | CashewTransformer, detectors | 🚨 Massive |
| `frontend/src/App.js` | Basic React components | ✅ Simple |

## 🚀 API Endpoints (Clean State)

| Endpoint | Method | Status | Handler |
|----------|--------|--------|---------|
| `/` | GET | ✅ Working | Root welcome |
| `/upload` | POST | ✅ Working | File upload |
| `/preview/{file_id}` | GET | ✅ Working | File preview |
| `/parse-range/{file_id}` | POST | ✅ Working | Range parsing |
| `/multi-csv/parse` | POST | ✅ Working | Multi-CSV parse |
| `/multi-csv/transform` | POST | ✅ Working | Transform data |
| `/configs` | GET | ✅ Working | List configs |

## 📝 Development Strategy

### **✅ SAFE MODIFICATION ZONES:**
- backend/main.py (125 lines)
- frontend/src/App.js (74 lines)  
- Most data_cleaning/ components
- API endpoint files <200 lines

### **🚨 DANGER ZONES - AVOID UNTIL SPLIT:**
- transformation_service.py (688 lines)
- cross_bank_matcher.py (533 lines)
- All frontend modern/ large components
- multi_csv_service.py (382 lines)

### **🎯 NEXT SESSION PRIORITIES:**
1. **Test clean baseline** - Verify basic functionality works
2. **Choose first target** - Select safest enhancement point
3. **Plan splitting strategy** - How to break down large files
4. **Implement gradually** - One small change at a time

## 📅 Last Updated
**Date:** 2025-06-21  
**Session:** 🧹 Strategic Rollback & Documentation Update  
**Status:** ✅ Clean baseline documented, ready for constraint-aware development

**🎯 GOAL:** Accurate inventory of current state to guide safe, incremental improvements while respecting the 200-line constraint.
