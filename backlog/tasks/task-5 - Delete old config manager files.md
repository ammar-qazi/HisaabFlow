---
id: task-5
title: Delete old config manager files
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 2", "Config", "Backend", "High Priority"]
dependencies: ["task-2", "task-3", "task-4"]
---

## Description

Remove the four old config manager files after successful migration to UnifiedConfigService.

## Acceptance Criteria

- [ ] Verify all integration tests pass with new UnifiedConfigService
- [ ] Remove `backend/api/config_manager.py`
- [ ] Remove `backend/bank_detection/config_manager.py`
- [ ] Remove `backend/transfer_detection/config_manager.py`
- [ ] Remove `backend/transfer_detection/enhanced_config_manager.py`
- [ ] Run final integration tests to confirm nothing is broken

## Context

Part of Phase 2 Config Unification. This is the final cleanup step after migrating all code to use the unified service.

## Files to Delete

- `backend/api/config_manager.py` (215 lines)
- `backend/bank_detection/config_manager.py` (324 lines)
- `backend/transfer_detection/config_manager.py` (256 lines)
- `backend/transfer_detection/enhanced_config_manager.py` (136 lines)