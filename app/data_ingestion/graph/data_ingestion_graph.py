from langgraph.graph import StateGraph,START,END
from app.data_ingestion.nodes.parse_pdf import parse_pdf
from app.data_ingestion.nodes.embed_and_store import embed_and_store
from app.data_ingestion.state import IngestionState
from app.data_ingestion.nodes.update_state import update_system_state

async def build_ingestion_graph():
    builder=StateGraph(IngestionState)
    builder.add_node("parse_pdf",parse_pdf)
    builder.add_node("embed_and_store",embed_and_store)
    builder.add_node("update_state",update_system_state)

    builder.add_edge(START,"parse_pdf")
    builder.add_edge("parse_pdf","embed_and_store")
    builder.add_edge("embed_and_store","update_state")
    builder.add_edge("update_state",END)

    return builder.compile()
    