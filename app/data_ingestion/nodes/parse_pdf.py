from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.data_ingestion.state import IngestionState


async def parse_pdf(state: IngestionState) -> IngestionState:
    loader = PyMuPDFLoader(state["file_path"])
    documents=loader.load()
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks=splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata["source"]=state["file_name"]
    
    return {
        "chunks": [c.page_content for c in chunks],
    }
