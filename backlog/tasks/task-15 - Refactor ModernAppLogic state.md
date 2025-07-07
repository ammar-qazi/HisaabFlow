---
id: task-15
title: Refactor ModernAppLogic state
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 5", "Frontend", "Medium Priority"]
dependencies: ["task-14"]
---

## Description

Refactor `ModernAppLogic.js` to use the new centralized state management instead of multiple useState hooks.

## Acceptance Criteria

- [ ] Remove multiple `useState` calls from ModernAppLogic.js
- [ ] Replace with single `const [state, dispatch] = useContext(GlobalStateContext)`
- [ ] Replace all `set...()` calls with `dispatch({ type: 'ACTION_NAME', payload: ... })`
- [ ] Optionally decompose into smaller hooks like `useFileUploads(dispatch)` or `useDataProcessing(state, dispatch)`
- [ ] Test all frontend functionality to ensure state management works correctly

## Context

Part of Phase 5 Frontend State Management. This completes the refactoring of complex frontend state management.

## Files to Modify

- `frontend/src/components/modern/ModernAppLogic.js`