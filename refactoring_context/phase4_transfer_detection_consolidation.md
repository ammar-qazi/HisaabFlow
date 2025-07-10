# Phase 4: Transfer Detection Consolidation Plan

## Current State Analysis
- `backend/transfer_detection/` - Contains actual detection algorithms (6 files, ~420 lines)
- `backend/core/transfer_detection/` - Contains service wrapper (1 file, ~92 lines)
- This creates architectural inconsistency and violates DRY principle

## Consolidation Strategy: Move to Core Domain Logic

### Step 1: Move All Transfer Detection Logic
- **Action**: Move all files from `backend/transfer_detection/` to `backend/core/transfer_detection/`
- **Rationale**: Keep all domain logic in `core/` for architectural consistency
- **Files to move**: 
  - `main_detector.py` → `backend/core/transfer_detection/detector.py`
  - `amount_parser.py` → `backend/core/transfer_detection/amount_parser.py`
  - `date_parser.py` → `backend/core/transfer_detection/date_parser.py`
  - `cross_bank_matcher.py` → `backend/core/transfer_detection/cross_bank_matcher.py`
  - `currency_converter.py` → `backend/core/transfer_detection/currency_converter.py`
  - `confidence_calculator.py` → `backend/core/transfer_detection/confidence_calculator.py`

### Step 2: Maintain Simple Class Names
- Keep `TransferDetector` (not TransferDomainService)
- Keep `CrossBankMatcher`, `CurrencyConverter`, etc.
- No fancy renaming - simple, clear names

### Step 3: Update Import Statements
- Update all files importing from `backend.transfer_detection`
- Use new path: `backend.core.transfer_detection`
- Likely files to update: services, API endpoints, tests

### Step 4: Clean Up
- Remove empty `backend/transfer_detection/` directory
- Update `__init__.py` files for proper module exports

## Benefits
- **Single Source of Truth**: One location for transfer detection logic
- **Architectural Consistency**: All domain logic in `core/`
- **Cleaner Dependencies**: No more confusing imports
- **Maintainability**: Easier to understand and modify

## Implementation Time
- **Estimated**: 1 hour
- **Risk**: Low (mostly file moves and import updates)
- **Validation**: Run existing tests to ensure no regression

## Implementation Steps

1. **Save Phase 4 plan** to refactoring_context directory ✓
2. **Move transfer detection files** from `backend/transfer_detection/` to `backend/core/transfer_detection/`
3. **Update import statements** across codebase for new transfer detection location
4. **Clean up** empty `backend/transfer_detection/` directory
5. **Run tests** to validate transfer detection consolidation

## Files That Will Need Import Updates
- Services layer files
- API endpoint files  
- Test files
- Main application files

This consolidation follows the "One Way" principle - single method for each task, with transfer detection having one canonical location in the domain layer.