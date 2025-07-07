---
id: task-7
title: Consolidate API versions
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 3", "API", "Backend", "High Priority"]
dependencies: ["task-6"]
---

## Description

Unify API router prefix and remove deprecated API versions to standardize all endpoints.

## Acceptance Criteria

- [ ] Ensure all routers use consistent prefix (e.g., `/api/v1`) in `backend/api/routes.py`
- [ ] Remove routing logic for deprecated versions like `/api/v3`
- [ ] Update all endpoint paths to use standardized format
- [ ] Run integration tests to verify all endpoints work

## Context

Part of Phase 3 API Stabilization. This consolidates API versions and removes deprecated endpoints.

## Files to Modify

- `backend/api/routes.py`
- Any files with deprecated API version references