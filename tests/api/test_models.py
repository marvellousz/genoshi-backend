"""
Unit tests for Pydantic models.
"""
import pytest
from datetime import date
from pydantic import ValidationError
from app.models import (
    DocumentRequest,
    ExtractedData,
    ValidationResult,
    ValidationResponse
)


class TestDocumentRequest:
    """Tests for DocumentRequest model."""
    
    def test_valid_request(self):
        """Test creating a valid DocumentRequest."""
        request = DocumentRequest(document_text="Sample document text")
        assert request.document_text == "Sample document text"
    
    def test_missing_document_text(self):
        """Test that document_text is required."""
        with pytest.raises(ValidationError):
            DocumentRequest()
    
    def test_empty_document_text(self):
        """Test with empty document_text (should be valid)."""
        request = DocumentRequest(document_text="")
        assert request.document_text == ""


class TestExtractedData:
    """Tests for ExtractedData model."""
    
    def test_all_fields_present(self):
        """Test creating ExtractedData with all fields."""
        data = ExtractedData(
            policy_number="HM-2025-10-A4B",
            vessel_name="MV Neptune",
            policy_start_date=date(2025, 11, 1),
            policy_end_date=date(2026, 10, 31),
            insured_value=5000000
        )
        assert data.policy_number == "HM-2025-10-A4B"
        assert data.vessel_name == "MV Neptune"
        assert data.insured_value == 5000000
    
    def test_all_fields_none(self):
        """Test creating ExtractedData with all None values."""
        data = ExtractedData()
        assert data.policy_number is None
        assert data.vessel_name is None
        assert data.policy_start_date is None
        assert data.policy_end_date is None
        assert data.insured_value is None
    
    def test_date_parsing(self):
        """Test date parsing from string."""
        data = ExtractedData(
            policy_start_date="2025-11-01",
            policy_end_date="2026-10-31"
        )
        assert isinstance(data.policy_start_date, date)
        assert isinstance(data.policy_end_date, date)
    
    def test_invalid_date_format(self):
        """Test that invalid date format raises error."""
        with pytest.raises(ValidationError):
            ExtractedData(policy_start_date="11-01-2025")  # Wrong format
    
    def test_negative_insured_value(self):
        """Test that negative insured value is accepted (validation happens later)."""
        data = ExtractedData(insured_value=-500)
        assert data.insured_value == -500
    
    def test_invalid_insured_value_type(self):
        """Test that non-integer insured value raises error."""
        with pytest.raises(ValidationError):
            ExtractedData(insured_value="not-a-number")


class TestValidationResult:
    """Tests for ValidationResult model."""
    
    def test_pass_result(self):
        """Test creating a PASS validation result."""
        result = ValidationResult(
            rule="Date Consistency",
            status="PASS",
            message="Policy end date is after start date."
        )
        assert result.rule == "Date Consistency"
        assert result.status == "PASS"
    
    def test_fail_result(self):
        """Test creating a FAIL validation result."""
        result = ValidationResult(
            rule="Value Check",
            status="FAIL",
            message="Insured value must be positive."
        )
        assert result.status == "FAIL"
    
    def test_missing_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            ValidationResult(rule="Test", status="PASS")


class TestValidationResponse:
    """Tests for ValidationResponse model."""
    
    def test_complete_response(self):
        """Test creating a complete ValidationResponse."""
        extracted_data = ExtractedData(
            policy_number="HM-2025-10-A4B",
            vessel_name="MV Neptune",
            policy_start_date=date(2025, 11, 1),
            policy_end_date=date(2026, 10, 31),
            insured_value=5000000
        )
        
        validation_results = [
            ValidationResult(
                rule="Date Consistency",
                status="PASS",
                message="Policy end date is after start date."
            ),
            ValidationResult(
                rule="Value Check",
                status="PASS",
                message="Insured value is valid."
            )
        ]
        
        response = ValidationResponse(
            extracted_data=extracted_data,
            validation_results=validation_results
        )
        
        assert response.extracted_data.policy_number == "HM-2025-10-A4B"
        assert len(response.validation_results) == 2
        assert all(r.status == "PASS" for r in response.validation_results)
    
    def test_empty_validation_results(self):
        """Test response with empty validation results."""
        response = ValidationResponse(
            extracted_data=ExtractedData(),
            validation_results=[]
        )
        assert len(response.validation_results) == 0

