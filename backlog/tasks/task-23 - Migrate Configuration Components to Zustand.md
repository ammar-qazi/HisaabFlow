---
id: task-23
title: Migrate Configuration Components to Zustand
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "Medium Priority", "Week 2"]
dependencies: ["task-22"]
---

## Description

**[UPDATED - Zustand Approach]** Migrate ModernConfigureAndReviewStep and all its sub-components to use Zustand stores. This removes props drilling in the configuration workflow and validates Zustand with complex component hierarchies.

## Acceptance Criteria

- [ ] Update ModernConfigureAndReviewStep to use Zustand stores
- [ ] Migrate AutoParseHandler to use useProcessingStore and useFileStore
- [ ] Update ConfidenceDashboard to use stores for metrics display
- [ ] Migrate AdvancedConfigPanel to use useUIStore for expansion state
- [ ] Update TransactionReview to use stores for data display
- [ ] Remove all props drilling between these components
- [ ] Ensure configuration workflow functions correctly
- [ ] Test auto-parsing and manual configuration features

## Context

Week 2 component migration task focusing on the configuration and review workflow. This validates Zustand with one of the most complex component hierarchies in the application.

## Files to Modify

- `frontend/src/components/modern/ModernConfigureAndReviewStep.js`
- `frontend/src/components/modern/configure-review/AutoParseHandler.js`
- `frontend/src/components/modern/configure-review/ConfidenceDashboard.js`
- `frontend/src/components/modern/configure-review/AdvancedConfigPanel.js`
- `frontend/src/components/modern/configure-review/TransactionReview.js`

## Migration Pattern

### Before (props drilling)
```javascript
// ModernConfigureAndReviewStep.js
<AutoParseHandler
  uploadedFiles={uploadedFiles}
  activeTab={activeTab}
  templates={templates}
  loading={loading}
  parsedResults={parsedResults}
  updateFileConfig={updateFileConfig}
  parseAllFiles={parseAllFiles}
/>
```

### After (Zustand stores)
```javascript
// AutoParseHandler.js
import useFileStore from '../../store/useFileStore'
import useProcessingStore from '../../store/useProcessingStore'

const { uploadedFiles, activeTab, templates } = useFileStore()
const { loading, parsedResults, updateFileConfig, parseAllFiles } = useProcessingStore()
```

## Store Mapping

### useFileStore
- uploadedFiles, activeTab, setActiveTab
- templates, bankConfigMapping
- selectedFileIndex

### useProcessingStore  
- parsedResults, setParsedResults
- loading, setLoading, error, setError
- transformedData, transferAnalysis

### useUIStore
- showAdvancedConfig, toggleAdvancedConfig
- expandedSections, toggleExpandedSection
- expandedFiles, toggleExpandedFile

## Props to Remove

From ModernConfigureAndReviewStep:
- uploadedFiles, activeTab, setActiveTab, templates, loading
- updateFileConfig, updateColumnMapping, applyTemplate
- previewFile, parseAllFiles, parsedResults

From sub-components:
- All passed props that are now available through stores

## Testing Requirements

- [ ] Auto-parsing triggers correctly
- [ ] Configuration dashboard displays accurate metrics
- [ ] Advanced configuration panel functions properly
- [ ] Transaction review shows correct data
- [ ] File expansion states work correctly
- [ ] Manual configuration overrides work
- [ ] Error states display appropriately
- [ ] Props drilling eliminated

## Technical Notes

- Use React.memo to prevent unnecessary re-renders
- Leverage Zustand's selective subscriptions for performance
- Ensure proper cleanup of event listeners and timers
- Test with different data scenarios (success, error, empty)
- Monitor component re-render patterns with React DevTools