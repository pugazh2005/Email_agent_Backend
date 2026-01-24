from app.agent.state import EmailAgentState
from langfuse import observe

@observe()
async def route_bug_or_write(state: EmailAgentState) -> str:
    intent = (state.get("classification") or {}).get("intent")
    if intent == "bug":
        return "track_bug"
    return "response"