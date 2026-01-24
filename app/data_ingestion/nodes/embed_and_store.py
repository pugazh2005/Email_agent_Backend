import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.data_ingestion.state import IngestionState
from app.data_ingestion.utils.embed_text import embed_text
from app.models.knowledge_models import Knowledge_Base
from app.core.database import async_session_maker
async def embed_and_store(state:IngestionState):
    chunks=state['chunks']
    async with async_session_maker() as db:
        for chunk in chunks:
            db.add(
                    Knowledge_Base(
                        id=str(uuid.uuid4()),
                        content=chunk,
                        embedding=embed_text(chunk),
                        source=state['file_name']
                    )
                )
        await db.commit()
    return {"chunks_ingested":len(chunks)}