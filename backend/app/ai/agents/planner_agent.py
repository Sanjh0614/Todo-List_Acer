import json
from app.ai.prompts.prompt_loader import load_prompt
from app.services.hybrid_client import HybridClient
from app.services.parser import Parser
from app.schemas.ai import TaskPlanOutput
from app.ai.graph.state import AIState

class PlannerAgent:
    def __init__(self):
        self.llm = HybridClient()
        self.system_prompt = load_prompt("planner")

    def execute(self, state: AIState) -> dict:
        context = state.get("context", {})
        active_commit = context.get("active_commitment") or {}
        
        title = active_commit.get("title", "")
        due_date = active_commit.get("due_date", "")
        
        # Build prompt from template
        prompt = self.system_prompt.replace("{title}", str(title)).replace("{due_date}", str(due_date))
        
        # Call LLM
        response_text = self.llm.generate_json(prompt, TaskPlanOutput.model_json_schema())
        
        # Parse output
        parsed_output = Parser.parse_json(response_text, TaskPlanOutput)
        return parsed_output.model_dump()
