---
id: task-28
title: Migrate transform and export components
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "Medium Priority", "Week 4"]
dependencies: ["task-27"]
---

## Description

Migrate ModernTransformAndExportStep and all its sub-components to use global state and custom hooks. This completes the component migration by updating the final step in the workflow.

## Acceptance Criteria

- [ ] Update ModernTransformAndExportStep to use custom hooks
- [ ] Migrate TransferAnalysisPanel to use useTransferAnalysis hook
- [ ] Update InteractiveDataTable to use useDataTable hook
- [ ] Migrate ExportOptions to use useExport hook
- [ ] Remove all remaining props drilling in transform/export workflow
- [ ] Ensure export functionality works correctly
- [ ] Test transfer analysis interactions thoroughly
- [ ] Verify data table performance with large datasets

## Context

Week 4 component migration task completing the transformation of all step components. This finalizes the elimination of props drilling throughout the application.

## Files to Modify

- `frontend/src/components/modern/ModernTransformAndExportStep.js`
- `frontend/src/components/modern/transform-export/TransferAnalysisPanel.js`
- `frontend/src/components/modern/transform-export/InteractiveDataTable.js`
- `frontend/src/components/modern/transform-export/ExportOptions.js`

## Props to Remove

From ModernTransformAndExportStep:
- transformedData, setTransformedData, transferAnalysis
- manuallyConfirmedTransfers, setManuallyConfirmedTransfers
- loading, exportData

From TransferAnalysisPanel:
- All state-related props (now handled by useTransferAnalysis)

From InteractiveDataTable:
- All table state props (now handled by useDataTable)

From ExportOptions:
- Export state props (now handled by useExport)

## Testing Requirements

- [ ] Transfer analysis panel functions correctly
- [ ] Transfer confirmation workflow works
- [ ] Data table sorting/filtering performs well
- [ ] Export functionality generates correct files
- [ ] Large dataset handling is performant
- [ ] Error states display appropriately
- [ ] Loading states function correctly

## Performance Considerations

- Use React.memo for expensive components
- Implement virtualization for large data tables
- Optimize transfer analysis rendering
- Add debouncing for search operations