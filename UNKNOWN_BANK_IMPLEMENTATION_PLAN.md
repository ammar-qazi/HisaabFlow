# Unknown Bank Support Implementation Plan

**Version:** 1.0  
**Date:** 2025-07-13  
**Project:** HisaabFlow - Bank Statement Parser

## 🎯 **Overview**

This plan outlines the implementation of comprehensive unknown bank support for HisaabFlow, enabling users to configure new banks through a single-panel interface with automatic format detection and guided configuration.

## 📋 **Requirements Summary**

### **Core Features**
- **Multiple Amount Formats**: Support American (1,234.56), European (1.234,56), space-separated (1 234,56), and other regional formats
- **Automatic Config Generation**: Auto-detect CSV structure, amount formats, and suggest header mappings
- **Single-Panel UI**: Comprehensive configuration interface (not step-by-step wizard)
- **Enhanced Field Support**: Date, Amount, Title, Note, Currency, Exchange To, Exchange To Currency
- **Smart Defaults**: Default categorization rules in app.conf for common merchants

### **Technical Specifications**
- **Confidence Threshold**: 50% (triggers unknown bank workflow)
- **Multi-Currency**: Already supported via account mapping (Revolut example)
- **Field Mapping**: 7 standard fields (Date, Amount, Title, Note, Currency, Exchange To, Exchange To Currency)
- **Default Categories**: Common merchants (Walmart, Costco, Amazon, Uber, etc.) in app.conf

## 🏗️ **Implementation Phases**

### **Phase 1: Enhanced Amount Format Detection (Weeks 1-2)**

#### **1.1 Create Amount Format Infrastructure**

**New Files:**
```
backend/infrastructure/amount_formats/
├── __init__.py
├── amount_format_detector.py      # Auto-detection logic
├── format_registry.py            # Supported format definitions  
├── format_validators.py          # Validation and confidence scoring
└── regional_formats.py           # Regional format specifications
```

**Core Classes:**
```python
@dataclass
class AmountFormat:
    decimal_separator: str          # "." or ","
    thousand_separator: str         # ",", ".", " ", "'" or ""
    negative_style: str            # "minus", "parentheses", "suffix"
    currency_position: str         # "prefix", "suffix", "none"
    grouping_pattern: List[int]    # [3] for standard, [3,2] for Indian

class AmountFormatDetector:
    def detect_format(self, amount_samples: List[str]) -> Tuple[AmountFormat, float]
    def analyze_amount_column(self, data: List[Dict]) -> AmountFormatAnalysis
    def get_format_confidence(self, samples: List[str], format_type: AmountFormat) -> float

class RegionalFormatRegistry:
    AMERICAN = AmountFormat(decimal=".", thousand=",", negative_style="minus")
    EUROPEAN = AmountFormat(decimal=",", thousand=".", negative_style="minus")
    SPACE_SEPARATED = AmountFormat(decimal=",", thousand=" ", negative_style="minus")
    INDIAN = AmountFormat(decimal=".", thousand=",", grouping_pattern=[3,2])
    SWISS = AmountFormat(decimal=".", thousand="'", negative_style="minus")
    NO_SEPARATOR = AmountFormat(decimal=".", thousand="", negative_style="minus")
```

#### **1.2 Enhance NumericCleaner**

**Modifications to `backend/infrastructure/csv_cleaning/numeric_cleaner.py`:**
```python
class NumericCleaner:
    def __init__(self, amount_format: Optional[AmountFormat] = None):
        self.amount_format = amount_format or RegionalFormatRegistry.AMERICAN
        self.format_detector = AmountFormatDetector()
    
    def auto_detect_and_clean(self, data: List[Dict]) -> Tuple[List[Dict], AmountFormat]:
        # Auto-detect format from amount columns
        detected_format, confidence = self.format_detector.detect_format(amount_samples)
        self.amount_format = detected_format
        return self.clean_numeric_columns(data), detected_format
    
    def parse_numeric_value_with_format(self, value: Any, format: AmountFormat) -> float:
        # Format-aware parsing logic
        pass
```

#### **1.3 Update DataCleaningConfig**

**Enhance `backend/infrastructure/config/unified_config_service.py`:**
```python
@dataclass  
class DataCleaningConfig:
    # ... existing fields ...
    
    # Enhanced amount format fields
    amount_format: AmountFormat = field(default_factory=lambda: RegionalFormatRegistry.AMERICAN)
    auto_detect_format: bool = True
    amount_format_confidence: float = 0.0
```

