---
id: task-3
title: Replace bank detection config manager
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 2", "Config", "Backend", "High Priority"]
dependencies: []
---

## Description

Update `backend/bank_detection/bank_detector.py` to use the UnifiedConfigService instead of the old bank detection config manager.

## Acceptance Criteria

- [ ] Update bank_detector.py to use UnifiedConfigService
- [ ] Maintain all existing bank detection functionality
- [ ] Run integration tests to verify bank detection works
- [ ] All existing bank configs continue to work

## Context

Part of Phase 2 Config Unification. This replaces the old `bank_detection.config_manager` with the new unified service.

## Files to Modify

- `backend/bank_detection/bank_detector.py`