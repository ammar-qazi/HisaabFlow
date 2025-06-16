# File Size Refactoring Plan - June 2025

## 🎯 Target: All Files Under 300 Lines (Preferably 200)

### Current Oversized Files (Lines > 300):

**Frontend (Total: 3 files)**
- `MultiCSVApp.js`: 414 lines (+114 over limit)
- `FileConfigurationStep.js`: 354 lines (+54 over limit)  
- `FileHandlers.js`: 338 lines (+38 over limit)

**Backend (Total: 5 files)**
- `universal_transformer.py`: 511 lines (+211 over limit)
- `parse_endpoints.py`: 453 lines (+153 over limit)
- `transform_endpoints.py`: 408 lines (+108 over limit)
- `enhanced_config_manager.py`: 335 lines (+35 over limit)
- `cross_bank_matcher.py`: 304 lines (+4 over limit)

**Other (Total: 1 file)**
- `launch_gui.py`: 327 lines (+27 over limit)

---

## 🔧 Refactoring Strategy

### Phase 1: Frontend Modularization (Session Priority)

#### 1. **MultiCSVApp.js** (414 → ~200 lines)
**Current Responsibilities:**
- Main app state management
- API configuration loading
- File preview functions
- Auto-configuration logic
- Component composition

**Proposed Split:**
- **`MultiCSVApp.js`** (150-180 lines): Main component, state, composition
- **`hooks/useAutoConfiguration.js`** (80-100 lines): Auto-config logic, bank mappings
- **`hooks/usePreviewHandlers.js`** (80-100 lines): Preview functions
- **`services/configurationService.js`** (60-80 lines): API calls for configurations

#### 2. **FileConfigurationStep.js** (354 → ~200 lines)
**Current Responsibilities:**
- BankDetectionDisplay component
- ConfigurationSelection component  
- ParseConfiguration component
- ColumnMapping component
- Main FileConfigurationStep component

**Proposed Split:**
- **`FileConfigurationStep.js`** (100-120 lines): Main component + ConfigurationSelection
- **`components/BankDetectionDisplay.js`** (80-100 lines): Bank detection UI
- **`components/ColumnMapping.js`** (80-100 lines): Column mapping logic
- **`components/ParseConfiguration.js`** (40-60 lines): Parse config controls

#### 3. **FileHandlers.js** (338 → ~200 lines)  
**Current Responsibilities:**
- File upload handlers
- Configuration handlers
- Auto-configuration logic
- Export functionality

**Proposed Split:**
- **`FileHandlers.js`** (120-150 lines): Core file operations
- **`handlers/configurationHandlers.js`** (80-100 lines): Configuration-specific logic
- **`handlers/autoConfigHandlers.js`** (80-100 lines): Auto-configuration logic
- **`utils/exportUtils.js`** (40-60 lines): Export functionality

### Phase 2: Backend Modularization

#### 4. **universal_transformer.py** (511 → ~200 lines)
**Proposed Split:**
- **`universal_transformer.py`** (150-180 lines): Main transformer class
- **`transformers/base_transformer.py`** (80-100 lines): Base transformation logic
- **`transformers/category_engine.py`** (120-150 lines): Categorization logic  
- **`transformers/currency_handler.py`** (80-100 lines): Currency conversion
- **`utils/transformation_utils.py`** (60-80 lines): Helper functions

#### 5. **parse_endpoints.py** (453 → ~200 lines)
**Proposed Split:**
- **`parse_endpoints.py`** (180-200 lines): Core parsing endpoints
- **`endpoints/file_upload_endpoints.py`** (120-150 lines): Upload/preview endpoints
- **`endpoints/preview_endpoints.py`** (100-120 lines): Preview-specific logic
- **`parsers/csv_parser_service.py`** (80-100 lines): Parsing service layer

#### 6. **transform_endpoints.py** (408 → ~200 lines)
**Proposed Split:**
- **`transform_endpoints.py`** (180-200 lines): Core transformation endpoints
- **`endpoints/analysis_endpoints.py`** (120-150 lines): Transfer analysis endpoints
- **`services/transformation_service.py`** (100-120 lines): Transformation service layer

### Phase 3: Configuration & Utility Files

#### 7. **enhanced_config_manager.py** (335 → ~200 lines)
**Proposed Split:**
- **`config_manager.py`** (150-180 lines): Core configuration management
- **`config/config_loader.py`** (80-100 lines): Configuration loading logic
- **`config/config_validator.py`** (60-80 lines): Configuration validation

#### 8. **cross_bank_matcher.py** (304 → ~200 lines)
**Proposed Split:**
- **`cross_bank_matcher.py`** (150-180 lines): Core matching logic
- **`matchers/amount_matcher.py`** (80-100 lines): Amount-based matching
- **`matchers/date_matcher.py`** (60-80 lines): Date-based matching

---

## 📊 Implementation Order

### **Session 1 (Current)**: Frontend Priority
1. ✅ **MultiCSVApp.js refactoring** (414 → ~200 lines)
2. ✅ **FileConfigurationStep.js modularization** (354 → ~200 lines)
3. ✅ **FileHandlers.js splitting** (338 → ~200 lines)

### **Session 2**: Backend Core
1. **universal_transformer.py** (511 → ~200 lines)
2. **parse_endpoints.py** (453 → ~200 lines)

### **Session 3**: Backend Endpoints
1. **transform_endpoints.py** (408 → ~200 lines)
2. **enhanced_config_manager.py** (335 → ~200 lines)

### **Session 4**: Cleanup
1. **cross_bank_matcher.py** (304 → ~200 lines)
2. **launch_gui.py** (327 → ~200 lines)

---

## 🔍 Design Principles

### **Modular Design**
- **Single Responsibility**: Each file has one clear purpose
- **Small Files**: Target 150-200 lines per file maximum
- **Logical Grouping**: Related functionality stays together

### **Maintainability**
- **Clear Imports**: Easy to understand dependencies
- **Consistent Naming**: Follow established conventions
- **Minimal Interfaces**: Keep function signatures simple

### **Functionality Preservation**
- **Zero Breaking Changes**: All existing functionality must work
- **Auto-Configuration**: Preserve the working auto-config system
- **Testing**: Verify functionality after each refactoring step

---

## ✅ Success Criteria

### **File Size Targets**
- All files under 300 lines (hard requirement)
- Most files under 200 lines (preferred target)
- No single file over 250 lines

### **Architecture Quality**
- Clear separation of concerns
- Logical module boundaries  
- Easy to understand and maintain
- Bank-agnostic design preserved

### **Functionality Requirements**
- Auto-configuration system continues working
- All existing features preserved
- No performance degradation
- Clean, readable code

---

## 🚦 Current Status: Ready to Begin Frontend Refactoring

**Next Action**: Start with MultiCSVApp.js modularization
