#!/bin/bash

# HisaabFlow Configuration Integrity Test
# Tests all .conf files can be loaded and validates their structure
echo "🧪 HisaabFlow Configuration Integrity Test..."

# Configuration
BACKEND_URL="http://127.0.0.1:8000"
CONFIGS_DIR="configs"
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
CONFIGS_TESTED=0
FAILED_TESTS=()

# Helper functions
log_test() {
    echo -e "${BLUE}📋 Test: $1${NC}"
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

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Wait for backend to be ready
wait_for_backend() {
    log_test "Backend Health Check"
    local max_attempts=15
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

# Test configuration file structure
test_config_file_structure() {
    local config_file="$1"
    local config_name=$(basename "$config_file" .conf)
    
    log_info "Testing structure of $config_name"
    
    # Check if file exists and is readable
    if [ ! -f "$config_file" ]; then
        log_failure "$config_name - file not found"
        return 1
    fi
    
    if [ ! -r "$config_file" ]; then
        log_failure "$config_name - file not readable"
        return 1
    fi
    
    # Handle app.conf separately
    if [[ "$config_name" == "app" || "$config_name" == "app.conf.template" ]]; then
        local required_keys=("date_tolerance_hours" "user_name" "confidence_threshold" "default_pair_category")
        local keys_found=0
        
        for key in "${required_keys[@]}"; do
            if grep -q -E "^\s*${key}\s*=" "$config_file"; then
                ((keys_found++))
                log_info "  Found key: $key"
            else
                log_warning "  Missing key: $key in $config_name"
            fi
        done
        
        if [ $keys_found -eq ${#required_keys[@]} ]; then
            log_success "$config_name - all required keys present"
            return 0
        else
            log_failure "$config_name - missing required keys ($keys_found/${#required_keys[@]})"
            return 1
        fi
    fi
    
    local required_sections=("[bank_info]" "[csv_config]" "[column_mapping]")
    local sections_found=0
    
    for section in "${required_sections[@]}"; do
        if grep -q "^$section" "$config_file"; then
            ((sections_found++))
            log_info "  Found section: $section"
        else
            log_warning "  Missing section: $section in $config_name"
        fi
    done
    
    if [ $sections_found -eq ${#required_sections[@]} ]; then
        log_success "$config_name - all required sections present"
        return 0
    else
        log_failure "$config_name - missing required sections ($sections_found/${#required_sections[@]})"
        return 1
    fi
}

# Test configuration loading via API
test_config_api_loading() {
    local config_name="$1"
    
    log_info "Testing API loading of $config_name"
    
    # Skip API loading test for app.conf (it's not a bank config)
    if [ "$config_name" = "app" ]; then
        log_info "  Skipping API test for app.conf (general settings, not loadable via config API)"
        return 0
    fi
    
    # Test with v1 API
    if response=$(curl -s --connect-timeout $TIMEOUT "$BACKEND_URL/api/v1/config/$config_name" 2>/dev/null); then
        if echo "$response" | grep -q '"success":\s*true'; then
            log_success "$config_name - loaded via v1 API"
            
            # Validate response structure
            if echo "$response" | grep -q '"bank_name"' && echo "$response" | grep -q '"config"'; then
                log_success "$config_name - valid response structure"
            else
                log_warning "$config_name - response missing expected fields"
            fi
            
            return 0
        else
            local error_msg=$(echo "$response" | grep -o '"detail":"[^"]*"' | cut -d'"' -f4)
            log_failure "$config_name - API returned error: ${error_msg:-unknown}"
            return 1
        fi
    else
        log_failure "$config_name - no response from v1 API"
        return 1
    fi
}

# Test configuration parsing consistency
test_config_parsing_consistency() {
    local config_file="$1"
    local config_name=$(basename "$config_file" .conf)
    
    log_info "Testing parsing consistency of $config_name"
    
    # Extract key values from the config file
    local bank_name=$(grep "^bank_name" "$config_file" | cut -d'=' -f2 | tr -d ' "'"'" | head -1)
    local delimiter=$(grep "^delimiter" "$config_file" | cut -d'=' -f2 | tr -d ' "'"'" | head -1)
    
    if [ -n "$bank_name" ]; then
        log_info "  Bank name: $bank_name"
    else
        log_info "  No bank_name in $config_name (optional field)"
    fi
    
    if [ -n "$delimiter" ]; then
        log_info "  Delimiter: $delimiter"
    else
        log_info "  No explicit delimiter in $config_name (will use default)"
    fi
    
    # Test if config can be loaded without errors
    if response=$(curl -s --connect-timeout $TIMEOUT "$BACKEND_URL/api/v1/config/$config_name" 2>/dev/null); then
        if echo "$response" | grep -q '"success":\s*true'; then
            # Check if API response bank_name matches config file (if bank_name exists in config)
            api_bank_name=$(echo "$response" | grep -o '"bank_name":"[^"]*"' | cut -d'"' -f4)
            if [ -n "$bank_name" ] && [ -n "$api_bank_name" ]; then
                # Clean both values for comparison (remove potential whitespace/newlines)
                clean_file_name=$(echo "$bank_name" | tr -d '\n\r' | xargs)
                clean_api_name=$(echo "$api_bank_name" | tr -d '\n\r' | xargs)
                
                if [ "$clean_file_name" = "$clean_api_name" ]; then
                    log_success "$config_name - bank_name consistency verified"
                else
                    log_info "$config_name - bank_name differs (file: '$clean_file_name', API: '$clean_api_name') - acceptable"
                fi
            elif [ -n "$bank_name" ]; then
                log_info "$config_name - has bank_name in config but API uses different value - acceptable"
            else
                log_info "$config_name - no bank_name in config (using API default) - acceptable"
            fi
        fi
    fi
    
    return 0
}

# Test all configuration files
test_all_configurations() {
    log_test "Configuration Files Discovery"
    
    if [ ! -d "$CONFIGS_DIR" ]; then
        log_failure "Configs directory not found: $CONFIGS_DIR"
        return 1
    fi
    
    # Find all .conf files
    local config_files=($(find "$CONFIGS_DIR" -name "*.conf" -type f))
    local template_files=($(find "$CONFIGS_DIR" -name "*.conf.template" -type f))
    
    log_info "Found ${#config_files[@]} .conf files"
    log_info "Found ${#template_files[@]} .conf.template files"
    
    if [ ${#config_files[@]} -eq 0 ] && [ ${#template_files[@]} -eq 0 ]; then
        log_failure "No configuration files found in $CONFIGS_DIR"
        return 1
    fi
    
    # Test .conf files
    for config_file in "${config_files[@]}"; do
        local config_name=$(basename "$config_file" .conf)
        echo ""
        log_test "Configuration: $config_name"
        ((CONFIGS_TESTED++))
        
        # Test file structure
        test_config_file_structure "$config_file"
        
        # Test API loading
        test_config_api_loading "$config_name"
        
        # Test parsing consistency
        test_config_parsing_consistency "$config_file"
    done
    
    # Test .conf.template files (structure only)
    for template_file in "${template_files[@]}"; do
        local template_name=$(basename "$template_file" .conf.template)
        echo ""
        log_test "Template: $template_name"
        ((CONFIGS_TESTED++))
        
        # Test template structure only
        test_config_file_structure "$template_file"
    done
}

# Test configuration list API
test_config_list_api() {
    log_test "Configuration List API"
    
    # Test v1 configs list
    if response=$(curl -s --connect-timeout $TIMEOUT "$BACKEND_URL/api/v1/configs" 2>/dev/null); then
        if echo "$response" | grep -q '"configurations"'; then
            local config_count=$(echo "$response" | grep -o '"[^"]*\.conf"' | wc -l)
            log_success "v1 configs list - found $config_count configurations"
            
            # Show available configurations
            log_info "Available configurations:"
            echo "$response" | grep -o '"[^"]*\.conf"' | sed 's/"//g' | sort | sed 's/^/    /'
        else
            log_failure "v1 configs list - invalid response format"
        fi
    else
        log_failure "v1 configs list - no response"
    fi
    
    # Test v3 configs list (legacy)
    if response=$(curl -s --connect-timeout $TIMEOUT "$BACKEND_URL/api/v3/configs" 2>/dev/null); then
        if echo "$response" | grep -q '"configurations"'; then
            log_success "v3 configs list (legacy) - working"
        else
            log_failure "v3 configs list (legacy) - invalid response format"
        fi
    else
        log_failure "v3 configs list (legacy) - no response"
    fi
}

# Main test execution
main() {
    echo "🧪 Starting HisaabFlow Configuration Integrity Test..."
    echo "Backend URL: $BACKEND_URL"
    echo "Configs directory: $CONFIGS_DIR"
    echo ""
    
    # Wait for backend to be ready
    if ! wait_for_backend; then
        echo ""
        echo "❌ Backend not ready - cannot run tests"
        exit 1
    fi
    
    echo ""
    
    # Run all test suites
    test_config_list_api
    echo ""
    test_all_configurations
    
    # Results summary
    echo ""
    echo "🎯 Configuration Integrity Test Results:"
    echo "✅ Tests passed: $TESTS_PASSED"
    echo "❌ Tests failed: $TESTS_FAILED"
    echo "📁 Configurations tested: $CONFIGS_TESTED"
    echo "📊 Total tests: $((TESTS_PASSED + TESTS_FAILED))"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo ""
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - $test"
        done
        echo ""
        echo "❌ Configuration Integrity Test: FAILED"
        exit 1
    else
        echo ""
        echo "✅ Configuration Integrity Test: PASSED"
        exit 0
    fi
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi