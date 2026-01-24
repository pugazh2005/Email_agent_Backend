from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.data_ingestion.state import IngestionState


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.data_ingestion.state import IngestionState
from app.models.system_state_for_kb import SystemState
from app.core.database import async_session_maker

async def update_system_state(
    state: IngestionState
) -> IngestionState:
    async with async_session_maker() as db:
        result = await db.execute(
            select(SystemState).where(SystemState.key == "kb_ready")
        )

        system_state = result.scalar_one_or_none()

        if system_state:
            system_state.value = "true"
        else:
            db.add(
                SystemState(
                    key="kb_ready",
                    value="true",
                )
            )

        await db.commit()
    return state
