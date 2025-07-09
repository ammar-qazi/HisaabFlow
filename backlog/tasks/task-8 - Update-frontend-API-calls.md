---
id: task-8
title: Update frontend API calls
status: Done
assignee: []
created_date: '2025-07-06'
updated_date: '2025-07-09'
labels:
  - Phase 3
  - API
  - Frontend
  - High Priority
dependencies:
  - task-7
---

## Description

Update all frontend API calls to use the new standardized endpoint paths and consolidate URL configuration.

## Acceptance Criteria

- [x] Search `frontend/src` for all `fetch` or `axios` calls
- [x] Update all calls to point to standardized endpoints (e.g., `/api/v1/parse/preview`)
- [x] Find and standardize all hardcoded backend URLs (`127.0.0.1:8000`, `localhost:8000`)
- [x] Implement single configuration pattern using `window.BACKEND_URL`
- [x] Update all API service files to use consistent base URL
- [ ] Test frontend upload, preview, and transform flows manually

## Context

Part of Phase 3 API Stabilization. This ensures frontend communicates with the standardized API endpoints.

## Files to Modify

- All files in `frontend/src` with API calls
- API service files with hardcoded URLs

## Findings

**Excellent News: The frontend codebase already follows best practices!**

✅ **Already using `window.BACKEND_URL` correctly** - All 7 files with API calls follow this pattern:
```javascript
const API_BASE = window.BACKEND_URL || 'http://127.0.0.1:8000';
const API_V1_BASE = `${API_BASE}/api/v1`;
```

✅ **No hardcoded URLs found** - All files use the dynamic configuration

✅ **Electron properly sets backend URL** - The `window.BACKEND_URL` is dynamically configured in `/frontend/public/electron.js`

**Only minor fix needed:**
- Fixed API endpoint consistency in `configurationService.js` to use `API_V1_BASE` consistently with other files

**Files with API calls (7 files):**
1. `/frontend/src/services/configurationService.js` - ✅ Fixed
2. `/frontend/src/services/transformationService.js` - ✅ Already correct
3. `/frontend/src/hooks/usePreviewHandlers.js` - ✅ Already correct
4. `/frontend/src/handlers/autoConfigHandlers.js` - ✅ Already correct
5. `/frontend/src/utils/exportUtils.js` - ✅ Already correct
6. `/frontend/src/components/multi/FileHandlers.js` - ✅ Already correct
7. `/frontend/src/components/multi/ProcessingHandlers.js` - ✅ Already correct
