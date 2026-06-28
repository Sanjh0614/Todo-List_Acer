import json
import logging
import requests
from typing import Optional, Any
from app.services.llm_client import LLMClient
from app.config import settings

class NvidiaClient(LLMClient):
    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_BASE_URL
        self.model = settings.NVIDIA_MODEL
        if not self.api_key:
            logging.warning("NVIDIA_API_KEY is not set in the environment.")

    def _invoke(self, prompt: str, system_instr: Optional[str] = None, temperature: float = 1.0) -> str:
        if not self.api_key:
            raise ValueError("NVIDIA API key not configured")
            
        invoke_url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        messages = []
        if system_instr:
            messages.append({"role": "system", "content": system_instr})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 16384,
            "temperature": temperature,
            "top_p": 0.95,
            "stream": False
        }
        
        response = requests.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def generate(self, prompt: str, system_instr: Optional[str] = None, temperature: float = 1.0) -> str:
        try:
            return self._invoke(prompt, system_instr, temperature)
        except Exception as e:
            logging.error(f"NVIDIA generation failed: {e}")
            raise

    def generate_json(self, prompt: str, response_schema: Any, system_instr: Optional[str] = None, temperature: float = 1.0) -> str:
        # Enforce JSON output for NVIDIA by appending instructions to the system prompt
        json_instruction = f"\n\nYou must respond ONLY with a valid JSON object adhering to this schema:\n{json.dumps(response_schema)}\nDo not include any markdown formatting like ```json or any other text outside the JSON object."
        
        if system_instr:
            system_instr += json_instruction
        else:
            system_instr = json_instruction
            
        try:
            content = self._invoke(prompt, system_instr, temperature)
            # Cleanup common markdown code block wrappings if the model ignores the instruction
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return content.strip()
        except Exception as e:
            logging.error(f"NVIDIA JSON generation failed: {e}")
            raise
