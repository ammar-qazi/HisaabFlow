"""
Test suite for API contract validation with strict response models
Tests that all endpoints return responses that match their Pydantic models
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.api.models import (
    UploadResponse, CleanupResponse, PreviewResponse, DetectRangeResponse,
    ParseResponse, MultiCSVResponse, ConfigListResponse, ConfigResponse,
    SaveConfigResponse, TransformResponse, ExportResponse
)
from pydantic import ValidationError
import tempfile
import os


@pytest.fixture
def client():
    """Create test client for API testing"""
    return TestClient(app)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing"""
    content = """Date,Amount,Description
2023-01-01,100.00,Test transaction
2023-01-02,-50.00,Another transaction
"""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_file.write(content)
    temp_file.close()
    yield temp_file.name
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except:
        pass


@pytest.mark.integration
class TestFileEndpointsContractValidation:
    """Test file endpoints return valid response models"""
    
    def test_upload_endpoint_response_model(self, client, sample_csv_file):
        """Test /upload endpoint returns valid UploadResponse model"""
        with open(sample_csv_file, 'rb') as f:
            response = client.post("/api/v1/upload", files={"file": f})
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches UploadResponse model
        try:
            upload_response = UploadResponse(**response_data)
            assert upload_response.success is True
            assert upload_response.file_id is not None
            assert upload_response.original_name is not None
            assert upload_response.size > 0
        except ValidationError as e:
            pytest.fail(f"Upload response validation failed: {e}")
    
    def test_cleanup_endpoint_response_model(self, client, sample_csv_file):
        """Test /cleanup endpoint returns valid CleanupResponse model"""
        # First upload a file
        with open(sample_csv_file, 'rb') as f:
            upload_response = client.post("/api/v1/upload", files={"file": f})
        file_id = upload_response.json()["file_id"]
        
        # Then cleanup
        response = client.delete(f"/api/v1/cleanup/{file_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches CleanupResponse model
        try:
            cleanup_response = CleanupResponse(**response_data)
            assert cleanup_response.success is True
        except ValidationError as e:
            pytest.fail(f"Cleanup response validation failed: {e}")


@pytest.mark.integration
class TestConfigEndpointsContractValidation:
    """Test config endpoints return valid response models"""
    
    def test_list_configs_endpoint_response_model(self, client):
        """Test /configs endpoint returns valid ConfigListResponse model"""
        response = client.get("/api/v1/configs")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches ConfigListResponse model
        try:
            config_list_response = ConfigListResponse(**response_data)
            assert isinstance(config_list_response.configurations, list)
            assert isinstance(config_list_response.raw_bank_names, list)
            assert isinstance(config_list_response.count, int)
        except ValidationError as e:
            pytest.fail(f"Config list response validation failed: {e}")
    
    def test_load_config_endpoint_response_model(self, client):
        """Test /config/{config_name} endpoint returns valid ConfigResponse model"""
        # First get available configs
        configs_response = client.get("/api/v1/configs")
        configs = configs_response.json()
        
        if configs["count"] > 0:
            config_name = configs["raw_bank_names"][0]
            response = client.get(f"/api/v1/config/{config_name}")
            
            assert response.status_code == 200
            response_data = response.json()
            
            # Validate response matches ConfigResponse model
            try:
                config_response = ConfigResponse(**response_data)
                assert config_response.success is True
                assert config_response.config is not None
                assert config_response.bank_name is not None
                assert config_response.display_name is not None
                assert config_response.source is not None
            except ValidationError as e:
                pytest.fail(f"Config response validation failed: {e}")
    
    def test_save_config_endpoint_response_model(self, client):
        """Test /save-config endpoint returns valid SaveConfigResponse model"""
        request_data = {
            "template_name": "test_bank",
            "config": {
                "bank_name": "Test Bank",
                "currency": "USD",
                "account": "Test Account"
            }
        }
        
        response = client.post("/api/v1/save-config", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches SaveConfigResponse model
        try:
            save_config_response = SaveConfigResponse(**response_data)
            assert save_config_response.success is True
            assert save_config_response.message is not None
            assert save_config_response.config_file is not None
            assert save_config_response.suggestion is not None
        except ValidationError as e:
            pytest.fail(f"Save config response validation failed: {e}")


@pytest.mark.integration
class TestParseEndpointsContractValidation:
    """Test parse endpoints return valid response models"""
    
    def test_preview_endpoint_response_model(self, client, sample_csv_file):
        """Test /preview/{file_id} endpoint returns valid PreviewResponse model"""
        # Upload file first
        with open(sample_csv_file, 'rb') as f:
            upload_response = client.post("/api/v1/upload", files={"file": f})
        file_id = upload_response.json()["file_id"]
        
        response = client.get(f"/api/v1/preview/{file_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches PreviewResponse model
        try:
            preview_response = PreviewResponse(**response_data)
            assert preview_response.success is True
            assert isinstance(preview_response.column_names, list)
            assert isinstance(preview_response.preview_data, list)
            assert isinstance(preview_response.total_rows, int)
            assert preview_response.bank_detection is not None
            assert isinstance(preview_response.encoding_used, str)
            assert isinstance(preview_response.parsing_info, dict)
        except ValidationError as e:
            pytest.fail(f"Preview response validation failed: {e}")
    
    def test_detect_range_endpoint_response_model(self, client, sample_csv_file):
        """Test /detect-range/{file_id} endpoint returns valid DetectRangeResponse model"""
        # Upload file first
        with open(sample_csv_file, 'rb') as f:
            upload_response = client.post("/api/v1/upload", files={"file": f})
        file_id = upload_response.json()["file_id"]
        
        response = client.get(f"/api/v1/detect-range/{file_id}")
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches DetectRangeResponse model
        try:
            detect_range_response = DetectRangeResponse(**response_data)
            assert detect_range_response.success is True
            assert isinstance(detect_range_response.suggested_header_row, int)
            assert isinstance(detect_range_response.total_rows, int)
            assert isinstance(detect_range_response.confidence, float)
        except ValidationError as e:
            pytest.fail(f"Detect range response validation failed: {e}")
    
    def test_parse_range_endpoint_response_model(self, client, sample_csv_file):
        """Test /parse-range/{file_id} endpoint returns valid ParseResponse model"""
        # Upload file first
        with open(sample_csv_file, 'rb') as f:
            upload_response = client.post("/api/v1/upload", files={"file": f})
        file_id = upload_response.json()["file_id"]
        
        request_data = {
            "start_row": 1,
            "end_row": None,
            "start_col": 0,
            "end_col": None,
            "encoding": "utf-8",
            "enable_cleaning": True
        }
        
        response = client.post(f"/api/v1/parse-range/{file_id}", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches ParseResponse model
        try:
            parse_response = ParseResponse(**response_data)
            assert parse_response.success is True
            assert isinstance(parse_response.headers, list)
            assert isinstance(parse_response.data, list)
            assert isinstance(parse_response.row_count, int)
        except ValidationError as e:
            pytest.fail(f"Parse response validation failed: {e}")


@pytest.mark.integration
class TestTransformEndpointsContractValidation:
    """Test transform endpoints return valid response models"""
    
    def test_transform_endpoint_response_model(self, client):
        """Test /transform endpoint returns valid TransformResponse model"""
        request_data = {
            "data": [
                {"date": "2023-01-01", "amount": 100.0, "description": "Test"},
                {"date": "2023-01-02", "amount": -50.0, "description": "Another"}
            ],
            "column_mapping": {
                "date": "Date",
                "amount": "Amount", 
                "description": "Description"
            },
            "bank_name": "test_bank"
        }
        
        response = client.post("/api/v1/transform", json=request_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Validate response matches TransformResponse model
        try:
            transform_response = TransformResponse(**response_data)
            assert transform_response.success is True
            assert isinstance(transform_response.data, list)
            assert isinstance(transform_response.row_count, int)
        except ValidationError as e:
            pytest.fail(f"Transform response validation failed: {e}")


@pytest.mark.integration
class TestStrictTypeValidation:
    """Test that strict type validation catches malformed responses"""
    
    def test_response_model_validation_catches_errors(self):
        """Test that response model validation catches type errors"""
        # Test invalid UploadResponse
        invalid_upload_data = {
            "success": "true",  # Should be bool, not string
            "file_id": 123,     # Should be string, not int
            "original_name": None,  # Should be string, not None
            "size": "large"     # Should be int, not string
        }
        
        with pytest.raises(ValidationError):
            UploadResponse(**invalid_upload_data)
    
    def test_union_type_validation_works(self):
        """Test that Union types in data fields work correctly"""
        # Test valid Union[str, int, float] data
        valid_data = [
            {"name": "John", "age": 30, "salary": 50000.0},
            {"name": "Jane", "age": 25, "salary": 60000}
        ]
        
        valid_response_data = {
            "success": True,
            "data": valid_data,
            "row_count": 2
        }
        
        # Should not raise ValidationError
        transform_response = TransformResponse(**valid_response_data)
        assert transform_response.success is True
        assert len(transform_response.data) == 2
        assert transform_response.row_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])