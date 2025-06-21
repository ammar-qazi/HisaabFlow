# AI Development Workflow & Guidelines

## 🧹 ROLLBACK LESSONS LEARNED
**Date:** 2025-06-21 - Strategic rollback completed

### **🚨 AVOID THESE APPROACHES (Caused Previous Bugs):**
1. **Complex Multi-File Systems**: Don't create 5+ interdependent files at once
   - ❌ preprocessing_aware_service.py + configuration_adjuster.py + enhanced_preprocessor.py + preprocessing_mapper.py + enhanced_bank_detector.py
   - ✅ Add ONE enhancement file at a time, test thoroughly

2. **Massive File Modifications**: Don't edit 300+ line files without splitting first  
   - ❌ Modifying multi_csv_service.py (382 lines) with complex integration
   - ✅ Split large files BEFORE adding features

3. **Tight Coupling**: Don't create components that depend on many others
   - ❌ Service depending on 5+ other components
   - ✅ Loose coupling with clear interfaces

4. **Rapid Multi-Feature Integration**: Don't add multiple features simultaneously
   - ❌ Adding preprocessing + bank detection + configuration adjustment together
   - ✅ Add one feature, test, validate, then add next

### **✅ FOLLOW THESE APPROACHES (Proven Safe):**
1. **Single Responsibility**: One clear purpose per file/component
2. **Gradual Enhancement**: Add → Test → Validate → Repeat
3. **Constraint Respect**: Never exceed 200 lines without splitting first
4. **Minimal Dependencies**: Limit imports and coupling
5. **Immediate Validation**: Test every single change before moving forward

### **🎯 SAFE DEVELOPMENT SEQUENCE:**
1. **Choose the smallest possible enhancement**
2. **Check if target file is under 150 lines** (safety margin)
3. **If not, split the file first** 
4. **Make minimal change**
5. **Test immediately**
6. **Validate end-to-end**
7. **Only then proceed to next change**

## 📋 START SESSION CHECKLIST
1. [ ] Read CURRENT_STATE.md
2. [ ] Check CODEBASE_MAP.md for file sizes
3. [ ] Identify files to modify
4. [ ] Check if any files are in "DO NOT TOUCH" list

## ⚡ CORE DEVELOPMENT RULES

## 🏗️ DATA STRUCTURE VALIDATION RULE
**CRITICAL: Before modifying any data transformation logic:**

### **📋 Pre-Modification Checklist:**
1. **Trace the data source**: Identify what format the upstream component returns
2. **Examine the destination**: Check what format the downstream component expects  
3. **Verify compatibility**: Ensure data structures match exactly
4. **Add conversion if needed**: Bridge mismatched formats with proper transformation

### **🔍 Common Structure Patterns to Check:**
- **Arrays vs Dictionaries**: `[item1, item2]` vs `{key: value}`
- **Nested vs Flat**: `{user: {name: "X"}}` vs `{user_name: "X"}`
- **Field naming**: `camelCase` vs `snake_case` vs `PascalCase`
- **Data types**: `string` vs `number` vs `boolean`
- **List vs Single item**: `[{item}]` vs `{item}`

### **💡 Validation Example:**
```python
# ALWAYS VERIFY BEFORE CHANGING:
# 1. Parser returns: {Date: "2025-06-10", Amount: "-18,063"}
# 2. Transform expects: [date, amount] or {date, amount}?
# 3. Add bridge if needed:

# Bad (assumes array):
date = row[0]  # FAILS if row is dict

# Good (handles both):
if isinstance(row, dict):
    date = row.get("Date", "")
elif isinstance(row, list):
    date = row[0] if len(row) > 0 else ""
```

### **🚨 Red Flags to Watch For:**
- `row[0]` when data might be dictionaries
- `len(obj)` without checking type first  
- Field access without `.get()` fallbacks
- Assuming consistent data format across components

### **🎯 This Rule Prevents:**
- Silent failures with cryptic "0" errors
- Type errors in production
- Data structure mismatches between components
- Complex debugging sessions

### Code Quality
- **Be modular** - Single responsibility principle
- **You're an expert full-stack developer** - Make confident technical decisions
- **70 lines max per tool call** - Prevents context corruption
- **200 lines max per file** - Split if approaching limit
- **Prefer editing existing files** over creating new ones
- **Use edit_file over write_file** when possible

### Development Approach  
- **Debug instead of test** - Inline validation only
- **Confirm before major changes** - Ask user before switching approaches
- **No test files** - Use console.log, print statements in main code
- **No external docs** without user approval
- **Read existing files** before making changes

### File Operations
- **Batch operations** - Read all needed files, then make changes
- **Search first** - Use search_files to find existing functionality
- **Simple fallbacks** - If operations fail, use simpler approaches

## 🐍 Python Conventions
```python
# File naming: snake_case.py
# Class naming: PascalCase
# Function naming: snake_case
# Constants: UPPER_SNAKE_CASE

# Import order:
# 1. Standard library
# 2. Third-party packages  
# 3. Local modules
```

## ⚛️ Frontend Conventions
```typescript
// File naming: PascalCase.tsx for components, camelCase.ts for utils
// Component naming: PascalCase
// Function naming: camelCase
// Constants: UPPER_SNAKE_CASE

// Component structure:
# 1. Imports
# 2. Types/interfaces
# 3. Component function
# 4. Default export
```

## 🔄 Multi-AI Handoff Protocol
1. **Before ending session:**
   - Update CURRENT_STATE.md with progress
   - Update CODEBASE_MAP.md if files changed
   - List next logical steps
   - Note any blockers encountered

2. **Conflict Resolution:**
   - If approach differs from previous AI: Ask user for guidance
   - Document decision rationale in CURRENT_STATE.md

## 🚨 VALIDATION APPROACH
**INLINE ONLY:**
```python
# Good: Debugging in main code
def process_file(file_path):
    print(f"Processing: {file_path}")  # Debug output
    result = parse_data(file_path)
    print(f"Parsed {len(result)} transactions")  # Debug output
    return result

# Bad: Separate test file
# test_process_file.py ❌ DO NOT CREATE
```

## 📝 UPDATE REQUIREMENTS
- Update CURRENT_STATE.md every session
- Update CODEBASE_MAP.md when files are modified
- Ask before creating new documentation files
