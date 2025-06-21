# HisaabFlow Data Standards

## 🎯 Purpose
This document defines consistent data formats across the HisaabFlow application to prevent data structure mismatches and ensure reliable component integration.

## 📊 Core Data Types

### **CSV Row Data**
```typescript
// ✅ ALWAYS: Dictionary format (from DataProcessor)
interface CSVRow {
  [columnName: string]: string;
}

// Example:
{
  "Date": "2025-06-10",
  "Amount": "-18,063",
  "Description": "Payment to merchant",
  "Balance": "45,230.50"
}

// ❌ NEVER: Array format
// ["2025-06-10", "-18,063", "Payment to merchant", "45,230.50"]
```

### **Bank Detection Result**
```typescript
interface BankDetectionResult {
  detected_bank: string;        // Bank identifier (e.g., "nayapay", "wise_usd")
  confidence: number;           // 0.0 to 1.0 (0% to 100%)
  reasons: string[];           // ["filename_match(1.0)", "header_match(0.8)"]
}

// Example:
{
  "detected_bank": "nayapay",
  "confidence": 0.6,
  "reasons": ["filename_match(1.0)", "header_match(1.0)"]
}
```

### **Parse Result**
```typescript
interface ParseResult {
  success: boolean;
  headers: string[];           // Column names
  data: CSVRow[];             // ALWAYS dictionaries
  row_count: number;
  cleaning_applied: boolean;
  bank_info: BankDetectionResult;
}
```

### **Configuration Object**
```typescript
interface BankConfiguration {
  bank_name: string;
  column_mapping: { [standardField: string]: string };
  currency?: string;
  account_type?: string;
  // ... other config fields
}

// Example:
{
  "bank_name": "nayapay",
  "column_mapping": {
    "date": "TIMESTAMP",
    "amount": "AMOUNT", 
    "description": "DESCRIPTION"
  },
  "currency": "PKR"
}
```

## 🔄 API Response Formats

### **Standard API Response**
```typescript
interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
```

### **Multi-CSV Parse Response**
```typescript
interface MultiCSVParseResponse {
  success: boolean;
  parsed_csvs: Array<{
    file_id: string;
    parse_result: ParseResult;
  }>;
  total_files: number;
  message: string;
}
```

### **Transform Response**
```typescript
interface TransformResponse {
  success: boolean;
  transformed_data: Array<{
    filename: string;
    bank: string;
    transactions: TransformedTransaction[];
    summary: {
      total_transactions: number;
      total_amount: number;
    };
  }>;
  transfer_analysis: {
    detected_transfers: any[];
    potential_matches: any[];
    total_transfers: number;
  };
}

interface TransformedTransaction {
  date: string;
  description: string;
  amount: string;
  balance: string;
  category: string;
  bank: string;
  account: string;
  currency: string;
  original_data?: CSVRow;  // For debugging
}
```

## 🏗️ Data Flow Standards

### **Frontend ↔ Backend Contract**
1. **Parsing Phase**: Backend returns `ParseResult` with `data: CSVRow[]`
2. **Transform Phase**: Frontend sends `CSVRow[]`, Backend returns `TransformedTransaction[]`
3. **Configuration**: Both use `BankConfiguration` format
4. **Error Handling**: Always return structured error with context

### **State Management (Frontend)**
```typescript
// Uploaded file state structure
interface UploadedFile {
  fileId: string;
  fileName: string;
  originalName: string;
  size: number;
  parseConfig: any;
  parsedData?: {
    success: boolean;
    headers: string[];
    data: CSVRow[];           // ALWAYS dictionaries
    bank_info: BankDetectionResult;
  };
  selectedConfiguration?: string;
  columnMapping?: { [key: string]: string };
}
```

## 🚨 Data Validation Rules

### **Before Any Data Transformation**
```python
# Python validation example
def validate_csv_data(data: List[Any]) -> List[Dict[str, str]]:
    """Validate and convert data to standard CSV row format"""
    validated_rows = []
    
    for i, row in enumerate(data):
        if isinstance(row, dict):
            # Already in correct format
            validated_rows.append(row)
        elif isinstance(row, list):
            # Convert array to dict (legacy support)
            raise ValueError(f"Row {i}: Array format no longer supported. Use dictionary format.")
        else:
            raise ValueError(f"Row {i}: Invalid data type {type(row)}. Expected dictionary.")
    
    return validated_rows
```

```javascript
// JavaScript validation example
function validateCSVData(data) {
  return data.map((row, index) => {
    if (typeof row === 'object' && !Array.isArray(row) && row !== null) {
      return row; // Correct dictionary format
    }
    if (Array.isArray(row)) {
      throw new Error(`Row ${index}: Array format no longer supported. Use dictionary format.`);
    }
    throw new Error(`Row ${index}: Invalid data type. Expected dictionary.`);
  });
}
```

### **Type Safety Checks**
```python
# Add to all transform functions
def transform_data(data: List[Dict[str, str]]) -> List[TransformedTransaction]:
    # Validate input format
    if not isinstance(data, list):
        raise TypeError("Data must be a list")
    
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            raise TypeError(f"Row {i} must be a dictionary, got {type(row)}")
    
    # Process data...
```

## 🔧 Migration Guidelines

### **Updating Existing Code**
1. **Check data access patterns**: Replace `row[0]` with `row.get("Date", "")`
2. **Add type validation**: Use isinstance() checks before processing
3. **Update error handling**: Provide specific error messages for data format issues
4. **Test with real data**: Ensure compatibility with actual CSV parser output

### **Adding New Endpoints**
1. **Define data contracts**: Document expected input/output formats
2. **Add validation**: Use Pydantic models or TypeScript interfaces
3. **Include examples**: Show sample request/response data
4. **Handle edge cases**: Empty data, missing fields, type mismatches

## 📖 Field Naming Conventions

### **Standard Field Names**
- **Date Fields**: `Date`, `TIMESTAMP`, `Booking Date`, `Transaction Date Time`
- **Amount Fields**: `Amount`, `AMOUNT` 
- **Description Fields**: `Description`, `DESCRIPTION`, `Partner Name`
- **Balance Fields**: `Balance`, `BALANCE`, `Running Balance`
- **Currency Fields**: `Currency`, `CURRENCY`

### **Backend (Python)**
- Use `snake_case` for all variables and function names
- Use `UPPER_SNAKE_CASE` for constants
- Use `PascalCase` for class names

### **Frontend (JavaScript)**
- Use `camelCase` for variables and function names
- Use `PascalCase` for component names
- Use `UPPER_SNAKE_CASE` for constants

## 🎯 Error Prevention Checklist

### **Before Modifying Data Logic**
- [ ] Identify upstream data format (dict/array/other)
- [ ] Check downstream expectations  
- [ ] Add type validation
- [ ] Test with sample data
- [ ] Handle edge cases (empty, null, invalid)
- [ ] Add error logging with context

### **Code Review Checklist**
- [ ] No bare array access (`row[0]`) without type check
- [ ] All data access uses `.get()` or null checks
- [ ] Type validation at function entry points
- [ ] Error messages include data context
- [ ] Sample data tested in development

## 🔄 Update History

| Date | Change | Author | Reason |
|------|--------|--------|--------|
| 2025-06-21 | Initial creation | AI Assistant | Standardize data formats across application |
| 2025-06-21 | Added validation examples | AI Assistant | Prevent data structure mismatches |

---

**💡 Remember**: When in doubt, prefer dictionaries over arrays for structured data. They're self-documenting and less prone to index errors.
