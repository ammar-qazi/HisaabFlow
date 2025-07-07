---
id: task-14
title: Create global state context
status: To Do
assignee: []
created_date: '2025-07-06'
labels: ["Phase 5", "Frontend", "Medium Priority"]
dependencies: ["task-13"]
---

## Description

Implement a centralized state management solution using React Context with useReducer.

## Acceptance Criteria

- [ ] Create `frontend/src/context/GlobalState.js`
- [ ] Define initial state object with all state variables
- [ ] Create main reducer function with action types
- [ ] Create `GlobalStateProvider` component
- [ ] Wrap main app in `<GlobalStateProvider>` in `frontend/src/App.js`
- [ ] Define action creators for common state updates

## Context

Part of Phase 5 Frontend State Management. This creates the foundation for centralized state management.

## Files to Create/Modify

- `frontend/src/context/GlobalState.js` (new)
- `frontend/src/App.js` (modify to add provider)