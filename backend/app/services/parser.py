from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
import logging

T = TypeVar('T', bound=BaseModel)

class Parser:
    @staticmethod
    def parse_json(json_str: str, schema: Type[T]) -> T:
        """Parses a JSON string into a Pydantic model. Raises ValidationError if it fails."""
        cleaned = json_str.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return schema.model_validate_json(cleaned)
        except ValidationError as e:
            logging.error(f"Failed to parse LLM output against {schema.__name__}: {e}\nRaw output: {json_str}")
            raise
