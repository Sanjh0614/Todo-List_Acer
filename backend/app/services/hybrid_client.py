import logging
from typing import Optional, Any
from app.services.llm_client import LLMClient
from app.services.nvidia_client import NvidiaClient
from app.services.gemini_client import GeminiClient

class HybridClient(LLMClient):
    def __init__(self):
        self.primary = NvidiaClient()
        self.fallback = GeminiClient()

    def generate(self, prompt: str, system_instr: Optional[str] = None, temperature: float = 1.0) -> str:
        try:
            return self.primary.generate(prompt, system_instr, temperature)
        except Exception as e:
            logging.warning(f"Primary NVIDIA client failed: {e}. Falling back to Gemini.")
            return self.fallback.generate(prompt, system_instr, temperature)

    def generate_json(self, prompt: str, response_schema: Any, system_instr: Optional[str] = None, temperature: float = 1.0) -> str:
        try:
            return self.primary.generate_json(prompt, response_schema, system_instr, temperature)
        except Exception as e:
            logging.warning(f"Primary NVIDIA JSON generation failed: {e}. Falling back to Gemini.")
            return self.fallback.generate_json(prompt, response_schema, system_instr, temperature)
