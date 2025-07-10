---
id: task-21
title: Migrate File Upload Components to Zustand
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "High Priority", "Week 1"]
dependencies: ["task-20"]
---

## Description

**[UPDATED - Zustand Approach]** Migrate file upload components to use Zustand stores, removing props drilling for file management operations. This replaces the original custom hook approach with direct store usage.

## Acceptance Criteria

- [ ] Replace file-related useState hooks with useFileStore in ModernFileUploadStep
- [ ] Replace drag-and-drop useState hooks with useUIStore in ModernFileUploadStep
- [ ] Update ModernAppLogic to use useFileStore instead of local useState
- [ ] Remove file-related props drilling between components
- [ ] Maintain all existing functionality (file upload, selection, removal, drag-and-drop)
- [ ] Update component tests to work with Zustand stores
- [ ] Verify no performance regressions in file operations

## Context

Week 1 validation task to ensure the new Zustand architecture works correctly with real components. Success here validates the approach for all other components.

## Files to Modify

- `frontend/src/components/modern/ModernFileUploadStep.js`
- `frontend/src/components/modern/ModernAppLogic.js`

## Migration Pattern

### Before (useState + props)
```javascript
// ModernAppLogic.js
const [uploadedFiles, setUploadedFiles] = useState([])
const [activeTab, setActiveTab] = useState(0)

// ModernFileUploadStep.js
const ModernFileUploadStep = ({ uploadedFiles, activeTab, setActiveTab, removeFile }) => {
  const [dragOver, setDragOver] = useState(false)
  // ...
}
```

### After (Zustand stores)
```javascript
// ModernAppLogic.js
import useFileStore from '../store/useFileStore'
const { uploadedFiles, activeTab, setActiveTab, removeFile } = useFileStore()

// ModernFileUploadStep.js
import useFileStore from '../store/useFileStore'
import useUIStore from '../store/useUIStore'
const { uploadedFiles, activeTab, setActiveTab, removeFile } = useFileStore()
const { dragOver, setDragOver } = useUIStore()
```

## Testing Requirements

- [ ] File upload still works correctly
- [ ] Drag and drop operations function properly
- [ ] Active file selection works
- [ ] File removal works correctly
- [ ] Component re-renders appropriately
- [ ] No memory leaks or performance issues
- [ ] Props drilling eliminated

## Technical Notes

- **Remove these props**: fileInputRef, handleFileSelect, uploadedFiles, activeTab, setActiveTab, removeFile
- **Replace with**: Direct useFileStore() and useUIStore() usage
- **Keep local**: fileInputRef (DOM operations only)
- **Store mapping**: 
  - File operations → useFileStore
  - Drag/drop UI → useUIStore
- **Test thoroughly**: This validates the entire new Zustand architecture