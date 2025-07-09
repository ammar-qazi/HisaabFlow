---
id: task-24
title: Migrate processing state to global state
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "High Priority", "Week 2"]
dependencies: ["task-23"]
---

## Description

Migrate all processing-related state from ModernAppLogic.js to global state. This includes parsedResults, transformedData, transferAnalysis, and manuallyConfirmedTransfers.

## Acceptance Criteria

- [ ] Remove processing useState variables from ModernAppLogic.js
- [ ] Update createProcessingHandlers to use dispatch instead of setState
- [ ] Migrate useAutoConfiguration hook to use global state
- [ ] Replace processing props with useProcessing hook in components
- [ ] Ensure all async processing operations work correctly
- [ ] Update error handling to use global error state
- [ ] Maintain backward compatibility during migration
- [ ] Test complete processing pipeline end-to-end

## Context

Week 2 core migration task moving the most complex state (processing pipeline) to centralized management. This is critical for the application's main functionality.

## Files to Modify

- `frontend/src/components/modern/ModernAppLogic.js`
- `frontend/src/components/multi/ProcessingHandlers.js`
- `frontend/src/hooks/useAutoConfiguration.js`
- `frontend/src/components/modern/ModernConfigureAndReviewStep.js`

## State Variables to Migrate

- `parsedResults` → `state.processing.parsing.results`
- `transformedData` → `state.processing.transformation.data`
- `transferAnalysis` → `state.processing.transformation.analysis`
- `manuallyConfirmedTransfers` → `state.processing.transfers.manuallyConfirmed`
- `templates` → `state.configuration.templates`
- `bankConfigMapping` → `state.configuration.bankMapping`

## Testing Requirements

- [ ] File parsing pipeline works correctly
- [ ] Configuration application functions properly
- [ ] Transfer analysis generates correctly
- [ ] Manual transfer confirmation works
- [ ] Error states display properly
- [ ] Loading states function correctly
- [ ] No data loss during state transitions

## Risk Mitigation

- Implement feature flags for gradual rollout
- Keep backup useState implementations during transition
- Test each processing step independently
- Monitor for performance regressions