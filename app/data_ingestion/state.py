from typing import TypedDict


class IngestionState(TypedDict):
    file_path: str
    file_name: str
    file_type: str
    chunks: list[str]
    chunks_ingested:int
    embeddings: list[list[float]]
    source: str
