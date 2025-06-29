#!/bin/bash

# Comprehensive Integration Test Suite with Rollback Support
# Runs all integration tests in sequence with optional automated rollback
echo "🧪 HisaabFlow Comprehensive Integration Test Suite..."

# Check for rollback flag
ROLLBACK_ON_FAILURE=false
if [[ "$1" == "--rollback-on-failure" ]]; then
    ROLLBACK_ON_FAILURE=true
    echo "🔄 Rollback on failure: ENABLED"
    echo "⚠️  Will execute 'git reset --hard HEAD~1' if any test fails"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
FAILED_SUITES=()

# Function to handle failure with optional rollback
handle_failure() {
    local error_msg="$1"
    echo -e "${RED}❌ $error_msg${NC}"
    
    if [ "$ROLLBACK_ON_FAILURE" = true ]; then
        echo ""
        echo -e "${YELLOW}🔄 EXECUTING AUTOMATIC ROLLBACK...${NC}"
        echo "📝 Current commit before rollback:"
        git log --oneline -1
        echo ""
        
        # Execute rollback
        if git reset --hard HEAD~1; then
            echo -e "${GREEN}✅ Rollback completed successfully${NC}"
            echo "📝 Current commit after rollback:"
            git log --oneline -1
            echo ""
            echo -e "${BLUE}🎯 You can retry your changes after fixing the issue${NC}"
        else
            echo -e "${RED}❌ Rollback failed! Manual intervention required${NC}"
        fi
    fi
    
    exit 1
}

# Function to run a test suite
run_test_suite() {
    local test_name="$1"
    local test_command="$2"
    
    echo ""
    echo -e "${BLUE}📋 Running: $test_name${NC}"
    echo "Command: $test_command"
    echo ""
    
    ((TOTAL_TESTS++))
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name: PASSED${NC}"
        ((PASSED_TESTS++))
        return 0
    else
        echo -e "${RED}❌ $test_name: FAILED${NC}"
        ((FAILED_TESTS++))
        FAILED_SUITES+=("$test_name")
        return 1
    fi
}

# Function to check if backend is running
check_backend() {
    if curl -s --connect-timeout 5 http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Backend not running - some tests may be skipped${NC}"
        return 1
    fi
}

# Main test execution
main() {
    echo "🧪 Starting Comprehensive Integration Test Suite..."
    echo "Rollback on failure: $ROLLBACK_ON_FAILURE"
    echo ""
    
    # Check backend status
    BACKEND_RUNNING=false
    if check_backend; then
        BACKEND_RUNNING=true
    fi
    
    echo ""
    echo -e "${BLUE}📊 Test Suite Overview:${NC}"
    echo "1. Backend Integration Test"
    echo "2. API Coverage Test (requires backend)"
    echo "3. Configuration Integrity Test (requires backend)"
    echo "4. AppImage Integration Test (if available)"
    echo ""
    
    # Test 1: Backend Integration
    if run_test_suite "Backend Integration Test" "./test_backend_integration.sh"; then
        echo "  ✓ Backend import and startup verification"
    else
        handle_failure "Backend integration test failed - core functionality broken"
    fi
    
    # Test 2: API Coverage (only if backend is running)
    if [ "$BACKEND_RUNNING" = true ]; then
        if run_test_suite "API Coverage Test" "./test_api_coverage.sh"; then
            echo "  ✓ All API endpoints responding correctly"
        else
            handle_failure "API coverage test failed - API functionality broken"
        fi
    else
        echo -e "${YELLOW}⚠️  Skipping API Coverage Test - backend not running${NC}"
    fi
    
    # Test 3: Configuration Integrity (only if backend is running)
    if [ "$BACKEND_RUNNING" = true ]; then
        if run_test_suite "Configuration Integrity Test" "./test_config_integrity.sh"; then
            echo "  ✓ All configuration files loading correctly"
        else
            handle_failure "Configuration integrity test failed - config system broken"
        fi
    else
        echo -e "${YELLOW}⚠️  Skipping Configuration Integrity Test - backend not running${NC}"
    fi
    
    # Test 4: AppImage Integration (if AppImage exists)
    if [ -f "frontend/dist/HisaabFlow-1.0.0.AppImage" ]; then
        if run_test_suite "AppImage Integration Test" "./test_appimage_integration.sh"; then
            echo "  ✓ AppImage structure and bundling correct"
        else
            handle_failure "AppImage integration test failed - distribution package broken"
        fi
    else
        echo -e "${YELLOW}⚠️  Skipping AppImage Integration Test - AppImage not found${NC}"
    fi
    
    # Results summary
    echo ""
    echo "🎯 Comprehensive Integration Test Results:"
    echo "✅ Test suites passed: $PASSED_TESTS"
    echo "❌ Test suites failed: $FAILED_TESTS"
    echo "📊 Total test suites: $TOTAL_TESTS"
    
    if [ $FAILED_TESTS -gt 0 ]; then
        echo ""
        echo "Failed test suites:"
        for suite in "${FAILED_SUITES[@]}"; do
            echo "  - $suite"
        done
        echo ""
        handle_failure "Integration test suite failed - system not ready for refactoring"
    else
        echo ""
        echo -e "${GREEN}✅ All Integration Tests: PASSED${NC}"
        echo -e "${BLUE}🎯 System is ready for safe refactoring!${NC}"
        exit 0
    fi
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi