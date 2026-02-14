from sqlalchemy import bindparam, select,func
from app.agent.state import EmailAgentState
from app.core.database import async_session_maker
from app.data_ingestion.utils.embed_text import embed_text
from app.models.knowledge_models import Knowledge_Base
from app.models.response_experience import ResponseExperience
from app.models.system_state_for_kb import SystemState

from langfuse import observe

@observe()
async def retrieve_docs(state:EmailAgentState):
    intent = state.get("classification", {}).get("intent")
    if intent in {"system", "personal", "other"}:
        return {}
    try:
        async with async_session_maker() as db:
            query_embedding = embed_text(state["email_content"])
            result = await db.execute(
                select(SystemState.value).where(SystemState.key == "kb_ready")
            )
            kb_ready=result.scalar_one_or_none()

            if kb_ready != "true":
                return {}
            stmt = (
                    select(
                        Knowledge_Base.content,
                        Knowledge_Base.source,
                        Knowledge_Base.embedding    
                    )
                    .order_by(Knowledge_Base.embedding.cosine_distance(query_embedding))
                    .limit(3)
                    )
            result = await db.execute(stmt, {"q": query_embedding})
            kb_rows = result.scalars().all()
            stmt = (
                    select(
                        ResponseExperience.response_text,
                        ResponseExperience.email_embedding
                    )
                    .where(ResponseExperience.outcome == "success")
                    .order_by(ResponseExperience.email_embedding.cosine_distance(query_embedding))
                    .limit(3)
                )

            result = await db.execute(stmt, {"q": query_embedding})
            exp_rows = result.scalars().all()
            
            retrieved_docs = []
            
            for row in kb_rows:
                retrieved_docs.append({
                    "source": "knowledge_base",
                    "content": row,
                })
            for row in exp_rows:
                retrieved_docs.append({
                    "source": "past_experience",
                    "content": row
                })
            return {"retrieved_docs": retrieved_docs}
    except Exception as e:
        print("error",e)
    finally:
        await db.close()