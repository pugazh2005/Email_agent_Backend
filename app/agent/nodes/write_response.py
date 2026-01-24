from typing import Literal

from sqlalchemy import select
from app.agent.state import EmailAgentState
from app.utils.chat_llm import llm
from langgraph.types import Command
from langgraph.graph import END
from app.models.email_models import Email
from app.core.database import async_session_maker
from app.utils.prompts import build_write_response_prompt

from langfuse import observe

@observe()
async def write_response(state:EmailAgentState) -> Command[Literal["human_review","send_reply",END]]:
    classification = state["classification"]
    intent = classification["intent"]
    state["customer_name"]=state["sender_email"].split("@")[0]
    has_retrieval = bool(state.get("retrieved_docs") and len(state.get("retrieved_docs", [])) > 0)
    
  
    if intent in ["system", "other"]:
        print(f"Skipping draft for {intent} email - no response needed")
        return Command(
            update={
                "draft_response": None,
                "needs_human_review": False,
                "has_retrieval": has_retrieval,
                "send_email_reply":"Email is classified as system or other, so stopping reply"
            },
            goto=END
        )
    
 
    docs = "\n".join(
        f"- {d['content']}" for d in state.get("retrieved_docs", [])
    )
    write_response_prompt=build_write_response_prompt(state["email_content"],state.get("customer_name","Customer"),classification["intent"],classification["urgency"],docs)
    response=await llm.ainvoke(write_response_prompt)
    
    draft_text = response.content
    
   
    needs_review = (
        state["classification"]["urgency"] in ["high", "critical"]
        or state["classification"]["intent"] in ["complex", "personal"]
    )
    
    async with async_session_maker() as db:
        try:
            
            result = await db.execute(
                select(Email).where(Email.email_id == state["email_id"])
                        )
            email = result.scalar_one_or_none()
            if email:
                email.draft_response = draft_text
                await db.commit()
                print(f"Updated draft_response in database for email {state['email_id']}")
        except Exception as e:
            print(f"Error updating draft_response: {e}")
            await db.rollback()
        finally:
            await db.close()
        
        print(f"Draft created. Needs review: {needs_review}")
        print(f"Draft: {draft_text}")
        
        return Command(
            update={
                "draft_response": draft_text,
                "needs_human_review": needs_review,
                "has_retrieval": has_retrieval
            },
            goto="human_review" if needs_review else "send_reply" 
        )
