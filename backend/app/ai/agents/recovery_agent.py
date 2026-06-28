import json
from app.ai.prompts.prompt_loader import load_prompt
from app.services.hybrid_client import HybridClient
from app.services.parser import Parser
from app.schemas.ai import RecoveryPlanOutput
from app.ai.graph.state import AIState

class RecoveryAgent:
    def __init__(self):
        self.llm = HybridClient()
        self.system_prompt = load_prompt("recovery")

    def execute(self, state: AIState) -> dict:
        context = state.get("context", {})
        input_data = state.get("input", {})
        
        tasks_str = json.dumps(context.get("tasks", []))
        events_str = json.dumps(context.get("calendar_events", []))
        days_left = input_data.get("days_left", 0)
        
        # Build prompt from template
        prompt = self.system_prompt.replace("{tasks}", tasks_str)\
                                   .replace("{events}", events_str)\
                                   .replace("{days_left}", str(days_left))
        
        # Call LLM
        response_text = self.llm.generate_json(prompt, RecoveryPlanOutput.model_json_schema())
        
        # Parse output
        parsed_output = Parser.parse_json(response_text, RecoveryPlanOutput)
        return parsed_output.model_dump()
