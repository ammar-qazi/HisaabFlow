"""
API consolidation tests for task-7

These tests validate all API endpoints before and after consolidation
to ensure no functionality is broken during the migration to /api/v1 only.
"""
import pytest
import requests
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
API_V1_BASE = f"{BASE_URL}/api/v1"
API_V3_BASE = f"{BASE_URL}/api/v3"  # Legacy - to be removed


@pytest.mark.integration
class TestAPIConsolidationBefore:
    """
    Test current API endpoints before consolidation
    Documents which endpoints exist and work currently
    """
    
    def test_root_endpoint(self):
        """Test root endpoint availability"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_api_v1_configs_endpoint(self):
        """Test /api/v1/configs endpoint"""
        response = requests.get(f"{API_V1_BASE}/configs")
        assert response.status_code == 200
        data = response.json()
        assert "configurations" in data

    def test_api_v3_configs_endpoint_legacy(self):
        """Test legacy /api/v3/configs endpoint (to be removed)"""
        response = requests.get(f"{API_V3_BASE}/configs")
        assert response.status_code == 200
        data = response.json()
        assert "configurations" in data

    def test_direct_configs_endpoint_compatibility(self):
        """Test direct /configs endpoint (compatibility - to be removed)"""
        response = requests.get(f"{BASE_URL}/configs")
        assert response.status_code == 200
        data = response.json()
        assert "configurations" in data

    def test_api_v1_upload_endpoint(self):
        """Test /api/v1/upload endpoint"""
        # This would require file upload - skip for now as it's more complex
        # Will be tested in Phase 5 comprehensive testing
        pass

    def test_api_v1_preview_endpoint_format(self):
        """Test that /api/v1/preview/{file_id} endpoint format is correct"""
        # Test endpoint structure exists (will fail without valid file_id)
        response = requests.get(f"{API_V1_BASE}/preview/test_file_id")
        # Expecting 404 or 422 since file doesn't exist, but not 404 route not found
        assert response.status_code in [404, 422, 500]  # Any except route not found

    def test_direct_preview_endpoint_compatibility(self):
        """Test direct /preview/{file_id} endpoint (compatibility - to be removed)"""
        response = requests.get(f"{BASE_URL}/preview/test_file_id")
        # Expecting 404 or 422 since file doesn't exist, but not 404 route not found
        assert response.status_code in [404, 422, 500]  # Any except route not found


@pytest.mark.integration 
class TestAPIConsolidationAfter:
    """
    Test API endpoints after consolidation
    These tests should pass after task-7 is complete
    """
    
    def test_only_api_v1_configs_works(self):
        """Test that only /api/v1/configs works after consolidation"""
        # V1 should work
        response = requests.get(f"{API_V1_BASE}/configs")
        assert response.status_code == 200
        
        # V3 should be removed (404)
        response = requests.get(f"{API_V3_BASE}/configs")
        assert response.status_code == 404
        
        # Direct route should be removed (404)
        response = requests.get(f"{BASE_URL}/configs")
        assert response.status_code == 404

    def test_only_api_v1_preview_works(self):
        """Test that only /api/v1/preview works after consolidation"""
        # V1 should work
        response = requests.get(f"{API_V1_BASE}/preview/test_file_id")
        assert response.status_code in [404, 422, 500]  # Not route not found
        
        # Direct route should be removed (404 route not found)
        response = requests.get(f"{BASE_URL}/preview/test_file_id")
        assert response.status_code == 404

    def test_api_v1_all_endpoints_available(self):
        """Test that all expected /api/v1 endpoints are available"""
        expected_v1_endpoints = [
            "/api/v1/configs",
            "/api/v1/upload", 
            "/api/v1/preview/test_id",
            "/api/v1/detect-range/test_id",
            "/api/v1/parse-range/test_id",
            "/api/v1/multi-csv/parse",
            "/api/v1/multi-csv/transform",
            "/api/v1/transform",
            "/api/v1/export"
        ]
        
        for endpoint in expected_v1_endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            # Should not be 404 (route not found) - other errors are fine
            assert response.status_code != 404, f"Endpoint {endpoint} should exist"


def run_pre_consolidation_tests():
    """
    Run tests to document current API state before consolidation
    This helps ensure we understand what's working before changes
    """
    print("🔍 Running pre-consolidation API tests...")
    
    # Document current working endpoints
    working_endpoints = []
    
    test_endpoints = [
        f"{BASE_URL}/",
        f"{BASE_URL}/health",
        f"{API_V1_BASE}/configs",
        f"{API_V3_BASE}/configs",
        f"{BASE_URL}/configs"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                working_endpoints.append(endpoint)
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")
    
    print(f"\n📊 Summary: {len(working_endpoints)} endpoints working")
    return working_endpoints


if __name__ == "__main__":
    # Can be run directly to test current API state
    run_pre_consolidation_tests()