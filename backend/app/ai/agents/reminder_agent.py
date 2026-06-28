import json
from app.ai.prompts.prompt_loader import load_prompt
from app.services.hybrid_client import HybridClient
from app.services.parser import Parser
from app.schemas.ai import ReminderOutput
from app.ai.graph.state import AIState

class ReminderAgent:
    def __init__(self):
        self.llm = HybridClient()
        self.system_prompt = load_prompt("reminder")

    def execute(self, state: AIState) -> dict:
        memory = state.get("memory", {})
        input_data = state.get("input", {})
        
        task_title = input_data.get("task_title", "Task")
        days_left = input_data.get("days_left", 0)
        history_str = json.dumps(memory.get("postponement_reasons", []))
        
        # Build prompt from template
        prompt = self.system_prompt.replace("{history}", history_str)\
                                   .replace("{task}", str(task_title))\
                                   .replace("{days_left}", str(days_left))
        
        # Call LLM
        response_text = self.llm.generate_json(prompt, ReminderOutput.model_json_schema())
        
        # Parse output
        parsed_output = Parser.parse_json(response_text, ReminderOutput)
        return parsed_output.model_dump()
