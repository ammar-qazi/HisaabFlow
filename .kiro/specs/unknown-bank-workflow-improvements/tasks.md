# Implementation Plan

## Phase 1: Header Row Configuration Support

- [x] 1. Enhance CSV structure analysis for flexible header detection
  - Implement intelligent header row detection algorithm that scans first 20 rows
  - Add support for 1-based indexing in user interface while maintaining 0-based backend processing
  - Create header suggestion engine that identifies potential header rows based on content patterns
  - Add validation for header row configuration to ensure data integrity
  - _Requirements: 3.1, 3.2, 3.3, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [x] 2. Update backend unknown bank service for header row configuration
  - Modify CSV analysis to accept and process header_row parameter (convert 1-based to 0-based internally)
  - Update bank configuration generation to include header_row in csv_config section
  - Add validation logic to ensure header_row is within valid range for CSV file
  - Update configuration file writing to include header_row parameter
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 3. Enhance backend CSV parsing to support configurable header rows
  - Update UnifiedCSVParser to accept header_row parameter
  - Modify parsing logic to use specified header row for column extraction
  - Add validation to ensure header_row is within file bounds
  - Update error handling for invalid header row configurations
  - _Requirements: 3.1, 3.2, 3.4, 3.7_

- [x] 4. Enhance UnknownBankPanel with header row configuration
  - Add header row input field with 1-based indexing for user display
  - Implement header row suggestion display with confidence scores and reasoning
  - Add preview functionality that shows how CSV will be parsed with selected header row
  - Create validation to ensure selected header row contains valid column names
  - Update sample data preview to respect configured header row
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7_

- [x] 5. Update configuration file format and validation
  - Add header_row field to configuration file template
  - Update configuration validation to check header_row parameter
  - Add migration logic for existing configurations without header_row
  - Create documentation for new configuration options
  - _Requirements: 3.1, 3.2, 3.7_

- [x] 6. Test header row functionality with NayaPay CSV
  - Create unit tests for header row detection and suggestion algorithms
  - Test NayaPay CSV configuration with header row 13
  - Add validation tests for various header row configurations
  - Test error handling for invalid header row values
  - _Requirements: 3.1, 3.2, 3.3, 3.7_

## Phase 2: File Re-evaluation Workflow

- [ ] 7. Create file re-evaluation service for automatic bank detection updates
  - Implement FileReEvaluationService class with methods for re-analyzing unknown files
  - Add API endpoint POST /api/v1/unknown-bank/re-evaluate-files for triggering re-evaluation
  - Create logic to update file classifications from unknown to known status
  - Implement error handling for partial re-evaluation failures
  - Add progress tracking for re-evaluation process
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 8. Update configuration service for re-evaluation support
  - Add reEvaluateUnknownFiles method to ConfigurationService
  - Implement file status tracking and confidence score updates
  - Add support for header_row parameter in configuration loading and saving
  - Create utility methods for converting between 1-based and 0-based indexing
  - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2_

- [ ] 9. Implement automatic file re-evaluation workflow
  - Modify saveConfiguration method to trigger re-evaluation of remaining unknown files
  - Add re-evaluation progress indicator component with file processing status
  - Implement UI updates for file status changes (unknown to known)
  - Add confidence score updates for reclassified files
  - Create logic to hide UnknownBankPanel when no unknown files remain
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3, 4.4_

- [ ] 10. Update file state management and UI synchronization
  - Implement FileStateManager for centralized file status tracking
  - Add logic to update file confidence scores in real-time
  - Create methods to remove files from unknown list when reclassified
  - Update UI components to reflect file status changes immediately
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 11. Add visual feedback and progress indicators
  - Create ReEvaluationProgressIndicator component for showing re-evaluation status
  - Add loading states and progress bars for file processing
  - Implement success/error notifications for re-evaluation results
  - Add visual confirmation when files are reclassified from unknown to known
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 12. Create comprehensive error handling for re-evaluation process
  - Implement error recovery strategies for parsing failures and network errors
  - Add detailed error reporting for failed re-evaluations
  - Create user-friendly error messages with actionable guidance
  - Add logging for debugging re-evaluation issues
  - _Requirements: 1.5, 4.4_

- [ ] 13. Write comprehensive tests for re-evaluation functionality
  - Add integration tests for complete re-evaluation workflow
  - Add performance tests for re-evaluation with multiple files
  - Create error handling tests for various failure scenarios
  - Test UI state updates during re-evaluation process
  - _Requirements: All Phase 2 requirements validation_
