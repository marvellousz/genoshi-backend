import json
from typing import List
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import ExtractedData, ValidationResult

logger = get_logger(__name__)


class DocumentValidator:
    def __init__(self):
        self.valid_vessels = self._load_valid_vessels()
    
    def validate(self, extracted_data: ExtractedData) -> List[ValidationResult]:
        results = []
        results.append(self._validate_dates(extracted_data))
        results.append(self._validate_value(extracted_data))
        results.append(self._validate_vessel(extracted_data))
        results.append(self._validate_policy_number(extracted_data))
        return results
    
    def _validate_dates(self, data: ExtractedData) -> ValidationResult:
        if data.policy_start_date is None or data.policy_end_date is None:
            return ValidationResult(
                rule="Date Consistency",
                status="FAIL",
                message="Policy dates are missing or invalid."
            )
        
        if data.policy_end_date > data.policy_start_date:
            return ValidationResult(
                rule="Date Consistency",
                status="PASS",
                message="Policy end date is after start date."
            )
        
        return ValidationResult(
            rule="Date Consistency",
            status="FAIL",
            message="Policy end date cannot be before the start date."
        )
    
    def _validate_value(self, data: ExtractedData) -> ValidationResult:
        if data.insured_value is None:
            return ValidationResult(
                rule="Value Check",
                status="FAIL",
                message="Insured value is missing."
            )
        
        if data.insured_value > 0:
            return ValidationResult(
                rule="Value Check",
                status="PASS",
                message="Insured value is valid."
            )
        
        return ValidationResult(
            rule="Value Check",
            status="FAIL",
            message="Insured value must be a positive number."
        )
    
    def _validate_vessel(self, data: ExtractedData) -> ValidationResult:
        if not data.vessel_name or data.vessel_name.strip() == "":
            return ValidationResult(
                rule="Vessel Name Match",
                status="FAIL",
                message="Vessel name is missing."
            )
        
        if data.vessel_name in self.valid_vessels:
            return ValidationResult(
                rule="Vessel Name Match",
                status="PASS",
                message=f"Vessel '{data.vessel_name}' is on the approved list."
            )
        
        return ValidationResult(
            rule="Vessel Name Match",
            status="FAIL",
            message=f"Vessel '{data.vessel_name}' is not on the approved list."
        )
    
    def _validate_policy_number(self, data: ExtractedData) -> ValidationResult:
        if not data.policy_number or data.policy_number.strip() == "":
            return ValidationResult(
                rule="Completeness Check",
                status="FAIL",
                message="Policy number is missing."
            )
        
        return ValidationResult(
            rule="Completeness Check",
            status="PASS",
            message="Policy number is present."
        )
    
    def _load_valid_vessels(self) -> List[str]:
        try:
            with open(settings.valid_vessels_file, 'r') as f:
                vessels = json.load(f)
                logger.info(f"Loaded {len(vessels)} valid vessels")
                return vessels
        except FileNotFoundError:
            logger.error(f"Vessels file not found: {settings.valid_vessels_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid vessels JSON: {e}")
            return []