### **Phase 2: Enhanced CSV Structure Analysis (Weeks 2-3)**

#### **2.1 Extend StructureAnalyzer**

**Modifications to `backend/infrastructure/csv_parsing/structure_analyzer.py`:**
```python
class StructureAnalyzer:
    def analyze_unknown_csv(self, csv_data: str, filename: str) -> UnknownCSVAnalysis:
        """Comprehensive analysis for unknown bank CSV files"""
        return UnknownCSVAnalysis(
            encoding=self.detect_encoding(csv_data),
            delimiter=self.detect_delimiter(csv_data),
            headers=self.extract_headers(csv_data),
            header_row=self.detect_header_row(csv_data),
            data_start_row=self.detect_data_start_row(csv_data),
            amount_format=self.detect_amount_format(csv_data),
            suggested_mappings=self.suggest_column_mappings(headers),
            filename_patterns=self.generate_filename_patterns(filename),
            sample_data=self.extract_sample_data(csv_data)
        )
    
    def suggest_column_mappings(self, headers: List[str]) -> Dict[str, List[str]]:
        """Suggest mappings for standard fields based on header analysis"""
        mapping_suggestions = {
            'date': self._find_date_columns(headers),
            'amount': self._find_amount_columns(headers),
            'title': self._find_description_columns(headers),
            'note': self._find_note_columns(headers),
            'currency': self._find_currency_columns(headers),
            'exchange_to': self._find_exchange_columns(headers),
            'exchange_to_currency': self._find_exchange_currency_columns(headers)
        }
        return mapping_suggestions
```

#### **2.2 Create Configuration Generation Service**

**New File: `backend/services/config_generation_service.py`:**
```python
class ConfigGenerationService:
    def __init__(self):
        self.structure_analyzer = StructureAnalyzer()
        self.format_detector = AmountFormatDetector()
        
    def analyze_unknown_bank_csv(self, csv_data: str, filename: str) -> UnknownBankAnalysis:
        """Complete analysis of unknown bank CSV"""
        pass
        
    def generate_bank_config(self, analysis: UnknownBankAnalysis, user_input: BankConfigInput) -> Dict[str, Any]:
        """Generate complete bank configuration"""
        pass
        
    def validate_generated_config(self, config: Dict[str, Any], sample_data: List[Dict]) -> ValidationResult:
        """Validate generated configuration against sample data"""
        pass
```

### **Phase 3: Configuration Creation API (Weeks 3)**

#### **3.1 New API Endpoints**

**New File: `backend/api/unknown_bank_endpoints.py`:**
```python
from fastapi import APIRouter, UploadFile
from ..services.config_generation_service import ConfigGenerationService

unknown_bank_router = APIRouter(prefix="/unknown-bank", tags=["unknown-bank"])

@unknown_bank_router.post("/analyze-csv")
async def analyze_unknown_csv(file: UploadFile) -> UnknownBankAnalysisResponse:
    """Analyze uploaded CSV for unknown bank configuration"""
    pass

@unknown_bank_router.post("/generate-config")  
async def generate_bank_config(request: GenerateBankConfigRequest) -> GenerateBankConfigResponse:
    """Generate bank configuration from user input"""
    pass

@unknown_bank_router.post("/validate-config")
async def validate_bank_config(request: ValidateBankConfigRequest) -> ValidationResponse:
    """Validate generated configuration with sample data"""
    pass

@unknown_bank_router.post("/save-config")
async def save_bank_config(request: SaveBankConfigRequest) -> SaveConfigResponse:
    """Save bank configuration and reload configs"""
    pass
```

#### **3.2 API Models**

**Add to `backend/api/models.py`:**
```python
class UnknownBankAnalysisResponse(BaseModel):
    filename: str
    encoding: str
    delimiter: str
    headers: List[str]
    header_row: int
    data_start_row: int
    detected_amount_format: AmountFormat
    format_confidence: float
    suggested_mappings: Dict[str, List[str]]
    filename_patterns: List[str]
    sample_data: List[Dict[str, Any]]

class GenerateBankConfigRequest(BaseModel):
    bank_name: str
    display_name: str
    filename_patterns: List[str]
    column_mappings: Dict[str, str]  # standard_field -> csv_column
    amount_format: AmountFormat
    currency_primary: str
    cashew_account: str

class BankConfigInput(BaseModel):
    bank_name: str
    display_name: str
    column_mappings: Dict[str, str]
    amount_format: AmountFormat
    # ... other fields
```

