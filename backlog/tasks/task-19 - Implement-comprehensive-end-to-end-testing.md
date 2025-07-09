---
id: task-19
title: Implement comprehensive end-to-end testing
status: Todo
assignee: []
created_date: '2025-07-09'
updated_date: '2025-07-09'
labels: [testing, e2e, automation]
dependencies: []
---

## Description

Implement a complete end-to-end test suite that validates the entire HisaabFlow application workflow from startup to export, ensuring reliability across all supported bank configurations and sample data.

## Background

The app has strong unit and integration testing foundation with pytest, but lacks comprehensive end-to-end testing that validates the complete user workflow. With multiple bank configurations and real sample data available, we need automated testing that ensures the entire pipeline works correctly.

## Requirements

### Core E2E Test Workflow
1. **App Startup Validation**
   - Start backend server and verify health endpoint
   - Validate all bank configurations load correctly
   - Check configuration integrity and completeness

2. **File Upload Testing**
   - Upload all CSV files from `sample_data/` directory
   - Test file validation and error handling
   - Verify file metadata extraction

3. **Parsing & Preview Testing**
   - Auto-detect bank configurations for each file
   - Parse CSV files using detected configurations
   - Preview data and validate structure

4. **Data Transformation Testing**
   - Transform parsed data to Cashew format
   - Apply transfer detection across multiple files
   - Validate currency handling and account mapping

5. **Export Testing**
   - Export final transformed data
   - Validate output format and completeness
   - Verify data integrity throughout pipeline

### Bank-Specific Testing

**Sample Data Coverage:**
- `12345678-00000000-87654321_2025-06-01_2025-06-30.csv` (Erste Bank)
- `statement_20141677_USD_2025-01-04_2025-06-02.csv` (Wise USD)
- `statement_23243482_EUR_2025-01-04_2025-06-02.csv` (Wise EUR)
- `m-02-2025.csv` (NayaPay)
- `account-statement_2024-04-01_2025-06-25_en-us_b9705c.csv` (Unknown bank)

**Configuration Testing:**
- Wise multi-currency support (USD, EUR, HUF)
- NayaPay PKR currency handling
- Erste Hungarian format processing
- Cross-bank transfer detection

### Error Handling & Edge Cases
- Invalid file formats and malformed CSVs
- Missing or incorrect bank configurations
- Network connectivity issues
- Data validation failures
- Transfer detection edge cases

## Technical Implementation

### Test Framework Strategy
- **Backend**: Extend existing pytest framework with FastAPI TestClient
- **Frontend**: Add Playwright or Cypress for full browser automation
- **Data Management**: Use existing sample data + create minimal test datasets
- **Environment**: Leverage existing virtual environment setup

### API Endpoint Coverage
Test complete workflow through existing endpoints:
- `POST /api/v1/upload` → File upload
- `GET /api/v1/configs` → Configuration loading
- `GET /api/v1/preview/{file_id}` → File preview
- `POST /api/v1/parse-range/{file_id}` → CSV parsing
- `POST /api/v1/multi-csv/parse` → Multi-file parsing
- `POST /api/v1/transform` → Data transformation
- `POST /api/v1/export` → Final export

### Test Data Strategy
- **Real Sample Data**: Use existing files for realistic testing
- **Synthetic Test Data**: Create minimal datasets for edge cases
- **Transfer Scenarios**: Generate known transfer pairs for detection validation
- **Multi-bank Datasets**: Test cross-bank transfer detection

## Implementation Tasks

### Phase 1: Framework Setup (1-2 days)
- [ ] Configure Playwright/Cypress for frontend automation
- [ ] Create test data management utilities
- [ ] Setup test environment isolation
- [ ] Integrate with existing pytest infrastructure

### Phase 2: Core Workflow Tests (3-4 days)
- [ ] Implement single bank full flow test
- [ ] Add multi-bank processing test
- [ ] Create transfer detection scenarios
- [ ] Test configuration loading and validation

### Phase 3: Bank-Specific Tests (2-3 days)
- [ ] Test each bank configuration individually
- [ ] Validate currency handling for each bank
- [ ] Test format-specific parsing rules
- [ ] Cross-bank transfer detection scenarios

### Phase 4: Error Handling & Edge Cases (2-3 days)
- [ ] Test malformed CSV handling
- [ ] Network failure simulation
- [ ] Configuration error scenarios
- [ ] Data validation edge cases

### Phase 5: CI/CD Integration (1-2 days)
- [ ] Integrate with existing pytest markers
- [ ] Configure automated test execution
- [ ] Setup coverage reporting
- [ ] Document test execution procedures

## Success Criteria

### Coverage Metrics
- **Code Coverage**: >90% for critical workflow paths
- **Bank Coverage**: All 4 bank configurations tested
- **Data Coverage**: All sample files successfully processed
- **API Coverage**: All workflow endpoints tested

### Quality Metrics
- **Reliability**: Tests pass consistently across environments
- **Performance**: Full E2E suite completes in <10 minutes
- **Maintainability**: Easy to update when features change
- **Documentation**: Clear test execution and debugging procedures

### Validation Criteria
- [ ] All sample data files process successfully end-to-end
- [ ] Transfer detection works across all bank combinations
- [ ] Error scenarios are properly handled and logged
- [ ] Export data matches expected format and completeness
- [ ] Tests run reliably in CI/CD environment

## Dependencies

- Existing pytest testing infrastructure
- FastAPI TestClient for backend testing
- Sample data files in `sample_data/` directory
- Bank configuration files in `configs/` directory
- Virtual environment setup (`backend/venv/`)

## Notes

This implementation builds on the existing strong testing foundation while adding comprehensive workflow validation. The focus is on testing real user scenarios with actual bank data rather than isolated unit tests.

The E2E tests will serve as regression protection and confidence validation for releases, ensuring that changes don't break the core user workflow across different bank configurations.