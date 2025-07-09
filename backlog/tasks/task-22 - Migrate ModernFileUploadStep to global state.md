---
id: task-22
title: Migrate ModernFileUploadStep to global state
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "High Priority", "Week 1"]
dependencies: ["task-21"]
---

## Description

Migrate ModernFileUploadStep component to use global state and custom hooks, removing props drilling for file management operations. This is the first component migration to validate the new architecture.

## Acceptance Criteria

- [ ] Remove file-related props from ModernFileUploadStep component
- [ ] Replace useState hooks with useFileManagement and useNavigation hooks
- [ ] Update ModernAppLogic to remove passed props to ModernFileUploadStep
- [ ] Ensure drag-and-drop functionality works with new state management
- [ ] Maintain all existing functionality (file upload, selection, removal)
- [ ] Update component tests to work with new hook-based architecture
- [ ] Verify no performance regressions in file operations

## Context

Week 1 validation task to ensure the new architecture works correctly with a real component. Success here validates the approach for all other components.

## Files to Modify

- `frontend/src/components/modern/ModernFileUploadStep.js`
- `frontend/src/components/modern/ModernAppLogic.js`

## Testing Requirements

- [ ] File upload still works correctly
- [ ] Drag and drop operations function properly
- [ ] Active file selection works
- [ ] File removal works correctly
- [ ] Component re-renders appropriately
- [ ] No memory leaks or performance issues

## Technical Notes

- Remove these props: fileInputRef, handleFileSelect, uploadedFiles, activeTab, setActiveTab, removeFile
- Replace with: useFileManagement(), useNavigation()
- Ensure fileInputRef is still managed locally if needed for DOM operations
- Test thoroughly as this validates the entire new architecture