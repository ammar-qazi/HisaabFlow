---
id: task-26
title: Migrate configure and review components
status: To Do
assignee: []
created_date: '2025-07-09'
labels: ["Phase 5", "Frontend", "Medium Priority", "Week 3"]
dependencies: ["task-25"]
---

## Description

Migrate ModernConfigureAndReviewStep and all its sub-components to use global state and custom hooks. This removes the remaining props drilling in the configuration workflow.

## Acceptance Criteria

- [ ] Update ModernConfigureAndReviewStep to use custom hooks
- [ ] Migrate AutoParseHandler to use global processing state
- [ ] Update ConfidenceDashboard to use global state for metrics
- [ ] Migrate AdvancedConfigPanel to use configuration hooks
- [ ] Update TransactionReview to use panel state hooks
- [ ] Remove all props drilling between these components
- [ ] Ensure configuration workflow functions correctly
- [ ] Test auto-parsing and manual configuration features

## Context

Week 3 component migration task focusing on the configuration and review workflow. This is one of the most complex component hierarchies in the application.

## Files to Modify

- `frontend/src/components/modern/ModernConfigureAndReviewStep.js`
- `frontend/src/components/modern/configure-review/AutoParseHandler.js`
- `frontend/src/components/modern/configure-review/ConfidenceDashboard.js`
- `frontend/src/components/modern/configure-review/AdvancedConfigPanel.js`
- `frontend/src/components/modern/configure-review/TransactionReview.js`

## Props to Remove

From ModernConfigureAndReviewStep:
- uploadedFiles, activeTab, setActiveTab, templates, loading
- updateFileConfig, updateColumnMapping, applyTemplate
- previewFile, parseAllFiles, parsedResults

From sub-components:
- All passed props that are now available through hooks

## Testing Requirements

- [ ] Auto-parsing triggers correctly
- [ ] Configuration dashboard displays accurate metrics
- [ ] Advanced configuration panel functions properly
- [ ] Transaction review shows correct data
- [ ] File expansion states work correctly
- [ ] Manual configuration overrides work
- [ ] Error states display appropriately

## Technical Notes

- Use React.memo to prevent unnecessary re-renders
- Implement proper dependency arrays for useEffect hooks
- Ensure proper cleanup of event listeners and timers
- Test with different data scenarios (success, error, empty)