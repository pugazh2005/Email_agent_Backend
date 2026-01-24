from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.agent.runner import run_email_agent
from app.core.database import async_session_maker, get_db
from app.data_ingestion.utils.embed_text import embed_text
from app.models.email_models import Email
from app.agent.graph import graph_holder
from app.models.response_experience import ResponseExperience
from app.schemas.email_schemas import ResumeAction, EmailOut
from app.agent.state import EmailAgentState
from langgraph.types import Command
from typing import Optional
from app.crud.email_crud import fetch_all_received_emails, fetch_email_by_id, fetch_email_for_run

agent_router = APIRouter(prefix="/agent", tags=["Agent"])


@agent_router.get("/emails/needs-approval")
async def get_needs_approval_emails(
    db: AsyncSession = Depends(get_db)
):
    
        result = await db.execute(
            select(Email).where(Email.status == "needs_approval")
        )
        emails = result.scalars().all()
        data = [
        {
            "email_id": email.email_id,
            "sender_email": email.sender_email,
            "intent": email.intent,
            "urgency": email.urgency,
            "status": email.status,
            "email_content":email.draft_response    
        }
        for email in emails
    ]
        return data
    


@agent_router.post("/run")
async def run_single_email(
    email_id: str = Query(..., description="Email ID to process"),
    db: AsyncSession = Depends(get_db),
) :
    email = await fetch_email_for_run(db,email_id)
    if not email:
        raise HTTPException(
            status_code=404,
            detail="Email not found or not in 'received' status"
        )

    result = await run_email_agent(email, db)
    return result
    


@agent_router.post("/run-all")
async def run_all_emails(
    db: AsyncSession = Depends(get_db),
) :
    emails = await fetch_all_received_emails(db)
    
    if not emails:
        return {
            "status": "success",
            "message": "No emails in 'received' state",
            "processed_count": 0,
            "needs_approval_count": 0,
            "completed_count": 0
        }
    
    results = []
    needs_approval_count = 0
    completed_count = 0
    error_count = 0
    
    for email in emails:
        try:
            result = await run_email_agent(email, db)
            results.append(result)

            if result["status"] in ["needs_review", "interrupted"]:
                needs_approval_count += 1
            elif result["status"] == "completed":
                completed_count += 1
            
        except Exception as e:
            error_count += 1
            results.append({
                "status": "error",
                "email_id": email.email_id,
                "thread_id": email.email_id,
                "message": f"Error processing email: {str(e)}",
                "error": str(e)
            })
    
    await db.commit()
    
    return {
        "status": "success",
        "message": f"Processed {len(emails)} emails",
        "total_emails": len(emails),
        "processed": len(results),
        "needs_approval": needs_approval_count,
        "completed": completed_count,
        "errors": error_count,
        "results": results
    }


@agent_router.post("/resume/{email_id}")
async def resume_interrupted_email(
    email_id: str,
    resume_action: ResumeAction,
    thread_id: str = Query(..., description="Thread ID from interrupted run"),
    db: AsyncSession = Depends(get_db),
):
    
    email = await fetch_email_by_id(db,email_id)
    
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    decision = resume_action.decision.strip().lower()
    
    if decision not in ["yes", "y", "approve", "approved", "no", "n", "reject", "rejected","edit","edit_response"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid decision. Must be: approve/approved/yes/y or reject/rejected/no/n"
        )
    
    if decision in ["yes", "y", "approve", "approved"]:
        action = "approve"
    elif decision in ["edit","edit_response"]:
        action="edit"
    else:
        action = "reject"
    
    resume_command = {
        "decision": action,
        "edited_response": resume_action.edited_response
    }
    
    try:
        
        output = await graph_holder.email_graph.ainvoke(
            Command(resume=resume_command),
            config={"configurable": {"thread_id": thread_id}}
        )
        
        
        if action == "approve" or action=="edit":
            email.status = "completed"
            email.final_response = output.get("final_response")
        else:  
            email.status = "rejected"
            db.add(
            ResponseExperience(
                email_intent=email.intent,
                urgency=email.urgency,
                topic=email.topic,
                email_embedding=embed_text(email.body),
                response_text=output.get(""),
                outcome="failed" ,
                feedback=None,
            )
        )
        
        await db.commit()
        
        return {
            "status": "success",
            "email_id": email_id,
            "action": action,
            "message": f"Email {action}ed successfully",
            "final_status": email.status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resuming graph execution: {str(e)}"
        )
            
    