#### **3.3 Enhanced UnifiedConfigService**

**Add methods to `backend/infrastructure/config/unified_config_service.py`:**
```python
class UnifiedConfigService:
    # ... existing methods ...
    
    def reload_all_configs(self) -> bool:
        """Hot-reload all bank configurations"""
        try:
            self._bank_configs.clear()
            self._detection_patterns.clear()
            self._load_all_bank_configs()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to reload configs: {e}")
            return False
    
    def create_bank_config_from_analysis(self, analysis: UnknownBankAnalysis, user_input: BankConfigInput) -> bool:
        """Create new bank config file from analysis and user input"""
        pass
```

### **Phase 4: Frontend Unknown Bank Panel (Weeks 4-5)**

#### **4.1 Enhanced Bank Detection Logic**

**Modify `frontend/src/utils/bankDetection.js`:**
```javascript
export const CONFIDENCE_THRESHOLD = 0.5; // 50% threshold

export const shouldTriggerUnknownBankWorkflow = (uploadedFiles) => {
  return uploadedFiles.some(file => 
    !file.detectedBank || (file.confidence || 0) < CONFIDENCE_THRESHOLD
  );
};

export const getUnknownBankFiles = (uploadedFiles) => {
  return uploadedFiles.filter(file => 
    !file.detectedBank || (file.confidence || 0) < CONFIDENCE_THRESHOLD
  );
};
```

#### **4.2 Unknown Bank Configuration Panel**

