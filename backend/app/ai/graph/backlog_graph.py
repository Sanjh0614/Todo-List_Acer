from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from app.config import settings

class BacklogState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    task_id: int
    recommendation: str

@tool
def get_task_context(task_id: int) -> str:
    """Fetch the full context of a backlog task by its ID. ALWAYS use this first!"""
    from app.database import SessionLocal
    from app.models.task import Task
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return "Task not found."
        return f"Title: {task.title}\nDescription: {task.description or 'No description'}\nPriority: {task.priority}\nPlanned Date: {task.planned_date}"
    finally:
        db.close()

@tool
def submit_recommendation(recommendation: str) -> str:
    """Submit the detailed, highly motivating recommendation back to the system. ALWAYS use this to submit the final output."""
    return "Recommendation submitted successfully."

tools = [get_task_context, submit_recommendation]

def llm_node(state: BacklogState):
    llm = ChatNVIDIA(
        api_key=settings.NVIDIA_API_KEY,
        base_url=settings.NVIDIA_BASE_URL,
        model=settings.NVIDIA_MODEL,
        temperature=0.7
    ).bind_tools(tools)
    
    res = llm.invoke(state["messages"])
    return {"messages": [res]}

def tool_node(state: BacklogState):
    last_msg = state["messages"][-1]
    msgs = []
    rec = state.get("recommendation", "")
    for tc in last_msg.tool_calls:
        if tc["name"] == "get_task_context":
            res = get_task_context.invoke(tc["args"])
            msgs.append(ToolMessage(content=str(res), tool_call_id=tc["id"]))
        elif tc["name"] == "submit_recommendation":
            rec = tc["args"]["recommendation"]
            msgs.append(ToolMessage(content="Success", tool_call_id=tc["id"]))
            
    return {"messages": msgs, "recommendation": rec}

def router(state: BacklogState):
    last_msg = state["messages"][-1]
    if getattr(last_msg, "tool_calls", None):
        return "tools"
    return END

workflow = StateGraph(BacklogState)
workflow.add_node("llm", llm_node)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "llm")
workflow.add_conditional_edges("llm", router)
workflow.add_edge("tools", "llm")

backlog_app = workflow.compile()

async def generate_backlog_recommendation_graph(task_id: int) -> str:
    msg = HumanMessage(content=f"Please analyze the backlog task with ID {task_id}, get its context using your tool, and then submit a detailed recommendation on how to complete it using the submit_recommendation tool.")
    try:
        result = await backlog_app.ainvoke({"messages": [msg], "task_id": task_id, "recommendation": ""})
        return result.get("recommendation", "No recommendation provided.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "Failed to generate recommendation. Break it down into small steps and just start!"
