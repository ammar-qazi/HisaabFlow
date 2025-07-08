---
id: task-3
title: Replace bank detection config manager
status: Done
assignee: []
created_date: '2025-07-06'
updated_date: '2025-07-08'
labels:
  - Phase 2
  - Config
  - Backend
  - High Priority
dependencies: []
---

## Description

Update `backend/bank_detection/bank_detector.py` to use the UnifiedConfigService instead of the old bank detection config manager.

## Acceptance Criteria

- [x] Update bank_detector.py to use UnifiedConfigService
- [x] Maintain all existing bank detection functionality
- [x] Run integration tests to verify bank detection works
- [x] All existing bank configs continue to work

## Context

Part of Phase 2 Config Unification. This replaces the old `bank_detection.config_manager` with the new unified service.

## Files Modified

- `backend/bank_detection/bank_detector.py` - Updated to use UnifiedConfigService directly
- `backend/services/preview_service.py` - Updated to use UnifiedConfigService
- `backend/services/transformation_service.py` - Updated to use UnifiedConfigService and fixed ConfigParser usage
- `backend/services/multi_csv_service.py` - Updated to use UnifiedConfigService
- `backend/services/parsing_service.py` - Updated to use UnifiedConfigService
- `backend/bank_detection/__init__.py` - Updated to export UnifiedConfigService helper

## Completion Notes

✅ **Task completed successfully** - All services migrated from BankDetectionFacade to UnifiedConfigService
✅ **Integration tests passing** - Bank detection functionality maintained
✅ **ConfigParser compatibility issues resolved** - Fixed all `.has_section()`, `.sections()`, `.get()`, and `.items()` calls
✅ **Multi-CSV processing working** - All 4 banks detect correctly with proper confidence scores
✅ **Phase 2 Config Unification achieved** - No more legacy config managers in use