**New File: `frontend/src/components/configure-review/UnknownBankPanel.js`:**
```jsx
import React, { useState, useEffect } from 'react';
import { Card, Button, Select, Input, Badge, Alert } from '../ui';
import { Settings, FileText, AlertTriangle, CheckCircle } from '../ui/Icons';

const STANDARD_FIELDS = [
  { value: 'date', label: 'Date', required: true },
  { value: 'amount', label: 'Amount', required: true },
  { value: 'title', label: 'Title/Description', required: true },
  { value: 'note', label: 'Note/Type', required: false },
  { value: 'currency', label: 'Currency', required: false },
  { value: 'exchange_to', label: 'Exchange To Amount', required: false },
  { value: 'exchange_to_currency', label: 'Exchange To Currency', required: false },
];

const AMOUNT_FORMATS = [
  { value: 'american', label: 'American (1,234.56)', example: '1,234.56' },
  { value: 'european', label: 'European (1.234,56)', example: '1.234,56' },
  { value: 'space_separated', label: 'Space Separated (1 234,56)', example: '1 234,56' },
  { value: 'indian', label: 'Indian (1,23,456.78)', example: '1,23,456.78' },
  { value: 'no_separator', label: 'No Separator (1234.56)', example: '1234.56' },
];

function UnknownBankPanel({ unknownFiles, onConfigCreated, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [bankConfig, setBankConfig] = useState({
    bankName: '',
    displayName: '',
    filenamePatterns: [],
    columnMappings: {},
    amountFormat: 'american',
    currencyPrimary: 'USD',
    cashewAccount: ''
  });
  const [validationResult, setValidationResult] = useState(null);

  // Auto-select first unknown file
  useEffect(() => {
    if (unknownFiles.length > 0 && !selectedFile) {
      setSelectedFile(unknownFiles[0]);
    }
  }, [unknownFiles, selectedFile]);

  // Analyze selected file
  useEffect(() => {
    if (selectedFile) {
      analyzeUnknownCSV(selectedFile);
    }
  }, [selectedFile]);

  const analyzeUnknownCSV = async (file) => {
    try {
      const response = await fetch('/api/v1/unknown-bank/analyze-csv', {
        method: 'POST',
        body: createFormData(file)
      });
      const result = await response.json();
      setAnalysis(result);
      
      // Auto-populate bank config with detected values
      setBankConfig(prev => ({
        ...prev,
        bankName: generateBankName(file.fileName),
        displayName: generateDisplayName(file.fileName),
        filenamePatterns: result.filename_patterns,
        amountFormat: mapDetectedFormat(result.detected_amount_format),
        currencyPrimary: detectCurrency(result.sample_data)
      }));
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  return (
    <Card padding="lg" elevated>
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <AlertTriangle size={20} className="text-orange-500" />
        <h3 className="text-lg font-semibold">Unknown Bank Configuration</h3>
        <Badge variant="warning">
          {unknownFiles.length} file{unknownFiles.length !== 1 ? 's' : ''} need setup
        </Badge>
      </div>

      {/* File Selection */}
      {unknownFiles.length > 1 && (
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">Select File to Configure:</label>
          <Select
            value={selectedFile?.fileName || ''}
            onChange={(e) => setSelectedFile(unknownFiles.find(f => f.fileName === e.target.value))}
          >
            {unknownFiles.map(file => (
              <option key={file.fileName} value={file.fileName}>
                {file.fileName} ({Math.round((file.confidence || 0) * 100)}% confidence)
              </option>
            ))}
          </Select>
        </div>
      )}

      {selectedFile && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Configuration Panel */}
          <div className="space-y-6">
            <BankInfoSection 
              config={bankConfig}
              onChange={setBankConfig}
              analysis={analysis}
            />
            
            <HeaderMappingSection
              config={bankConfig}
              onChange={setBankConfig}
              analysis={analysis}
            />
            
            <AmountFormatSection
              config={bankConfig}
              onChange={setBankConfig}
              analysis={analysis}
            />
            
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => validateConfig(bankConfig, analysis)}
                disabled={loading}
              >
                Validate Config
              </Button>
              <Button
                variant="primary"
                onClick={() => saveConfiguration(bankConfig)}
                disabled={loading || !isConfigValid(bankConfig)}
              >
                Save & Apply
              </Button>
            </div>
          </div>

          {/* Preview Panel */}
          <div className="space-y-6">
            <ConfigPreviewSection
              config={bankConfig}
              analysis={analysis}
              validationResult={validationResult}
            />
            
            <SampleDataPreview
              analysis={analysis}
              mappings={bankConfig.columnMappings}
            />
          </div>
        </div>
      )}
    </Card>
  );
}

// Sub-components for each section...
function BankInfoSection({ config, onChange, analysis }) {
  return (
    <div className="space-y-4">
      <h4 className="font-medium">Bank Information</h4>
      <Input
        label="Bank Name"
        value={config.bankName}
        onChange={(e) => onChange(prev => ({ ...prev, bankName: e.target.value }))}
        placeholder="e.g. mybank"
        required
      />
      <Input
        label="Display Name" 
        value={config.displayName}
        onChange={(e) => onChange(prev => ({ ...prev, displayName: e.target.value }))}
        placeholder="e.g. MyBank"
        required
      />
      <Input
        label="Primary Currency"
        value={config.currencyPrimary}
        onChange={(e) => onChange(prev => ({ ...prev, currencyPrimary: e.target.value }))}
        placeholder="USD"
        required
      />
    </div>
  );
}

function HeaderMappingSection({ config, onChange, analysis }) {
  const availableHeaders = analysis?.headers || [];
  
  return (
    <div className="space-y-4">
      <h4 className="font-medium">Header Mapping</h4>
      {STANDARD_FIELDS.map(field => (
        <div key={field.value}>
          <label className="block text-sm font-medium mb-1">
            {field.label} {field.required && <span className="text-red-500">*</span>}
          </label>
          <Select
            value={config.columnMappings[field.value] || ''}
            onChange={(e) => onChange(prev => ({
              ...prev,
              columnMappings: { ...prev.columnMappings, [field.value]: e.target.value }
            }))}
          >
            <option value="">Select column...</option>
            {availableHeaders.map(header => (
              <option key={header} value={header}>{header}</option>
            ))}
          </Select>
          {analysis?.suggested_mappings[field.value] && (
            <div className="text-xs text-gray-500 mt-1">
              Suggested: {analysis.suggested_mappings[field.value].join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function AmountFormatSection({ config, onChange, analysis }) {
  const detectedFormat = analysis?.detected_amount_format;
  const confidence = analysis?.format_confidence || 0;
  
  return (
    <div className="space-y-4">
      <h4 className="font-medium">Amount Format</h4>
      
      {detectedFormat && (
        <Alert variant="info" className="mb-3">
          Auto-detected: {getFormatLabel(detectedFormat)} 
          ({Math.round(confidence * 100)}% confidence)
        </Alert>
      )}
      
      <Select
        value={config.amountFormat}
        onChange={(e) => onChange(prev => ({ ...prev, amountFormat: e.target.value }))}
        label="Number Format"
      >
        {AMOUNT_FORMATS.map(format => (
          <option key={format.value} value={format.value}>
            {format.label}
          </option>
        ))}
      </Select>
      
      <div className="text-sm text-gray-600">
        Example: {AMOUNT_FORMATS.find(f => f.value === config.amountFormat)?.example}
      </div>
    </div>
  );
}

export default UnknownBankPanel;
```

