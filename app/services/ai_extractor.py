import json
from typing import Dict, Any
from groq import Groq

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.exceptions import AIExtractorError

logger = get_logger(__name__)


class AIExtractor:
    def __init__(self):
        if not settings.groq_api_key:
            raise AIExtractorError("GROQ_API_KEY not configured")
        
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.ai_model
        self.temperature = settings.ai_temperature
        self.max_tokens = settings.ai_max_tokens
    
    async def extract(self, document_text: str) -> Dict[str, Any]:
        try:
            prompt = self._build_prompt(document_text)
            
            logger.info("Extracting data from document")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Extract structured data from documents. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            extracted_data = self._parse_response(response_text)
            
            logger.info(f"Extracted: {extracted_data}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            if isinstance(e, AIExtractorError):
                raise
            raise AIExtractorError(f"AI service error: {str(e)}")
    
    def _build_prompt(self, document_text: str) -> str:
        return f"""Extract these fields from the insurance document as JSON:
- policy_number (string or null)
- vessel_name (string or null)  
- policy_start_date (YYYY-MM-DD or null)
- policy_end_date (YYYY-MM-DD or null)
- insured_value (integer or null)

Rules:
- Dates must be in YYYY-MM-DD format
- Remove currency symbols from insured_value
- Preserve negative values
- Return only JSON, no markdown or explanations

Document:
---
{document_text}
---

JSON format:
{{"policy_number": null, "vessel_name": null, "policy_start_date": null, "policy_end_date": null, "insured_value": null}}
"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        try:
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {response_text}")
            raise AIExtractorError(f"Invalid JSON response: {str(e)}")
        
        required_fields = ["policy_number", "vessel_name", "policy_start_date", "policy_end_date", "insured_value"]
        for field in required_fields:
            if field not in extracted_data:
                extracted_data[field] = None
        
        return extracted_data
