import uuid

from sqlalchemy import select
from app.agent.state import EmailAgentState
from app.core.database import async_session_maker
from app.models.email_models import Email
from app.models.bugs_model import Bug

from langfuse import observe

@observe()
async def bug_tracking(state: EmailAgentState) -> EmailAgentState:
    classification = state.get("classification")

    if not classification or classification.get("intent") != "bug":
        return {}

    async with async_session_maker() as db:
        try:
            
            result = await db.execute(
                select(Email).where(Email.email_id == state["email_id"])
            )
            email = result.scalar_one_or_none()

            if not email:
                return {}

            result = await db.execute(
                select(Bug).where(Bug.email_id == email.email_id)
            )
            existing_bug = result.scalar_one_or_none()

            if existing_bug:
                return {"bug_id": existing_bug.bug_id}

        
            bug_id = f"BUG-{uuid.uuid4()}"

            bug = Bug(
                bug_id=bug_id,
                email_id=email.email_id,
                description=state.get("email_content", ""),
                status="open"
            )

            db.add(bug)
            email.status = "bug_created"
            email.ticket_id = bug_id  
            await db.commit()

            return {
                "bug_id": bug_id
            }

        except Exception:
            db.rollback()
            raise

        finally:
            await db.close()
