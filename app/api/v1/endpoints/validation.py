from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError

from app.models.schemas import DocumentRequest, ValidationResponse, ExtractedData
from app.services.ai_extractor import AIExtractor
from app.services.validator import DocumentValidator
from app.api.deps import get_ai_extractor, get_document_validator
from app.utils.exceptions import AIExtractorError
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/validate", response_model=ValidationResponse)
async def validate_document(
    request: DocumentRequest,
    ai_extractor: AIExtractor = Depends(get_ai_extractor),
    validator: DocumentValidator = Depends(get_document_validator)
):
    logger.info("Processing validation request")
    
    try:
        raw_data = await ai_extractor.extract(request.document_text)
    except AIExtractorError as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"AI service failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    try:
        extracted_data = ExtractedData(**raw_data)
    except ValidationError as e:
        logger.error(f"Invalid data schema: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

    try:
        validation_results = validator.validate(extracted_data)
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")

    response = ValidationResponse(
        extracted_data=extracted_data,
        validation_results=validation_results
    )
    
    passed = sum(1 for r in validation_results if r.status == "PASS")
    logger.info(f"Validation complete: {passed}/{len(validation_results)} passed")
    
    return response
