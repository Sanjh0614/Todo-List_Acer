import json
from app.ai.prompts.prompt_loader import load_prompt
from app.services.hybrid_client import HybridClient
from app.services.parser import Parser
from app.schemas.ai import ChatOutput
from app.ai.graph.state import AIState

class ChatAgent:
    def __init__(self):
        self.llm = HybridClient()
        self.system_prompt = load_prompt("chat")

    def execute(self, state: AIState) -> dict:
        input_data = state.get("input", {})
        last_message = input_data.get("message", "")
        
        # Build prompt from template
        prompt = self.system_prompt.replace("{last_user_message}", str(last_message))
        
        # For chat we might not strictly enforce JSON from LLM directly if it's open text,
        # but the PDF API Contract says Chat returns {"reply": "..."}
        # Let's enforce JSON for consistency with the schema.
        response_text = self.llm.generate_json(prompt, ChatOutput.model_json_schema())
        
        parsed_output = Parser.parse_json(response_text, ChatOutput)
        return parsed_output.model_dump()
