# HisaabFlow Data Standards

## 🎯 Purpose
This document defines the **actual data formats** used by our clean, working HisaabFlow baseline to prevent data structure mismatches and ensure reliable component integration.

**⚠️ Based on:** Clean baseline code after strategic rollback (commit 3e6ff14)

## 📊 Core Data Types

### **CSV Row Data (Parser Output)**
```typescript
// ✅ CURRENT FORMAT: Dictionary with string keys (from DataProcessor)
interface CSVRow {
  [columnName: string]: string;
}

// Example from working parser:
{
  "Date": "2025-06-10",
  "Amount": "-18,063",
  "Description": "Payment to merchant", 
  "Balance": "45,230.50"
}

// ❌ NOT USED: Array format
// ["2025-06-10", "-18,063", "Payment to merchant", "45,230.50"]
```

### **Bank Detection Result (BankDetector.detect_bank)**
```typescript
// ✅ CURRENT FORMAT: BankDetectionResult object
class BankDetectionResult {
  bank_name: string;           // Bank identifier (e.g., "nayapay", "wise_usd")
  confidence: number;          // 0.0 to 1.0 (0% to 100%)
  reasons: string[];           // List of detection reasons
}

// Example from working detector:
{
  bank_name: "nayapay",
  confidence: 0.85,
  reasons: ["filename contains 'nayapay'", "header contains 'Amount'"]
}
```

### **Parse Result (UnifiedCSVParser.parse_csv)**
```typescript
interface ParseResult {
  success: boolean;
  headers: string[];           // Column names from CSV
  data: CSVRow[];             // Array of dictionary rows
  row_count: number;
  error?: string;             // If success is false
  parsing_info?: object;      // Additional parsing details
}

// Example from working parser:
{
  success: true,
  headers: ["Date", "Amount", "Description", "Balance"],
  data: [
    {"Date": "2025-06-10", "Amount": "-18,063", "Description": "Payment", "Balance": "45,230.50"},
    {"Date": "2025-06-09", "Amount": "1,000", "Description": "Deposit", "Balance": "63,293.50"}
  ],
  row_count: 2
}
```

### **Bank Info Structure (MultiCSVService output)**
```typescript
interface BankInfo {
  detected_bank: string;                    // Bank name from detector
  confidence: number;                       // Detection confidence
  reasons: string[];                        // Detection reasons
  original_headers: string[];               // Headers from parser
  preprocessing_applied?: boolean;          // Whether preprocessing was used
  preprocessing_info?: object;              // Preprocessing details
}

// Example from working service:
{
  detected_bank: "erste_bank",
  confidence: 0.92,
  reasons: ["content signature match", "header pattern match"],
  original_headers: ["Date", "Amount", "Description"],
  preprocessing_applied: false
}
```

### **Multi-CSV Service Response**
```typescript
interface MultiCSVResponse {
  success: boolean;
  results: CSVFileResult[];
  error?: string;
}

interface CSVFileResult {
  filename: string;
  success: boolean;
  bank_info: BankInfo;
  parse_result: ParseResult;
  cleaned_data?: CSVRow[];                  // If cleaning applied
  error?: string;
}
```

### **Transformation Service Input/Output**
```typescript
// ✅ INPUT: Array of CSV data objects
interface TransformationInput {
  csv_data_list: CSVFileResult[];
  user_name?: string;
  enable_transfer_detection?: boolean;
}

// ✅ OUTPUT: Standardized Cashew format
interface TransformationOutput {
  success: boolean;
  data: CashewTransaction[];                // Standardized format
  transfer_analysis?: TransferAnalysis;
  error?: string;
}

interface CashewTransaction {
  Date: string;                             // YYYY-MM-DD format
  Amount: number;                           // Numeric value
  Title: string;                            // Description
  Account: string;                          // Bank account name
  Currency: string;                         // Currency code
  Category?: string;                        // Transaction category
}
```

## 🔄 Data Flow Patterns

### **1. File Upload → Parse Flow**
```
File Upload 
  ↓ (filename, file_path)
MultiCSVService.process_files() 
  ↓ (raw CSV data)
UnifiedCSVParser.parse_csv()
  ↓ (ParseResult with CSVRow[])
BankDetector.detect_bank_from_data()
  ↓ (BankDetectionResult + ParseResult)
Return: CSVFileResult[]
```

