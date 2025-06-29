#!/bin/bash

# HisaabFlow API Endpoint Coverage Test
# Tests all critical API endpoints to ensure functionality during refactoring
echo "🧪 HisaabFlow API Endpoint Coverage Test..."

# Configuration
BACKEND_URL="http://127.0.0.1:8000"
TEST_CSV_PATH="sample_data/statement_20141677_USD_2025-01-04_2025-06-02.csv"
TIMEOUT=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Helper functions
log_test() {
    echo "📋 Test: $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_failure() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
    FAILED_TESTS+=("$1")
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Wait for backend to be ready
wait_for_backend() {
    log_test "Backend Health Check"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s --connect-timeout 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
            log_success "Backend is ready"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - waiting for backend..."
        sleep 2
        ((attempt++))
    done
    
    log_failure "Backend not responding after $max_attempts attempts"
    return 1
}

# Test basic endpoints
test_basic_endpoints() {
    log_test "Basic Endpoints"
    
    # Test root endpoint
    if response=$(curl -s --connect-timeout 5 "$BACKEND_URL/"); then
        if echo "$response" | grep -q "Bank Statement Parser"; then
            log_success "Root endpoint (/)"
        else
            log_failure "Root endpoint (/) - invalid response"
        fi
    else
        log_failure "Root endpoint (/) - no response"
    fi
    
    # Test health endpoint
    if response=$(curl -s --connect-timeout 5 "$BACKEND_URL/health"); then
        if echo "$response" | grep -q "healthy"; then
            log_success "Health endpoint (/health)"
        else
            log_failure "Health endpoint (/health) - invalid response"
        fi
    else
        log_failure "Health endpoint (/health) - no response"
    fi
}

# Test configuration endpoints
test_config_endpoints() {
    log_test "Configuration Endpoints"
    
    # Test list configs
    if response=$(curl -s --connect-timeout 5 "$BACKEND_URL/api/v1/configs"); then
        if echo "$response" | grep -q "configurations"; then
            log_success "List configs (/api/v1/configs)"
        else
            log_failure "List configs (/api/v1/configs) - invalid response"
        fi
    else
        log_failure "List configs (/api/v1/configs) - no response"
    fi
    
    # Test load specific config (try a common one)
    if response=$(curl -s --connect-timeout 5 "$BACKEND_URL/api/v1/config/wise_personal"); then
        if echo "$response" | grep -q "success"; then
            log_success "Load config (/api/v1/config/wise_personal)"
        else
            log_warning "Load config (/api/v1/config/wise_personal) - may not exist"
        fi
    else
        log_failure "Load config (/api/v1/config/wise_personal) - no response"
    fi
    
    # Test legacy v3 config endpoint
    if response=$(curl -s --connect-timeout 5 "$BACKEND_URL/api/v3/configs"); then
        if echo "$response" | grep -q "configurations"; then
            log_success "Legacy v3 configs (/api/v3/configs)"
        else
            log_failure "Legacy v3 configs (/api/v3/configs) - invalid response"
        fi
    else
        log_failure "Legacy v3 configs (/api/v3/configs) - no response"
    fi
}

# Test file endpoints
test_file_endpoints() {
    log_test "File Management Endpoints"
    
    # Use existing sample data
    if [ ! -f "$TEST_CSV_PATH" ]; then
        # Try other sample files if the primary one doesn't exist
        for sample_file in sample_data/*.csv; do
            if [ -f "$sample_file" ]; then
                TEST_CSV_PATH="$sample_file"
                log_warning "Using alternative sample file: $TEST_CSV_PATH"
                break
            fi
        done
        
        if [ ! -f "$TEST_CSV_PATH" ]; then
            log_failure "No sample CSV files found for testing"
            return 1
        fi
    fi
    
    # Test file upload
    if [ -f "$TEST_CSV_PATH" ]; then
        if response=$(curl -s --connect-timeout 10 -X POST -F "file=@$TEST_CSV_PATH" "$BACKEND_URL/api/v1/upload"); then
            if echo "$response" | grep -q "file_id"; then
                file_id=$(echo "$response" | grep -o '"file_id":"[^"]*"' | cut -d'"' -f4)
                log_success "File upload (/api/v1/upload) - file_id: $file_id"
                
                # Store file_id for other tests
                echo "$file_id" > /tmp/test_file_id
            else
                log_failure "File upload (/api/v1/upload) - no file_id in response"
            fi
        else
            log_failure "File upload (/api/v1/upload) - no response"
        fi
    else
        log_failure "File upload - test CSV not found"
    fi
}

# Test parsing endpoints
test_parse_endpoints() {
    log_test "Parsing Endpoints"
    
    # Get file_id from upload test
    if [ -f "/tmp/test_file_id" ]; then
        file_id=$(cat /tmp/test_file_id)
        
        # Test preview endpoint
        if response=$(curl -s --connect-timeout 10 "$BACKEND_URL/api/v1/preview/$file_id"); then
            if echo "$response" | grep -q "column_names"; then
                log_success "File preview (/api/v1/preview/$file_id)"
            else
                log_failure "File preview (/api/v1/preview/$file_id) - invalid response"
            fi
        else
            log_failure "File preview (/api/v1/preview/$file_id) - no response"
        fi
        
        # Test detect range endpoint
        if response=$(curl -s --connect-timeout 10 "$BACKEND_URL/api/v1/detect-range/$file_id"); then
            if echo "$response" | grep -q "start_row\|suggested_header_row"; then
                log_success "Detect range (/api/v1/detect-range/$file_id)"
            else
                log_failure "Detect range (/api/v1/detect-range/$file_id) - invalid response"
            fi
        else
            log_failure "Detect range (/api/v1/detect-range/$file_id) - no response"
        fi
        
        # Test parse range endpoint with basic config
        parse_config='{"start_row": 1, "end_row": null, "start_col": 0, "end_col": null, "encoding": "utf-8"}'
        if response=$(curl -s --connect-timeout 10 -X POST -H "Content-Type: application/json" -d "$parse_config" "$BACKEND_URL/api/v1/parse-range/$file_id"); then
            if echo "$response" | grep -q "headers\|data"; then
                log_success "Parse range (/api/v1/parse-range/$file_id)"
            else
                log_failure "Parse range (/api/v1/parse-range/$file_id) - invalid response"
            fi
        else
            log_failure "Parse range (/api/v1/parse-range/$file_id) - no response"
        fi
        
    else
        log_warning "Skipping parse tests - no file_id available"
    fi
}

# Test transformation endpoints
test_transform_endpoints() {
    log_test "Transformation Endpoints"
    
    # Test basic transform endpoint with minimal data
    transform_data='{
        "data": [
            {"Date": "2024-01-01", "Description": "Test", "Amount": "100.00"}
        ],
        "column_mapping": {
            "Date": "date",
            "Description": "description", 
            "Amount": "amount"
        },
        "bank_name": "test_bank"
    }'
    
    if response=$(curl -s --connect-timeout 10 -X POST -H "Content-Type: application/json" -d "$transform_data" "$BACKEND_URL/api/v1/transform"); then
        if echo "$response" | grep -q "success\|data"; then
            log_success "Transform data (/api/v1/transform)"
        else
            log_failure "Transform data (/api/v1/transform) - invalid response"
        fi
    else
        log_failure "Transform data (/api/v1/transform) - no response"
    fi
}

# Test critical desktop endpoints
test_desktop_endpoints() {
    log_test "Critical Desktop App Endpoints"
    
    # Test health endpoint (critical for desktop app)
    if response=$(curl -s --connect-timeout 5 "$BACKEND_URL/health"); then
        if echo "$response" | grep -q "healthy\|status"; then
            log_success "Desktop health check (/health)"
        else
            log_failure "Desktop health check (/health) - invalid response"
        fi
    else
        log_failure "Desktop health check (/health) - no response"
    fi
    
    # Note: We don't test /shutdown endpoint as it would stop the server
    log_warning "Shutdown endpoint (/shutdown) not tested - would terminate backend"
}

# Test API versioning consistency
test_api_versioning() {
    log_test "API Versioning Consistency"
    
    # Test v1 vs v3 config endpoints return similar data
    v1_response=$(curl -s --connect-timeout 5 "$BACKEND_URL/api/v1/configs" 2>/dev/null)
    v3_response=$(curl -s --connect-timeout 5 "$BACKEND_URL/api/v3/configs" 2>/dev/null)
    
    if [ -n "$v1_response" ] && [ -n "$v3_response" ]; then
        # Basic check that both return configuration data
        if echo "$v1_response" | grep -q "configurations" && echo "$v3_response" | grep -q "configurations"; then
            log_success "API versioning consistency (v1 and v3 both respond)"
        else
            log_failure "API versioning consistency - different response formats"
        fi
    else
        log_failure "API versioning consistency - one or both endpoints failed"
    fi
}

# Cleanup function
cleanup() {
    log_test "Cleanup"
    
    # Clean up test files
    if [ -f "/tmp/test_file_id" ]; then
        rm -f "/tmp/test_file_id"
        log_success "Cleaned up temporary test files"
    fi
    
    # Note: We don't clean up uploaded files as the backend should handle that
}

# Main test execution
main() {
    echo "🧪 Starting HisaabFlow API Coverage Test..."
    echo "Backend URL: $BACKEND_URL"
    echo "Test CSV: $TEST_CSV_PATH"
    echo ""
    
    # Wait for backend to be ready
    if ! wait_for_backend; then
        echo ""
        echo "❌ Backend not ready - cannot run tests"
        exit 1
    fi
    
    echo ""
    
    # Run all test suites
    test_basic_endpoints
    echo ""
    test_config_endpoints
    echo ""
    test_file_endpoints
    echo ""
    test_parse_endpoints
    echo ""
    test_transform_endpoints
    echo ""
    test_desktop_endpoints
    echo ""
    test_api_versioning
    echo ""
    
    # Cleanup
    cleanup
    
    # Results summary
    echo ""
    echo "🎯 API Coverage Test Results:"
    echo "✅ Tests passed: $TESTS_PASSED"
    echo "❌ Tests failed: $TESTS_FAILED"
    echo "📊 Total tests: $((TESTS_PASSED + TESTS_FAILED))"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo ""
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
        echo ""
        echo "❌ API Coverage Test: FAILED"
        exit 1
    else
        echo ""
        echo "✅ API Coverage Test: PASSED"
        exit 0
    fi
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi