import os
from sqlalchemy.ext.asyncio import AsyncSession
from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

from app.data_ingestion.graph.data_ingestion_graph import build_ingestion_graph


langfuse = get_client()

async def run_ingestion_graph(
    file_path: str,
    file_name: str,
    db: AsyncSession,
):  
    graph = await build_ingestion_graph()

    handler = CallbackHandler()

    with langfuse.start_as_current_observation(
        as_type="span",
        name="ingestion-pipeline",
        input={
            "file_name": file_name,
            "file_path": file_path,
        },
    ) as root_span:

        with propagate_attributes(
            user_id="user_123",          
            session_id="ingestion_session_abc",   
            metadata={"pipeline": "pdf-ingestion"},
        ):

            result = await graph.ainvoke(
                {
                    "file_path": file_path,
                    "file_name": file_name,
                },
                config={
                    "callbacks": [handler],
                },
            )

        root_span.update(output={
            "chunks_ingested": result.get("chunks_ingested"),
            "source": result.get("file_name"),
        })

    if os.path.exists(file_path):
        os.remove(file_path)

    return {
        "status": "success",
        "chunks_ingested": result["chunks_ingested"],
        "source": result["file_name"],
    }
