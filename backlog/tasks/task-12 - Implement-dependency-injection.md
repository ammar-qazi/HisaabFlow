---
id: task-12
title: Implement dependency injection
status: Done
assignee: []
created_date: '2025-07-06'
updated_date: '2025-07-09'
labels:
  - Phase 4
  - Backend
  - API
  - Medium Priority
dependencies:
  - task-11
---

## Description

Refactor API endpoints to use dependency injection instead of creating service instances directly.

## Acceptance Criteria

- [x] Update each endpoint in `backend/api/*_endpoints.py`
- [x] Replace direct service instantiation with FastAPI `Depends` injection
- [x] Example: `def transform_data(service: CashewTransformerService = Depends(CashewTransformerService))`
- [x] Ensure all endpoints use dependency injection pattern
- [x] Run integration tests to verify DI is working correctly

## Context

Part of Phase 4 Service Decomposition. This improves testability and maintainability through dependency injection.

## Files to Modify

- All endpoint files in `backend/api/*_endpoints.py`
