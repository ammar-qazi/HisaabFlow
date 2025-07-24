# Requirements Document

## Introduction

This feature addresses critical issues in the unknown bank configuration workflow that prevent proper bank detection updates, cause UI inconsistencies, and limit flexibility for banks with non-standard CSV structures. The improvements will enhance the user experience by automatically re-evaluating files after configuration creation, providing proper UI state management, and supporting flexible CSV parsing for banks like NayaPay that have headers in non-standard locations.

## Requirements

### Requirement 1

**User Story:** As a user who has just created a configuration for an unknown bank, I want the system to automatically re-evaluate all remaining unknown files to see if they now match the new configuration, so that I don't have to restart the application or manually configure each file individually.

#### Acceptance Criteria

1. WHEN a user successfully saves a new bank configuration THEN the system SHALL automatically trigger re-analysis of all remaining unknown files
2. WHEN the re-analysis completes THEN files that now match the new configuration SHALL be moved from unknown to known status
3. WHEN files are reclassified THEN the UI SHALL update to reflect the new file statuses without requiring a page refresh
4. WHEN multiple files belong to the same bank type THEN creating one configuration SHALL automatically resolve all matching files
5. IF re-analysis fails for any file THEN the system SHALL log the error and continue processing other files

### Requirement 2

**User Story:** As a user who has successfully configured an unknown bank, I want the Unknown Bank Panel to disappear and the file confidence scores to update properly, so that the UI accurately reflects the current state of my files.

#### Acceptance Criteria

1. WHEN a bank configuration is successfully created and applied THEN the Unknown Bank Panel SHALL hide if no unknown files remain
2. WHEN files are reclassified from unknown to known THEN their confidence scores SHALL update to reflect the new bank detection confidence
3. WHEN the Advanced Configuration panel displays file information THEN it SHALL show the correct confidence percentages for all files
4. WHEN the file list updates THEN the UI SHALL reflect changes immediately without requiring manual refresh
5. IF a file was previously unknown but now matches a configuration THEN it SHALL appear in the appropriate known bank section

### Requirement 3

**User Story:** As a user working with banks that have non-standard CSV structures (like NayaPay), I want to specify custom header row and data start row positions in the unknown bank configuration, so that I can properly configure banks with metadata or headers in non-standard locations.

#### Acceptance Criteria

1. WHEN configuring an unknown bank THEN the user SHALL be able to specify the header row number (1-based indexing)
2. WHEN configuring an unknown bank THEN the user SHALL be able to specify the data start row number (1-based indexing)
3. WHEN header row is specified THEN the system SHALL use that row to extract column headers for mapping
4. WHEN data start row is specified THEN the system SHALL begin data parsing from that row
5. WHEN analyzing CSV structure THEN the system SHALL provide intelligent suggestions for header and data start rows based on content analysis
6. WHEN preview data is displayed THEN it SHALL respect the specified header and data start row settings
7. IF header row or data start row values are invalid THEN the system SHALL provide clear error messages and fallback to defaults

### Requirement 4

**User Story:** As a user managing multiple unknown files, I want clear visual feedback about the re-analysis process and its results, so that I understand what's happening when configurations are applied to other files.

#### Acceptance Criteria

1. WHEN re-analysis begins THEN the system SHALL display a progress indicator showing the re-evaluation process
2. WHEN files are being re-analyzed THEN the UI SHALL show which files are currently being processed
3. WHEN re-analysis completes THEN the system SHALL display a summary of how many files were reclassified
4. WHEN files are successfully reclassified THEN the system SHALL provide visual confirmation of the changes
5. IF re-analysis encounters errors THEN the system SHALL display clear error messages with actionable guidance

### Requirement 5

**User Story:** As a user configuring unknown banks, I want the system to intelligently detect and suggest appropriate header and data start rows for complex CSV structures, so that I can quickly configure banks without manual trial and error.

#### Acceptance Criteria

1. WHEN analyzing a CSV file THEN the system SHALL scan the first 20 rows to identify potential header locations
2. WHEN potential headers are found THEN the system SHALL suggest the most likely header row based on content patterns
3. WHEN header row is identified THEN the system SHALL automatically suggest the appropriate data start row
4. WHEN CSV contains metadata or account information THEN the system SHALL skip these sections and identify actual transaction data
5. WHEN multiple potential header rows exist THEN the system SHALL provide options for the user to choose from
6. WHEN suggestions are made THEN the system SHALL explain the reasoning behind each suggestion