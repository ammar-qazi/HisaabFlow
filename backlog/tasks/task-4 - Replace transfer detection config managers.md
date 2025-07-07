---
id: task-4
title: Replace transfer detection config managers
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 2", "Config", "Backend", "High Priority"]
dependencies: []
---

## Description

Update all files in `backend/transfer_detection/` to use the UnifiedConfigService instead of the old transfer detection config managers.

## Acceptance Criteria

- [ ] Update all transfer detection files to use UnifiedConfigService
- [ ] Maintain all existing transfer detection functionality
- [ ] Run integration tests to verify transfer detection works
- [ ] All existing transfer patterns continue to work

## Context

Part of Phase 2 Config Unification. This replaces the old `transfer_detection.config_manager` and `enhanced_config_manager` with the new unified service.

## Files to Modify

- All files in `backend/transfer_detection/` directory