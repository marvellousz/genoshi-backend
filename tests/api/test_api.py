"""
Integration tests for the FastAPI application.
"""
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models import ExtractedData

client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root(self):
        """Test the root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestHealthCheck:
    """Tests for the health check endpoint."""
    
    def test_health(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestValidateEndpoint:
    """Tests for the /validate endpoint."""
    
    def test_successful_validation(self):
        """Test successful document validation."""
        with patch('app.services.ai_extractor.AIExtractor.extract') as mock_extract:
            # Mock the AI extraction to return valid data
            mock_extract.return_value = {
                "policy_number": "HM-2025-10-A4B",
                "vessel_name": "MV Neptune",
                "policy_start_date": "2025-11-01",
                "policy_end_date": "2026-10-31",
                "insured_value": 5000000
            }
            
            response = client.post(
                "/api/v1/validate",
                json={"document_text": "Sample document text"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "extracted_data" in data
            assert "validation_results" in data
            assert len(data["validation_results"]) == 4
    
    def test_failed_validation(self):
        """Test document validation with failures."""
        with patch('app.services.ai_extractor.AIExtractor.extract') as mock_extract:
            # Mock the AI extraction to return invalid data
            mock_extract.return_value = {
                "policy_number": None,
                "vessel_name": "The Wanderer",
                "policy_start_date": "2026-01-01",
                "policy_end_date": "2025-12-31",
                "insured_value": -500
            }
            
            response = client.post(
                "/api/v1/validate",
                json={"document_text": "Sample document text"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "validation_results" in data
            # All validations should fail
            assert all(r["status"] == "FAIL" for r in data["validation_results"])
    
    def test_missing_document_text(self):
        """Test request without document_text."""
        response = client.post("/api/v1/validate", json={})
        assert response.status_code == 422  # Validation error
    
    def test_empty_document_text(self):
        """Test request with empty document_text."""
        response = client.post(
            "/api/v1/validate",
            json={"document_text": ""}
        )
        # Should still process but may fail validations
        assert response.status_code in [200, 503]  # 503 if AI fails
    
    def test_ai_service_failure(self):
        """Test handling of AI service failure."""
        with patch('app.services.ai_extractor.AIExtractor.extract') as mock_extract:
            from app.utils.exceptions import AIExtractorError
            mock_extract.side_effect = AIExtractorError("API key not configured")
            
            response = client.post(
                "/api/v1/validate",
                json={"document_text": "Sample document text"}
            )
            
            assert response.status_code == 503
            assert "AI service failed" in response.json()["detail"]
    
    def test_invalid_ai_response(self):
        """Test handling of invalid AI response format."""
        with patch('app.services.ai_extractor.AIExtractor.extract') as mock_extract:
            # Mock AI returning data with wrong types
            mock_extract.return_value = {
                "policy_number": "HM-2025-10-A4B",
                "vessel_name": "MV Neptune",
                "policy_start_date": "invalid-date",  # Invalid date format
                "policy_end_date": "2026-10-31",
                "insured_value": "not-a-number"  # Invalid type
            }
            
            response = client.post(
                "/api/v1/validate",
                json={"document_text": "Sample document text"}
            )
            
            # Should return 400 for schema validation error
            assert response.status_code == 400
            assert "invalid" in response.json()["detail"].lower()


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""
    
    def test_openapi_docs(self):
        """Test that OpenAPI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc(self):
        """Test that ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_json(self):
        """Test that OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema


@pytest.mark.integration
class TestEndToEndValidation:
    """End-to-end integration tests (require valid API key)."""
    
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here",
                        reason="Requires valid GROQ_API_KEY in .env file")
    def test_pass_document(self):
        """Test with the sample passing document."""
        with open("data/sample_document_pass.txt", "r") as f:
            document_text = f.read()
        
        response = client.post(
            "/api/v1/validate",
            json={"document_text": document_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "extracted_data" in data
        assert "validation_results" in data
        assert len(data["validation_results"]) == 4
    
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here",
                        reason="Requires valid GROQ_API_KEY in .env file")
    def test_fail_document(self):
        """Test with the sample failing document."""
        with open("data/sample_document_fail.txt", "r") as f:
            document_text = f.read()
        
        response = client.post(
            "/api/v1/validate",
            json={"document_text": document_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "extracted_data" in data
        assert "validation_results" in data
        assert len(data["validation_results"]) == 4

