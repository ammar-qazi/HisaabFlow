---
id: task-21
title: Create file management custom hooks
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "High Priority", "Week 1"]
dependencies: ["task-20"]
---

## Description

Create custom hooks for file management operations to encapsulate file upload, selection, and management logic. This provides clean interfaces for components to interact with file state.

## Acceptance Criteria

- [ ] Create `useFileManagement` hook with file operations
- [ ] Create `useNavigation` hook for step navigation and loading states
- [ ] Implement file CRUD operations (add, remove, setActive)
- [ ] Add drag-and-drop state management
- [ ] Include computed values (allFiles, activeFile, fileCount)
- [ ] Write comprehensive tests for all custom hooks
- [ ] Add JSDoc documentation for hook interfaces

## Context

Week 1 task creating the custom hook layer that components will use to interact with the global state. These hooks abstract away the complexity of dispatch operations.

## Files to Create

- `frontend/src/hooks/useFileManagement.js`
- `frontend/src/hooks/useNavigation.js`
- `frontend/src/hooks/__tests__/useFileManagement.test.js`
- `frontend/src/hooks/__tests__/useNavigation.test.js`

## Technical Notes

- Use useCallback for all action functions to prevent unnecessary re-renders
- Include error handling in hook operations
- Provide both individual file operations and batch operations
- Ensure hooks are composable and reusable across components