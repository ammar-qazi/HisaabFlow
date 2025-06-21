# HisaabFlow Data Standards

## 🎯 Purpose
This document defines the **standardized data formats and API contracts** used by HisaabFlow after Phase 1 Type Safety & API Versioning implementation. All components must adhere to these specifications for reliable integration.

**✅ Status:** Updated for Phase 1 Type Safety Implementation and v1 API versioning.

---

## 📊 Core Data Types (Pydantic Models)

### **CSVRow (Pydantic Model)**
**Source:** `backend/models/csv_models.py`
```python
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

class CSVRow(BaseModel):
    date: date
    amount: Decimal
    description: str
    balance: Optional[Decimal] = None
```

### **BankDetectionResult (Pydantic Model)**
**Source:** `backend/models/csv_models.py`
```python
from pydantic import BaseModel, Field
from typing import List

class BankDetectionResult(BaseModel):
    bank_name: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)
```

---

## 🔗 API Endpoint Contracts (v1)

All core endpoints are now versioned under `/api/v1` prefix as implemented in `backend/main.py`.

### **POST /api/v1/upload**
**Purpose:** Upload a single CSV file and receive a unique file ID for subsequent operations.

```typescript
// Request: FormData with 'file' field
// Response
{
  "success": true,
  "file_id": "string",
  "original_name": "string", 
  "size": number
}
```

### **GET /api/v1/preview/{file_id}**
**Purpose:** Generate a preview of uploaded CSV with bank detection and suggested parsing parameters.

```typescript
// Request: GET with file_id in URL path
// Optional query params: encoding, header_row

// Response
{
  "success": true,
  "preview_data": Array<Array<string>>, // Raw CSV rows
  "bank_detection": {
    "bank_name": "string",
    "confidence": number,
    "reasons": Array<string>
  },
  "suggested_header_row": number,
  "suggested_data_start_row": number,
  "total_rows": number
}
```

### **POST /api/v1/multi-csv/parse**
**Purpose:** Parse one or more uploaded CSV files using their file IDs with custom parsing configurations.

```typescript
// Request
{
  "file_ids": Array<string>,
  "parse_configs": {
    [file_id: string]: {
      "header_row"?: number,
      "data_start_row"?: number,
      "encoding"?: string
    }
  },
  "enable_cleaning"?: boolean
}

// Response
{
  "success": true,
  "parsed_csvs": Array<{
    "file_id": string,
    "filename": string,
    "success": boolean,
    "bank_info": BankDetectionResult,
    "parse_result": {
      "success": boolean,
      "headers": Array<string>,
      "data": Array<CSVRow>,
      "row_count": number
    },
    "error"?: string
  }>
}
```

### **POST /api/v1/multi-csv/transform**
**Purpose:** Transform parsed CSV data into standardized Cashew format for export.

```typescript
// Request
{
  "csv_data_list": Array<ParsedCSVResult>, // From parse endpoint
  "user_name"?: string,
  "enable_transfer_detection"?: boolean
}

// Response  
{
  "success": true,
  "transformed_data": Array<{
    "Date": string,        // YYYY-MM-DD format
    "Amount": number,      // Numeric value
    "Title": string,       // Description
    "Account": string,     // Bank account identifier
    "Currency": string,    // Currency code
    "Category"?: string    // Optional category
  }>,
  "transfer_analysis"?: Object,
  "error"?: string
}
```

---

## 🔄 Data Processing Flow

### **Standard Upload → Transform Pipeline**
```
1. POST /api/v1/upload 
   ↓ (receives file_id)
2. GET /api/v1/preview/{file_id}
   ↓ (bank detection + parsing suggestions)  
3. POST /api/v1/multi-csv/parse
   ↓ (structured CSVRow data)
4. POST /api/v1/multi-csv/transform
   ↓ (standardized Cashew format)
```

### **Type Safety Integration**
All data structures are now validated using Pydantic models, ensuring:
- **Compile-time validation** of data formats
- **Automatic serialization/deserialization** 
- **Clear error messages** for invalid data
- **IDE support** with type hints

---

## ⚠️ Migration Notes

### **Breaking Changes from Previous Version**
- **TypeScript interfaces → Pydantic models**: Core data types now defined in Python
- **Unversioned APIs → /api/v1**: All endpoints require v1 prefix  
- **Enhanced type validation**: Stricter data format requirements
- **Improved error handling**: Pydantic validation errors

### **Backward Compatibility**
- API response formats remain functionally equivalent
- Frontend can be updated incrementally to use v1 endpoints
- Data structures maintain same field names and types

---

## 📅 Last Updated
**Date:** 2025-06-21  
**Update:** Phase 1 Type Safety & API Versioning  
**Changes:** 
- Updated Core Data Types to reference Pydantic models in `backend/models/csv_models.py`
- Replaced unversioned API contracts with v1 versioned endpoints
- Added type safety documentation and migration notes
