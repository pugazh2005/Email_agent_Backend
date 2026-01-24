from app.utils.chat_llm import embedder

def embed_text(text: str) -> list[float]:
    return embedder.embed_query(text)
