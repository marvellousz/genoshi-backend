import pytest
from datetime import date
from app.models import ExtractedData, ValidationResult
from app.services.validator import DocumentValidator


validator = DocumentValidator()


class TestDateConsistency:
    
    def test_valid_dates(self):
        data = ExtractedData(
            policy_start_date=date(2025, 1, 1),
            policy_end_date=date(2026, 1, 1)
        )
        result = validator._validate_dates(data)
        assert result.status == "PASS"
    
    def test_end_before_start(self):
        data = ExtractedData(
            policy_start_date=date(2026, 1, 1),
            policy_end_date=date(2025, 1, 1)
        )
        result = validator._validate_dates(data)
        assert result.status == "FAIL"
    
    def test_same_dates(self):
        data = ExtractedData(
            policy_start_date=date(2025, 1, 1),
            policy_end_date=date(2025, 1, 1)
        )
        result = validator._validate_dates(data)
        assert result.status == "FAIL"
    
    def test_missing_start_date(self):
        data = ExtractedData(
            policy_start_date=None,
            policy_end_date=date(2026, 1, 1)
        )
        result = validator._validate_dates(data)
        assert result.status == "FAIL"
    
    def test_missing_end_date(self):
        data = ExtractedData(
            policy_start_date=date(2025, 1, 1),
            policy_end_date=None
        )
        result = validator._validate_dates(data)
        assert result.status == "FAIL"


class TestInsuredValue:
    
    def test_positive_value(self):
        data = ExtractedData(insured_value=1000000)
        result = validator._validate_value(data)
        assert result.status == "PASS"
    
    def test_negative_value(self):
        data = ExtractedData(insured_value=-500)
        result = validator._validate_value(data)
        assert result.status == "FAIL"
    
    def test_zero_value(self):
        data = ExtractedData(insured_value=0)
        result = validator._validate_value(data)
        assert result.status == "FAIL"
    
    def test_missing_value(self):
        data = ExtractedData(insured_value=None)
        result = validator._validate_value(data)
        assert result.status == "FAIL"


class TestVesselName:
    
    def test_valid_vessel(self):
        data = ExtractedData(vessel_name="MV Neptune")
        result = validator._validate_vessel(data)
        assert result.status == "PASS"
    
    def test_invalid_vessel(self):
        data = ExtractedData(vessel_name="The Wanderer")
        result = validator._validate_vessel(data)
        assert result.status == "FAIL"
    
    def test_missing_vessel(self):
        data = ExtractedData(vessel_name=None)
        result = validator._validate_vessel(data)
        assert result.status == "FAIL"
    
    def test_empty_vessel(self):
        data = ExtractedData(vessel_name="   ")
        result = validator._validate_vessel(data)
        assert result.status == "FAIL"


class TestPolicyNumber:
    
    def test_valid_policy_number(self):
        data = ExtractedData(policy_number="HM-2025-10-A4B")
        result = validator._validate_policy_number(data)
        assert result.status == "PASS"
    
    def test_missing_policy_number(self):
        data = ExtractedData(policy_number=None)
        result = validator._validate_policy_number(data)
        assert result.status == "FAIL"
    
    def test_empty_policy_number(self):
        data = ExtractedData(policy_number="   ")
        result = validator._validate_policy_number(data)
        assert result.status == "FAIL"


class TestValidateDocumentData:
    
    def test_all_pass(self):
        data = ExtractedData(
            policy_number="HM-2025-10-A4B",
            vessel_name="MV Neptune",
            policy_start_date=date(2025, 11, 1),
            policy_end_date=date(2026, 10, 31),
            insured_value=5000000
        )
        results = validator.validate(data)
        assert len(results) == 4
        assert all(r.status == "PASS" for r in results)
    
    def test_all_fail(self):
        data = ExtractedData(
            policy_number=None,
            vessel_name="Invalid Vessel",
            policy_start_date=date(2026, 1, 1),
            policy_end_date=date(2025, 12, 31),
            insured_value=-500
        )
        results = validator.validate(data)
        assert len(results) == 4
        assert all(r.status == "FAIL" for r in results)
    
    def test_mixed_results(self):
        data = ExtractedData(
            policy_number="HM-2025-10-A4B",
            vessel_name="Invalid Vessel",
            policy_start_date=date(2025, 1, 1),
            policy_end_date=date(2026, 1, 1),
            insured_value=1000000
        )
        results = validator.validate(data)
        assert len(results) == 4
        passed = sum(1 for r in results if r.status == "PASS")
        assert passed == 3


class TestLoadValidVessels:
    
    def test_load_valid_vessels(self):
        vessels = validator.valid_vessels
        assert isinstance(vessels, list)
        assert len(vessels) > 0
        assert "MV Neptune" in vessels
