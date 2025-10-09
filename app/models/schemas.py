from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class DocumentRequest(BaseModel):
    document_text: str = Field(..., description="Raw insurance document text")


class ExtractedData(BaseModel):
    policy_number: Optional[str] = None
    vessel_name: Optional[str] = None
    policy_start_date: Optional[date] = None
    policy_end_date: Optional[date] = None
    insured_value: Optional[int] = None


class ValidationResult(BaseModel):
    rule: str
    status: str
    message: str


class ValidationResponse(BaseModel):
    extracted_data: ExtractedData
    validation_results: List[ValidationResult]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
