from app.agent.state import EmailAgentState
from langfuse import observe

@observe()
async def read_email(state:EmailAgentState)->EmailAgentState:
    if "email_content" not in state:
        raise ValueError("email_content missing from state")
    return state