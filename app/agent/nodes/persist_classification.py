from sqlalchemy import select
from app.agent.state import EmailAgentState
from app.models.email_models import Email
from app.core.database import async_session_maker

from langfuse import observe

@observe()
async def persist_classification(
    state:EmailAgentState
):
    try:
        async with async_session_maker() as db:
            if not state['classification']:
                return {}
            result=await db.execute(select(Email).where(Email.email_id==state['email_id']))

            email=result.scalar_one_or_none()

            if not email:
                return {}
            
            classification=state['classification']
            email.intent=classification['intent']
            email.urgency=classification['urgency']
            email.topic=classification['topic']
            email.summary=classification['summary']
            email.status="classified"

            await db.commit()
    except Exception as e:
        print("error",e)
    
    return {}