### **2. Parse Results → Transform Flow**
```
CSVFileResult[] 
  ↓ (with bank_info + parse_result.data)
TransformationService.transform_multi_csv()
  ↓ (data preprocessing + standardization)
CashewTransformer.transform()
  ↓ (apply bank-specific mapping)
Return: CashewTransaction[]
```

### **3. Bank Detection Data Flow**
```
Filename + CSV Content 
  ↓
BankDetector.detect_bank()
  ↓ (initial detection)
BankConfigManager.detect_header_row()
  ↓ (bank-specific header detection)
Final BankDetectionResult
```

## 🚨 Critical Compatibility Rules

### **Data Structure Validation**
1. **Always verify format**: Check if data is `CSVRow[]` (array of dictionaries) or `object[]`
2. **Handle both formats**: Add fallback logic for different input types
3. **Access patterns**: Use `.get()` or `?.` for safe access
4. **Type checking**: Verify array vs object before processing

### **Bank Detection Integration**
```typescript
// ✅ CORRECT: Access detected bank info
const bankName = bankInfo.detected_bank;
const confidence = bankInfo.confidence;

// ❌ AVOID: Direct object access without checking
const bankName = bankInfo['bank_name']; // Wrong property name
```

### **CSV Data Access Patterns**
```typescript
// ✅ CORRECT: Safe dictionary access
const amount = row.get('Amount') || row['Amount'] || '';

// ✅ CORRECT: Handle missing data
const date = row['Date'] || row['date'] || '';

// ❌ AVOID: Array access on dictionary
const amount = row[1]; // Will fail if row is dictionary
```

## 📋 API Endpoint Data Contracts

### **POST /multi-csv/parse**
```typescript
// Request
{
  files: File[];
  parse_configs: {
    [filename: string]: {
      header_row?: number;
      start_row?: number;
      end_row?: number;
      encoding?: string;
    }
  };
  enable_cleaning?: boolean;
}

// Response: MultiCSVResponse
{
  success: boolean;
  results: CSVFileResult[];
}
```

### **POST /multi-csv/transform**
```typescript
// Request
{
  csv_data: CSVFileResult[];           // From parse endpoint
  user_name?: string;
  enable_transfer_detection?: boolean;
}

// Response: TransformationOutput
{
  success: boolean;
  data: CashewTransaction[];
}
```

## 🔧 Configuration Data Types

### **Bank Configuration Structure**
```typescript
interface BankConfig {
  bank_info: {
    name: string;
    file_patterns: string;              // Comma-separated
    detection_content_signatures: string;
    cashew_account: string;
  };
  csv_config: {
    expected_headers: string;           // Comma-separated
    header_row?: number;
    data_start_row?: number;
  };
  column_mapping: {
    [standardField: string]: string;    // Maps to CSV columns
  };
}
```

## 📝 Testing & Validation

### **Sample Data Structures for Testing**
```typescript
// Valid CSV row for testing
const testRow: CSVRow = {
  "Date": "2025-06-21",
  "Amount": "-1500.00", 
  "Description": "Test transaction",
  "Balance": "10000.00"
};

// Valid bank detection for testing
const testBankDetection: BankDetectionResult = {
  bank_name: "test_bank",
  confidence: 0.95,
  reasons: ["test signature match"]
};
```

## ⚠️ Known Legacy Issues (Avoid)

### **Removed/Deprecated Patterns**
- ❌ Preprocessing-aware components (removed in rollback)
- ❌ Array-based CSV row format
- ❌ Complex multi-file interdependencies
- ❌ Enhanced detection with configuration adjustment

### **Safe Development Guidelines**
1. **Stick to working patterns**: Use formats documented above
2. **Test incrementally**: Validate each data transformation
3. **Handle edge cases**: Always check for null/undefined
4. **Maintain compatibility**: Keep existing API contracts

## 📅 Last Updated
**Date:** 2025-06-21  
**Session:** Clean Baseline Data Standards Creation  
**Based On:** Working code after strategic rollback (commit 3e6ff14)

**🎯 Purpose:** Accurate documentation of proven data structures to guide safe development without introducing bugs from failed experiments.
