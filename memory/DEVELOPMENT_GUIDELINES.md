# HisaabFlow Development Guidelines
*Consolidated AI Assistant & Developer Reference*

## 🧠 **AI Assistant Memory Context**

### **Project Identity**
- **Name**: HisaabFlow (Bank Statement Parser & Financial Analysis Tool)
- **Primary Developer**: Ammar (ammmarqz@gmail.com)
- **Repository**: `/home/ammar/claude_projects/HisaabFlow`
- **Current Branch**: `frontend-modernization`

### **Architecture Overview**
```
HisaabFlow/
├── backend/          # FastAPI Python backend (STABLE)
├── frontend/         # Modern React frontend (RECENTLY MODERNIZED)
├── configs/          # Bank configuration files (ACTIVELY USED)
├── memory/           # Consolidated documentation (THIS FOLDER)
└── sample_data/      # Test data for development
```

## 🎯 **Current Working Features**

### ✅ **Fully Implemented & Working**
1. **Multi-Bank CSV Processing**: 7+ bank formats supported
2. **Transfer Detection**: Cross-bank transfer identification with 70%+ confidence
3. **Modern React UI**: 4-step workflow with professional design
4. **Interactive Data Table**: Filter, sort, search, export functionality
5. **Transaction Categorization**: Rule-based with transfer-specific categories
6. **Real-time Processing**: Live feedback during transformation

### 🔧 **Recent Fixes (June 2025)**
- Fixed transfer detection frontend-backend data structure mismatch
- Added interactive data table with full functionality
- Resolved categorization display issues
- Modernized entire frontend architecture

## 💻 **Development Principles**

### **Code Quality Standards**
- **File Size Limit**: Max 200 lines per file
- **Modular Design**: Single responsibility principle
- **Debugging**: Inline debugging over separate test files
- **Error Handling**: Graceful degradation with user feedback

### **Frontend Architecture**
- **Component Structure**: `/src/components/modern/` for new UI
- **Theme System**: Consistent styling via ThemeProvider
- **State Management**: React hooks for local state
- **Build Process**: `npm run build` for production

### **Backend Architecture**
- **API Layer**: FastAPI with structured endpoints
- **Services Layer**: Business logic separation
- **Configuration**: `.conf` files for bank-specific settings
- **Transfer Detection**: Advanced pattern matching system

## 🚀 **Development Workflow**

### **Adding New Features**
1. **Plan**: Update this memory document first
2. **Implement**: Follow modular design principles
3. **Test**: Use inline debugging and sample data
4. **Document**: Update relevant memory files
5. **Commit**: Use descriptive commit messages with emojis

### **Debugging Process**
- Use inline `console.log()` and `print()` statements
- Check browser console for frontend issues
- Monitor backend logs at `/backend.log`
- Test with sample data in `/sample_data/`

### **Configuration Management**
- Bank configs in `/configs/*.conf`
- App settings in `/configs/app.conf`
- Transfer patterns use `{name}` placeholders
- Categorization rules support regex patterns

## 🏦 **Bank Integration**

### **Supported Banks**
- **Wise**: USD, EUR, PKR, HUF variants
- **NayaPay**: PKR transactions
- **Erste**: European banking
- **Extensible**: Easy to add new banks via config files

### **Adding New Banks**
1. Create `/configs/newbank.conf`
2. Define file patterns and detection signatures
3. Set up column mappings
4. Add transfer patterns if applicable
5. Test with sample data

## 🔍 **Transfer Detection System**

### **How It Works**
- **Pattern Matching**: Uses regex with `{name}` placeholders
- **Cross-Bank Detection**: Matches "Sent to X" with "Received from X"
- **Date Tolerance**: 72-hour window for matching
- **Confidence Scoring**: 70%+ threshold for acceptance
- **Currency Conversion**: Supports exchange amount matching

### **Configuration**
```ini
[transfer_patterns]
outgoing_transfer = Sent money to {name}
incoming_transfer = Received money from {name}
```

## 📊 **Data Flow**

### **Processing Pipeline**
1. **Upload**: CSV files uploaded via modern UI
2. **Detection**: Auto-detect bank type and structure
3. **Parsing**: Extract transactions with bank-specific rules
4. **Transformation**: Convert to standardized Cashew format
5. **Analysis**: Run transfer detection and categorization
6. **Export**: Interactive table with filtering and export

### **Data Structures**
- **Raw CSV**: Original bank format
- **Parsed Data**: Standardized fields (Date, Amount, Title, etc.)
- **Transformed Data**: Cashew format with categories
- **Transfer Analysis**: Detected pairs with confidence scores

## 🎨 **UI Component Structure**

### **Modern Components** (`/frontend/src/components/modern/`)
- **ModernMultiCSVApp**: Main application wrapper
- **ModernFileUploadStep**: File selection and upload
- **ModernConfigureAndReviewStep**: Configuration and validation
- **ModernTransformAndExportStep**: Results and export
- **InteractiveDataTable**: Advanced data viewing

### **UI Library** (`/frontend/src/components/ui/`)
- **CoreIcons**: Basic icons (chevrons, buttons, etc.)
- **ExtendedIcons**: Financial and data icons
- **ThemeProvider**: Consistent styling system
- **Button, Card, etc.**: Reusable components

## 🔧 **Common Development Tasks**

### **Running the Application**
```bash
# Backend
cd backend && source venv/bin/activate && python main.py

# Frontend Development
cd frontend && npm start

# Frontend Production Build
cd frontend && npm run build
```

### **Adding New Icon**
1. Add to `/frontend/src/components/ui/ExtendedIcons.js`
2. Export in the default object
3. Import where needed from `../ui/Icons`

### **Modifying Transfer Detection**
1. Edit patterns in `/configs/bankname.conf`
2. Update `transfer_detection/config_manager.py` if needed
3. Test with sample data
4. Check backend logs for debugging

## 📝 **Memory Management**

### **This Directory (`/memory/`)**
- **PROJECT_STATUS_CURRENT.md**: Current state and achievements
- **DEVELOPMENT_GUIDELINES.md**: This file - AI assistant reference
- **Historical files**: Keep for reference but prefer current docs

### **Outdated Locations** (TO BE CLEANED)
- `/ai_assistance/memory/`: Various historical documents
- `/frontend/memory/`: Phase-specific progress docs
- Root level: `MODERNIZATION_PLAN.md`, `PHASE_2_CONTINUATION.md`

## 🎯 **Next Development Priorities**

### **If Issues Arise**
1. Check browser console for frontend errors
2. Review backend logs for API issues
3. Verify configuration files are correct
4. Test with known-good sample data
5. Update this memory document with solutions

### **Potential Enhancements**
- Additional bank format support
- Advanced categorization rules
- Export format options (Excel, JSON)
- Historical transaction analysis
- Multi-currency conversion rates

---
*This document serves as the primary reference for AI assistants and developers working on HisaabFlow. Keep it updated with any significant changes.*