#### **4.3 Integration with Main App**

**Modify `frontend/src/components/steps/ConfigureAndReviewStep.js`:**
```jsx
import UnknownBankPanel from '../configure-review/UnknownBankPanel';
import { shouldTriggerUnknownBankWorkflow, getUnknownBankFiles } from '../../utils/bankDetection';

function ConfigureAndReviewStep({ uploadedFiles, ... }) {
  const unknownFiles = getUnknownBankFiles(uploadedFiles);
  const hasUnknownFiles = shouldTriggerUnknownBankWorkflow(uploadedFiles);

  return (
    <div>
      {hasUnknownFiles && (
        <UnknownBankPanel 
          unknownFiles={unknownFiles}
          onConfigCreated={handleConfigCreated}
          loading={loading}
        />
      )}
      
      {/* Existing configuration panels */}
      <AdvancedConfigPanel ... />
      {/* ... other components */}
    </div>
  );
}
```

### **Phase 5: Enhanced Default Categorization (Week 5)**

#### **5.1 Update app.conf**

**Modify `configs/app.conf`:**
```ini
[general]
date_tolerance_hours = 72
user_name = Your Name Here

[transfer_detection]
confidence_threshold = 0.7

[transfer_categorization]  
default_pair_category = Balance Correction

# New: Default categorization for unknown banks
[default_categorization]
# Grocery & Retail
walmart = Grocery
costco = Grocery  
lidl = Grocery
aldi = Grocery
target = Shopping
amazon = Shopping
ebay = Shopping

# Technology
apple = Electronics
microsoft = Software
google = Software
netflix = Entertainment
spotify = Entertainment

# Transportation
uber = Transportation
lyft = Transportation
bolt = Transportation
grab = Transportation

# Food & Dining
mcdonalds = Dining
kfc = Dining
starbucks = Dining
subway = Dining

# Gas & Fuel
shell = Transportation
exxon = Transportation
bp = Transportation

# Finance & Services
paypal = Financial Services
stripe = Financial Services
```

#### **5.2 Enhance Configuration Loading**

**Modify `backend/infrastructure/config/unified_config_service.py`:**
```python
class UnifiedConfigService:
    def __init__(self, config_dir: str = None):
        # ... existing code ...
        self._default_categorization: Dict[str, str] = {}
        self._load_app_config()  # This will now load default categorization
        
    def _load_app_config(self) -> None:
        """Load application configuration including default categorization"""
        # ... existing code ...
        
        # Load default categorization rules
        if 'default_categorization' in self._app_config:
            self._default_categorization = dict(self._app_config['default_categorization'])
            print(f"[BUILD] Loaded {len(self._default_categorization)} default categorization rules")
    
    def get_default_categorization_rules(self) -> Dict[str, str]:
        """Get default categorization rules for unknown banks"""
        return self._default_categorization.copy()
    
    def categorize_merchant_with_defaults(self, bank_name: str, merchant: str) -> Optional[str]:
        """Categorize merchant using bank-specific rules with default fallback"""
        # Try bank-specific rules first
        category = self.categorize_merchant(bank_name, merchant)
        if category:
            return category
            
        # Fallback to default rules
        merchant_lower = merchant.lower()
        for pattern, category in self._default_categorization.items():
            if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', merchant_lower):
                return category
                
        return None
```

### **Phase 6: Integration & Testing (Week 6)**

#### **6.1 End-to-End Testing**
- Test complete workflow: unknown file → analysis → configuration → save → reload
- Validate amount format detection with various regional samples
- Test header mapping suggestions and validation
- Verify default categorization fallback

