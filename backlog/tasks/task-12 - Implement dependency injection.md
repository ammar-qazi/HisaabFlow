---
id: task-12
title: Implement dependency injection
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 4", "Backend", "API", "Medium Priority"]
dependencies: ["task-11"]
---

## Description

Refactor API endpoints to use dependency injection instead of creating service instances directly.

## Acceptance Criteria

- [ ] Update each endpoint in `backend/api/*_endpoints.py`
- [ ] Replace direct service instantiation with FastAPI `Depends` injection
- [ ] Example: `def transform_data(service: CashewTransformerService = Depends(CashewTransformerService))`
- [ ] Ensure all endpoints use dependency injection pattern
- [ ] Run integration tests to verify DI is working correctly

## Context

Part of Phase 4 Service Decomposition. This improves testability and maintainability through dependency injection.

## Files to Modify

- All endpoint files in `backend/api/*_endpoints.py`