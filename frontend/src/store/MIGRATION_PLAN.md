# Zustand Migration Plan

## Overview
Migration plan for replacing 26 useState variables with Zustand stores, following expert panel recommendations.

## Current State Analysis
Based on frontend code analysis, the following components contain useState variables that need migration:

### High Priority Components (Core State)
1. **ModernAppLogic.js** - 9 core state variables
2. **ModernMultiCSVApp.js** - Navigation state
3. **ModernFileUploadStep.js** - File upload state
4. **ModernConfigureAndReviewStep.js** - Configuration state

### Medium Priority Components (UI State)
1. **InteractiveDataTable.js** - Table state
2. **TransferAnalysisPanel.js** - Transfer UI state
3. **ModernDataReviewStep.js** - Review state
4. **ExportOptions.js** - Export state

### Low Priority Components (Leaf Components)
1. **TransformationProgress.js** - Stage index
2. **ModernFileConfigurationStep.js** - Selection state
3. **TransactionReview.js** - Expansion state

## Store Mapping

### useFileStore → Components
- **ModernAppLogic.js**: `uploadedFiles`, `activeTab`, `parsedResults`, `templates`, `bankConfigMapping`
- **ModernFileUploadStep.js**: `uploadedFiles`, `dragOver`, `dragCounter`
- **ModernConfigureAndReviewStep.js**: `selectedFileIndex`, `templates`

### useProcessingStore → Components
- **ModernAppLogic.js**: `loading`, `error`, `transformedData`, `transferAnalysis`, `manuallyConfirmedTransfers`
- **TransferAnalysisPanel.js**: `expandedTransfers`, `expandedPotentialTransfers`, `selectedPotentialTransfers`
- **ModernDataReviewStep.js**: `isApplyingCategorization`, `stageIndex`
- **ExportOptions.js**: `exporting`, `exportSuccess`, `selectedFormat`

### useUIStore → Components
- **ModernMultiCSVApp.js**: `currentStep`
- **ModernConfigureAndReviewStep.js**: `showAdvancedConfig`, `expandedSections`
- **InteractiveDataTable.js**: `searchTerm`, `sortConfig`, `filterCategory`, `currentPage`, `itemsPerPage`
- **ModernDataReviewStep.js**: `viewMode`, `expandedFiles`, `validationChecklist`

## Migration Strategy

### Phase 1: Core Infrastructure (Completed)
- [x] Install Zustand package
- [x] Create useFileStore
- [x] Create useProcessingStore
- [x] Create useUIStore

### Phase 2: High Priority Migration (Week 1)
1. **ModernAppLogic.js** (Day 1-2)
   - Replace core state variables with store imports
   - Update handler functions to use store actions
   - Remove useState declarations
   - Test file upload and processing flow

2. **ModernFileUploadStep.js** (Day 2-3)
   - Migrate file upload state to useFileStore
   - Update drag-and-drop handlers
   - Remove local useState variables
   - Test file upload functionality

3. **ModernMultiCSVApp.js** (Day 3)
   - Migrate currentStep to useUIStore
   - Update navigation handlers
   - Test step navigation flow

### Phase 3: Medium Priority Migration (Week 2)
1. **ModernConfigureAndReviewStep.js** (Day 1-2)
   - Migrate configuration state to appropriate stores
   - Update configuration handlers
   - Test configuration flow

2. **InteractiveDataTable.js** (Day 2-3)
   - Migrate table state to useUIStore
   - Update filtering and sorting handlers
   - Test table functionality

3. **TransferAnalysisPanel.js** (Day 3-4)
   - Migrate transfer UI state to useProcessingStore
   - Update transfer selection handlers
   - Test transfer analysis flow

4. **ModernDataReviewStep.js** (Day 4-5)
   - Migrate review state to appropriate stores
   - Update review handlers
   - Test data review functionality

### Phase 4: Low Priority Migration (Week 3)
1. **ExportOptions.js** (Day 1)
   - Migrate export state to useProcessingStore
   - Update export handlers
   - Test export functionality

2. **TransformationProgress.js** (Day 2)
   - Migrate stage index to useProcessingStore
   - Update progress handlers
   - Test progress display

3. **Remaining Components** (Day 3-5)
   - Migrate remaining useState variables
   - Update component handlers
   - Test remaining functionality

### Phase 5: Cleanup and Optimization (Week 4)
1. **Remove Unused Code** (Day 1-2)
   - Remove all useState imports where replaced
   - Remove old handler functions
   - Clean up prop drilling

2. **Performance Optimization** (Day 3-4)
   - Add React DevTools integration
   - Optimize re-render patterns
   - Add state persistence if needed

3. **Testing and Validation** (Day 5)
   - End-to-end testing of all flows
   - Performance testing
   - User acceptance testing

## Migration Patterns

### Before (useState)
```javascript
const [uploadedFiles, setUploadedFiles] = useState([])
const [activeTab, setActiveTab] = useState(0)

const addFile = (file) => {
  setUploadedFiles(prev => [...prev, file])
}
```

### After (Zustand)
```javascript
import useFileStore from '../store/useFileStore'

const { uploadedFiles, activeTab, addFiles } = useFileStore()

const addFile = (file) => {
  addFiles([file])
}
```

## Testing Strategy

### Unit Tests
- Test store actions and state updates
- Test component integration with stores
- Test store state persistence

### Integration Tests
- Test full user workflows with new state management
- Test cross-component state synchronization
- Test performance with large datasets

### Migration Testing
- Test each component migration independently
- Ensure backward compatibility during transition
- Test rollback scenarios if needed

## Risk Mitigation

### Gradual Migration
- Migrate one component at a time
- Maintain existing functionality during transition
- Test thoroughly at each step

### Rollback Plan
- Keep original useState code in comments initially
- Maintain git branches for each migration step
- Document any breaking changes

### Performance Monitoring
- Monitor component re-render patterns
- Track bundle size changes
- Measure application performance

## Benefits Expected

### Code Reduction
- 85% reduction in state management code
- Elimination of prop drilling
- Simpler component interfaces

### Performance Improvements
- Selective component updates
- No provider re-render overhead
- Better memory efficiency

### Developer Experience
- Simpler debugging with React DevTools
- Clearer state update patterns
- Reduced complexity in component logic

## Success Metrics

### Technical Metrics
- [ ] 90% reduction in useState variables
- [ ] 70% reduction in props passed between components
- [ ] 40% improvement in component re-render performance
- [ ] 100% test coverage for new stores

### User Experience Metrics
- [ ] Maintain current application performance
- [ ] No regression in user functionality
- [ ] Improved application responsiveness

## Next Steps

1. Begin Phase 2 migration with ModernAppLogic.js
2. Create unit tests for each store
3. Update documentation for new architecture
4. Schedule team review of migration progress

## Notes

- This migration follows expert panel recommendations to use Zustand
- The original 4-week Context + useReducer plan has been replaced with this 3-week Zustand migration
- All stores are designed to be simple and maintainable
- No provider wrapping is required - stores work directly with components