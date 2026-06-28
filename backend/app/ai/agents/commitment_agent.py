import json
from app.ai.prompts.prompt_loader import load_prompt
from app.services.hybrid_client import HybridClient
from app.services.parser import Parser
from app.schemas.ai import CommitmentOutput
from app.ai.graph.state import AIState

class CommitmentAgent:
    def __init__(self):
        self.llm = HybridClient()
        self.system_prompt = load_prompt("commitment")

    def execute(self, state: AIState) -> dict:
        input_text = state.get("input", "")
        # Build prompt from template
        prompt = self.system_prompt.replace("{message}", str(input_text))
        
        # Call LLM
        response_text = self.llm.generate_json(prompt, CommitmentOutput.model_json_schema())
        
        # Parse output
        parsed_output = Parser.parse_json(response_text, CommitmentOutput)
        return parsed_output.model_dump()
