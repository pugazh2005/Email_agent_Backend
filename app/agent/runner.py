from sqlalchemy.ext.asyncio import AsyncSession
from app.agent.graph import graph_holder
from app.agent.state import EmailAgentState
from app.models.email_models import Email
from sqlalchemy import select

from langfuse import get_client, propagate_attributes


async def run_email_agent(email: Email, db: AsyncSession):
    thread_id = email.email_id
    
    initial_state = EmailAgentState(
        email_id=email.email_id,
        email_content=email.body,
        sender_email=email.sender_email,
        customer_name=email.customer_name,
        subject=email.subject,
        classification=None,
        search_query=None,
        retrieved_docs=None,
        bug_id=None,
        draft_response=None,
        final_response=None,
        has_retrieval=None,
        needs_human_review=False,
        send_reply_message=None,
    )
    
    try:
       
        output = await graph_holder.email_graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": thread_id}}
        )
        
        if output.get("needs_human_review"):
            email.status = "needs_approval"
            await db.commit()
            return {
                "status": "needs_review",
                "email_id": email.email_id,
                "thread_id": thread_id,
                "needs_human_review": True,
                "message": "Email requires human review"
            }
        else:
            email.status = "completed"
            await db.commit()
            return {
                "status": "completed",
                "email_id": email.email_id,
                "thread_id": thread_id,
                "needs_human_review": False,
                "message": "Email processed successfully"
            }
            
    except Exception as e:
        if "Interrupt" in str(type(e).__name__):
            email.status = "needs_approval"
            await db.commit()
            
            return {
                "status": "interrupted",
                "email_id": email.email_id,
                "thread_id": thread_id,
                "needs_human_review": True,
                "message": "Human review required (interrupted)",
                "interrupt_details": str(e)
            }
        email.status = "error"
        await db.commit()
        raise e