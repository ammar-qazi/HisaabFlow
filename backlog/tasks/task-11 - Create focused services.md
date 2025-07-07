---
id: task-11
title: Create focused services
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 4", "Backend", "Medium Priority"]
dependencies: ["task-10"]
---

## Description

Create new focused services to replace the monolithic transformation and multi-CSV services.

## Acceptance Criteria

- [ ] Create `backend/services/cashew_transformer_service.py`
- [ ] Create `backend/services/transfer_detection_service.py`
- [ ] Create `backend/services/export_service.py`
- [ ] Move relevant logic from old services to new focused services
- [ ] Maintain backward compatibility during transition
- [ ] Create unit tests for each new service

## Context

Part of Phase 4 Service Decomposition. This creates smaller, focused services with single responsibilities.

## Files to Create

- `backend/services/cashew_transformer_service.py`
- `backend/services/transfer_detection_service.py`
- `backend/services/export_service.py`