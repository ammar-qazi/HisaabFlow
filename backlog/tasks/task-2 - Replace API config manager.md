---
id: task-2
title: Replace API config manager
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 2", "Config", "API", "High Priority"]
dependencies: []
---

## Description

Update `backend/api/config_endpoints.py` to use the UnifiedConfigService instead of the old API config manager.

## Acceptance Criteria

- [ ] Update config_endpoints.py to use UnifiedConfigService
- [ ] Maintain backward compatibility with existing API contracts
- [ ] Run integration tests to verify functionality
- [ ] All existing API endpoints continue to work

## Context

Part of Phase 2 Config Unification. This replaces the old `api.config_manager` with the new unified service.

## Files to Modify

- `backend/api/config_endpoints.py`