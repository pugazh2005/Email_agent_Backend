from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.knowledge_ingestion import know_router
from app.api.agent_endpoints import agent_router
from app.api.emails_ingestion import email_router
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.agent.graph.agent_graph import build_email_graph
from app.agent.graph import graph_holder

import os
CHECKPOINTER_URL=os.getenv("CHECKPOINTER_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):

    async with AsyncPostgresSaver.from_conn_string(
        CHECKPOINTER_URL
    ) as checkpointer:
        await checkpointer.setup()
        graph_holder.email_graph=build_email_graph(checkpointer)
        yield 

app=FastAPI(title="Agentic_email_support_system",lifespan=lifespan)
app.include_router(know_router)
app.include_router(email_router)
app.include_router(agent_router)