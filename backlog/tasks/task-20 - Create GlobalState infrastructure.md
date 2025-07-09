---
id: task-20
title: Create GlobalState infrastructure
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "High Priority", "Week 1"]
dependencies: ["task-13"]
---

## Description

Create the foundational React Context + useReducer infrastructure for centralized state management. This establishes the base architecture for migrating all 26 useState variables.

## Acceptance Criteria

- [ ] Create `frontend/src/context/GlobalState.js` with initial state structure
- [ ] Implement root reducer with combineReducers pattern
- [ ] Create GlobalStateProvider component
- [ ] Add action types and action creators in `frontend/src/context/actions.js`
- [ ] Create selector functions in `frontend/src/context/selectors.js`
- [ ] Write unit tests for reducers and action creators
- [ ] Update `frontend/src/App.js` to wrap app in GlobalStateProvider

## Context

Week 1 foundation task for Phase 5 Frontend State Management. This creates the infrastructure that all subsequent migration tasks will build upon.

## Files to Create

- `frontend/src/context/GlobalState.js`
- `frontend/src/context/actions.js`
- `frontend/src/context/reducers.js`
- `frontend/src/context/selectors.js`

## Files to Modify

- `frontend/src/App.js`

## Technical Notes

- Use normalized state structure with byId/allIds pattern for files
- Implement domain-separated reducers (files, processing, ui, configuration)
- Add TypeScript types if applicable
- Include error boundaries for context provider