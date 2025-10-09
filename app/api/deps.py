from app.services.ai_extractor import AIExtractor
from app.services.validator import DocumentValidator


def get_ai_extractor() -> AIExtractor:
    return AIExtractor()


def get_document_validator() -> DocumentValidator:
    return DocumentValidator()
