from app.agent.state import EmailAgentState
from langgraph.graph import START,END
from typing import Literal
from langgraph.types import Command,interrupt

from langfuse import observe

@observe()
async def human_review(state: EmailAgentState) -> Command[Literal["send_reply", END]]:
    decision = interrupt({
        "email_id": state["email_id"],
        "email": state["email_content"],
        "draft": state["draft_response"],
        "classification": state.get("classification"),
        "message": """Give your decision as a json,
        decision: 'approve' or 'reject' or 'edit',
        if you choose decision as edit give the edited response as follows in json
        edited_response:"your edited response"
        """
    })

    if decision.get("decision").strip().lower() in ["approve", "approved"]:
        return Command(update={"final_response":state["draft_response"]}
                       ,goto="send_reply")
    elif decision.get("decision").strip().lower() in ["edit"]:
        return Command(update={"final_response":decision.get("edited_response")},goto="send_reply")
    return Command(goto=END)