#### **6.2 Performance Testing**  
- Large CSV file handling (10k+ transactions)
- Format detection performance with extensive sample analysis
- Config reload impact on system performance

#### **6.3 Edge Case Handling**
- Mixed amount formats within same file
- Corrupted or incomplete CSV data
- Invalid user input validation
- Network error handling during config save

## 📁 **File Structure Changes**

### **New Files**
```
backend/
├── infrastructure/amount_formats/          # New amount format system
│   ├── __init__.py
│   ├── amount_format_detector.py
│   ├── format_registry.py
│   ├── format_validators.py
│   └── regional_formats.py
├── services/
│   └── config_generation_service.py        # New config generation service
├── api/
│   └── unknown_bank_endpoints.py           # New API endpoints

frontend/src/components/configure-review/
└── UnknownBankPanel.js                     # New comprehensive UI panel
```

### **Modified Files**
```
configs/app.conf                            # Add default categorization
backend/infrastructure/csv_cleaning/numeric_cleaner.py    # Format-aware cleaning
backend/infrastructure/config/unified_config_service.py   # Enhanced config service
backend/infrastructure/csv_parsing/structure_analyzer.py  # Enhanced analysis
backend/api/models.py                       # New API models
frontend/src/utils/bankDetection.js         # Enhanced detection logic
frontend/src/components/steps/ConfigureAndReviewStep.js   # Integration
```

## 🚀 **Success Metrics**

### **Phase 1 Success Criteria**
- [ ] Multiple amount formats correctly detected and parsed
- [ ] Format detection confidence scoring working
- [ ] Enhanced NumericCleaner handling all regional formats

### **Phase 2 Success Criteria**  
- [ ] Complete CSV structure analysis for unknown files
- [ ] Smart header mapping suggestions with 80%+ accuracy
- [ ] Filename pattern generation working

### **Phase 3 Success Criteria**
- [ ] All API endpoints functional and tested
- [ ] Config generation and validation working
- [ ] Hot-reload capability implemented

### **Phase 4 Success Criteria**
- [ ] Single-panel UI complete and intuitive
- [ ] Real-time validation and preview working
- [ ] Seamless integration with existing workflow

### **Phase 5 Success Criteria**
- [ ] Default categorization rules loaded and applied
- [ ] Fallback categorization working for unknown banks
- [ ] Common merchants automatically categorized

### **Phase 6 Success Criteria**
- [ ] End-to-end workflow tested and functional
- [ ] Performance acceptable for large files
- [ ] Edge cases handled gracefully

## 📝 **Technical Notes**

### **Amount Format Detection Algorithm**
1. **Sample Analysis**: Extract amount-like values from multiple columns
2. **Pattern Recognition**: Identify decimal/thousand separators using regex patterns
3. **Statistical Validation**: Verify format consistency across samples
4. **Confidence Scoring**: Rate detection confidence based on sample size and consistency

### **Header Mapping Intelligence**
- **Keyword Matching**: Match headers against known patterns (date, amount, description keywords)
- **Position Analysis**: Consider column position for common bank formats
- **Content Analysis**: Analyze sample data to infer column types
- **User Feedback**: Learn from user corrections for future suggestions

### **Configuration Validation**
- **Required Fields**: Ensure Date and Amount mappings are provided
- **Format Consistency**: Validate amount format against sample data
- **Duplicate Detection**: Check for conflicting bank names or patterns
- **Sample Processing**: Test configuration against sample data before saving

## 🔧 **Development Guidelines**

### **Code Style**
- Follow existing HisaabFlow patterns and architecture
- Maintain clean separation between detection, analysis, and configuration
- Use comprehensive error handling and logging
- Add inline debugging statements (console.log, print) as per project standards

### **Testing Strategy**
- **Unit Tests**: Test individual format detection and validation functions
- **Integration Tests**: Test complete unknown bank workflow
- **Regression Tests**: Ensure existing bank configurations still work
- **Performance Tests**: Validate handling of large CSV files

### **Documentation**
- Update API documentation for new endpoints
- Add inline code documentation for complex algorithms
- Update user documentation with unknown bank workflow
- Create troubleshooting guide for common configuration issues

---

**This implementation plan provides a comprehensive solution for unknown bank support while maintaining HisaabFlow's excellent architecture and extensibility.**