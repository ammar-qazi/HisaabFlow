---
id: task-24
title: Migrate Transform and Export Components to Zustand
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "Medium Priority", "Week 2"]
dependencies: ["task-23"]
---

## Description

**[UPDATED - Zustand Approach]** Migrate ModernTransformAndExportStep and all its sub-components to use Zustand stores. This completes the component migration by updating the final step in the workflow and eliminates all remaining props drilling.

## Acceptance Criteria

- [ ] Update ModernTransformAndExportStep to use Zustand stores
- [ ] Migrate TransferAnalysisPanel to use useProcessingStore for transfer state
- [ ] Update InteractiveDataTable to use useUIStore for table state
- [ ] Migrate ExportOptions to use useProcessingStore for export state
- [ ] Remove all remaining props drilling in transform/export workflow
- [ ] Ensure export functionality works correctly
- [ ] Test transfer analysis interactions thoroughly
- [ ] Verify data table performance with large datasets

## Context

Week 2 component migration task completing the transformation of all step components. This finalizes the elimination of props drilling throughout the application using Zustand stores.

## Files to Modify

- `frontend/src/components/modern/ModernTransformAndExportStep.js`
- `frontend/src/components/modern/transform-export/TransferAnalysisPanel.js`
- `frontend/src/components/modern/transform-export/InteractiveDataTable.js`
- `frontend/src/components/modern/transform-export/ExportOptions.js`

## Migration Pattern

### Before (props drilling)
```javascript
// ModernTransformAndExportStep.js
<TransferAnalysisPanel
  transferAnalysis={transferAnalysis}
  manuallyConfirmedTransfers={manuallyConfirmedTransfers}
  setManuallyConfirmedTransfers={setManuallyConfirmedTransfers}
  expandedTransfers={expandedTransfers}
  setExpandedTransfers={setExpandedTransfers}
/>

<InteractiveDataTable
  data={transformedData}
  searchTerm={searchTerm}
  setSearchTerm={setSearchTerm}
  sortConfig={sortConfig}
  setSortConfig={setSortConfig}
/>
```

### After (Zustand stores)
```javascript
// TransferAnalysisPanel.js
import useProcessingStore from '../../store/useProcessingStore'

const { 
  transferAnalysis, 
  manuallyConfirmedTransfers, 
  addManuallyConfirmedTransfer,
  expandedTransfers, 
  toggleExpandedTransfer
} = useProcessingStore()

// InteractiveDataTable.js
import useProcessingStore from '../../store/useProcessingStore'
import useUIStore from '../../store/useUIStore'

const { transformedData } = useProcessingStore()
const { searchTerm, setSearchTerm, sortConfig, setSortConfig } = useUIStore()
```

## Store Mapping

### useProcessingStore
- transformedData, setTransformedData
- transferAnalysis, setTransferAnalysis
- manuallyConfirmedTransfers, addManuallyConfirmedTransfer
- expandedTransfers, toggleExpandedTransfer
- exporting, setExporting
- exportSuccess, setExportSuccess

### useUIStore
- searchTerm, setSearchTerm
- sortConfig, setSortConfig
- filterCategory, setFilterCategory
- currentPage, setCurrentPage
- itemsPerPage, setItemsPerPage

## Props to Remove

From ModernTransformAndExportStep:
- transformedData, setTransformedData, transferAnalysis
- manuallyConfirmedTransfers, setManuallyConfirmedTransfers
- loading, exportData

From TransferAnalysisPanel:
- All state-related props (now handled by stores)

From InteractiveDataTable:
- All table state props (now handled by stores)

From ExportOptions:
- Export state props (now handled by stores)

## Testing Requirements

- [ ] Transfer analysis panel functions correctly
- [ ] Transfer confirmation workflow works
- [ ] Data table sorting/filtering performs well
- [ ] Export functionality generates correct files
- [ ] Large dataset handling is performant
- [ ] Error states display appropriately
- [ ] Loading states function correctly
- [ ] Props drilling eliminated

## Performance Considerations

- Use React.memo for expensive components
- Leverage Zustand's selective subscriptions for performance
- Implement virtualization for large data tables
- Optimize transfer analysis rendering
- Add debouncing for search operations
- Monitor component re-render patterns