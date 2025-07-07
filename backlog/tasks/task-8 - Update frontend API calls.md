---
id: task-8
title: Update frontend API calls
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 3", "API", "Frontend", "High Priority"]
dependencies: ["task-7"]
---

## Description

Update all frontend API calls to use the new standardized endpoint paths and consolidate URL configuration.

## Acceptance Criteria

- [ ] Search `frontend/src` for all `fetch` or `axios` calls
- [ ] Update all calls to point to standardized endpoints (e.g., `/api/v1/parse/preview`)
- [ ] Find and standardize all hardcoded backend URLs (`127.0.0.1:8000`, `localhost:8000`)
- [ ] Implement single configuration pattern using `window.BACKEND_URL`
- [ ] Update all API service files to use consistent base URL
- [ ] Test frontend upload, preview, and transform flows manually

## Context

Part of Phase 3 API Stabilization. This ensures frontend communicates with the standardized API endpoints.

## Files to Modify

- All files in `frontend/src` with API calls
- API service files with hardcoded URLs